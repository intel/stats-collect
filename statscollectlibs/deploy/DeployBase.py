# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the base class for software deployment sub-classes.

Terminology:
    * category - type of an installable. Currently, there are 3 categories: drivers, simple helpers
                 shelpers) and python helpers (pyhelpers).
    * installable - a sub-project to install on the SUT (System Under Test). An installable may
                    include one or more deployable. For example, a driver installable may include
                    multiple drivers. A python helper installable may include multiple python helper
                    scripts.
    * deployable - each installable provides one or multiple deployables of the same category as the
                   installable.
    * helper - somewhat poorly defined term. In the context of this module, a helper may refer to a
               non-driver installable. For example, a python helper installable. But also a helper
               may refer to a single non-driver deployable. For example, a python helper script.

Installable vs Deployable:
    * Installables come in the form of source code. Deployables are individual executable programs
      (script, binary) or kernel drivers.
    * An installable corresponds to a directory with source code and/or scripts. The source code may
      need to be compiled. The compilation results in one or several deployables. The scripts in the
      installable directory may be deployables.
    * Deployables are ultimately copied to the SUT and executed on the SUT.

Helper deployable types:
    1. Simple helpers (shelpers) are stand-alone independent programs, which come in the form of a
       single executable file.
    2. Python helpers (pyhelpers) are helper programs written in Python. Unlike simple helpers,
       they are not totally independent but depend on various Python modules. Deploying a Python
       helper is trickier because all Python modules should also be deployed.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import os
import time
import copy
import typing
from typing import TypedDict, Literal, cast, Iterator
from pathlib import Path
from pepclibs.helperlibs import Logging, ClassHelpers, ProcessManager, LocalProcessManager
from pepclibs.helperlibs import ProjectFiles
from pepclibs.helperlibs.Exceptions import ErrorExists, ErrorNotFound

if typing.TYPE_CHECKING:
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType

    # The supported installable categories.
    InstallableCategoriesType = Literal["drivers", "shelpers", "pyhelpers"]

    class InstallableInfoTypedDict(TypedDict, total=False):
        """
        The type of the dictionary that describes an installable.

        Attributes:
            name: The name of the installable.
            category: Category name of the installable ("drivers", "shelpers", etc).
            category_descr: The description of the installable category.
            minkver: Minimum SUT kernel version required for the installable.
            deployables: List of deployables this installable provides.
        """

        name: str
        category: InstallableCategoriesType
        category_descr: str
        minkver: str
        deployables: tuple[str, ...]

    # The tool deploy information type.
    class DeployInfoTypedDict(TypedDict):
        """
        The deployment description dictionary type.

        Attributes:
            installables: Dictionary of installables. The key is the installable name, and the value
                          is the installable information dictionary.
        """
        installables: dict[str, InstallableInfoTypedDict]

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

# The supported installable categories.
CATEGORIES: dict[InstallableCategoriesType, str] = {"drivers"    : "kernel driver",
                                                    "shelpers"   : "simple helper program",
                                                    "pyhelpers"  : "python helper program"}

def _get_deploy_cmd(pman: ProcessManagerType, toolname: str) -> str:
    """""
    Generate the deployment command for a given tool.

    Args:
        pman: The process manager object representing the host where the tool will be deployed.
        toolname: The name of the tool for which the deployment command is generated.

    Returns:
        str: The command that should be run to deploy the specified tool.
    """

    cmd = f"{toolname} deploy"
    if pman.is_remote:
        cmd += f" -H {pman.hostname}"
    return cmd

def _get_deploy_suggestion(pman: ProcessManagerType,
                           prjname: str,
                           toolname: str,
                           what: str,
                           is_helper: bool = False) -> str:
    """
    Generate and return a suggestion message for deployment errors.

    Args:
        pman: The process manager object for the host where the deployable was supposed to be found.
        prjname: The name of the project the deployable belongs to.
        toolname: The name of the tool the deployable belongs to.
        what: A human-readable name of the deployable.
        is_helper: If 'True', the deployable is a helper (not a driver).

    Returns:
        str: A suggestion message with steps to resolve the deployment issue.
    """

    if not is_helper:
        return f"Please run '{_get_deploy_cmd(pman, toolname)}'"

    envar = ProjectFiles.get_project_helpers_envar(prjname)
    msg = f"Here are the options to try:\n" \
          f" * Run '{_get_deploy_cmd(pman, toolname)}'.\n" \
          f" * Ensure that {what} is in 'PATH'{pman.hostmsg}.\n" \
          f" * Set the '{envar}' environment variable to the path of {what}{pman.hostmsg}."
    return msg

def get_installed_deployable_path(prjname: str,
                                  toolname: str,
                                  deployable: str,
                                  pman: ProcessManagerType | None = None) -> Path:
    """
    Search for a deployable that belongs to the 'prjname' project.

    Args:
        prjname: The name of the project the deployable belongs to.
        toolname: The name of the tool the deployable belongs to.
        deployable: The name of the deployable to find.
        pman: The process manager object for the host to find the deployable on (the local host by
              default).

    Returns:
        Path: The path to the deployable if found.

    Raises:
        ErrorNotFound: If the deployable cannot be found.
    """

    with ProcessManager.pman_or_local(pman) as wpman:
        try:
            return ProjectFiles.find_project_helper(prjname, deployable, pman=wpman)
        except ErrorNotFound as err:
            what = f"the '{deployable}' helper program"
            errmsg = f"{err}\n"
            errmsg += _get_deploy_suggestion(wpman, prjname, toolname, what, is_helper=True)
            raise ErrorNotFound(errmsg) from None

def _get_insts_cats(deploy_info: DeployInfoTypedDict) -> \
                tuple[dict[str, InstallableInfoTypedDict],
                      dict[str, dict[str, InstallableInfoTypedDict]]]:
    """
    Build and return dictionaries for installables and categories based on 'deploy_info'.

    Args:
        deploy_info: A dictionary containing deployment information, including installables and
                    their categories.

    Returns:
        tuple: A tuple containing two dictionaries:
            * insts: A dictionary where keys are installable names and values are installable
                     information dictionaries.
            * cats: A dictionary where keys are category names and values are sub-dictionaries,
                    where keys are installable names and values are installable information
                    dictionaries for all the installables in the category.
    """

    insts: dict[str, InstallableInfoTypedDict] = {}
    cats: dict[str, dict[str, InstallableInfoTypedDict]] = {cat: {} for cat in CATEGORIES}

    for name, info in deploy_info["installables"].items():
        info = cast(InstallableInfoTypedDict, copy.deepcopy(info))
        info["name"] = name

        # Add category description to the installable information dictionary.
        catname = info["category"]
        info["category_descr"] = CATEGORIES[catname]

        insts[name] = info
        cats[catname][name] = info

    return insts, cats

class DeployCheckBase(ClassHelpers.SimpleCloseContext):
    """
    Provide API for verifying that all the required deployables are in place and up-to-date.
    """

    def __init__(self,
                 prjname: str,
                 toolname: str,
                 deploy_info: DeployInfoTypedDict,
                 pman: ProcessManagerType | None = None):
        """
        Initialize a class instance.

        Args:
            prjname: Name of the project 'toolname' belongs to.
            toolname: Name of the tool to check the deployment for.
            deploy_info: A dictionary containing deployment information (installables, categories,
                         etc).
            pman: The process manager object that defines the SUT to check the deployment at (local
                  host by default).
        """

        self._prjname = prjname
        self._toolname = toolname

        # Installables information.
        self._insts: dict[str, InstallableInfoTypedDict] = {}
        # Lists of installables in every category.
        self._cats: dict[str, dict[str, InstallableInfoTypedDict]] = {}

        self._time_delta: float | None = None

        if pman:
            self._spman = pman
            self._close_spman = False
        else:
            self._spman = LocalProcessManager.LocalProcessManager()
            self._close_spman = True

        self._insts, self._cats = _get_insts_cats(deploy_info)

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_spman",))

    @staticmethod
    def _get_newest_mtime(path: Path) -> float:
        """
        Find and return the most recent modification time of files in the given path.

        If the path is a directory, it recursively check all files within the directory
        and its subdirectories to find the most recent modification time. If the path is
        a file, it return the modification time of that file.

        Args:
            path: The path to a file or directory to check.

        Returns:
            The most recent modification time.

        Raises:
            ErrorNotFound: If no files are found in the given path.
        """

        newest = 0.0
        if not path.is_dir():
            mtime = path.stat().st_mtime
            newest = max(mtime, newest)
        else:
            for root, _, files in os.walk(path):
                for file in files:
                    mtime = Path(root, file).stat().st_mtime
                    newest = max(mtime, newest)

        if not newest:
            raise ErrorNotFound(f"No files found in the '{path}'")

        return newest

    def _get_deployables(self, category) -> Iterator[str]:
        """
        Yield all deployable items for a given category.

        Args:
            category: The category for which to retrieve deployable items.

        Yields:
            Names of all deployables for the specified category.
        """

        for inst_info in self._cats[category].values():
            yield from inst_info["deployables"]

    def _get_installed_deployable_path(self, deployable: str) -> Path:
        """
        Return the path of an installed helper deployable (a non-driver ) on the SUT.

        Args:
            deployable: The name of the deployable.

        Returns:
            The path to the installed deployable on the SUT.
        """

        return get_installed_deployable_path(self._prjname, self._toolname, deployable,
                                             pman=self._spman)

    def _get_deployable_print_name(self, installable: str, deployable: str) -> str:
        """
        Returns a human-readable name for a deployable.

        Args:
            installable: The name of the installable.
            deployable: The name of the deployable.

        Returns:
            A string representing a human-readable name for the deployable.
        """

        cat_descr = self._insts[installable]["category_descr"]
        if deployable != installable:
            return f"The '{deployable}' component of the '{installable}' {cat_descr}"
        return f"The '{deployable}' {cat_descr}"

    def _deployable_not_found(self, installable: str, deployable: str):
        """
        Handle the case when a deployable is not found: format an appropriate error message and
        raise an 'ErrorNotFound' exception.

        Args:
            installable: The name of the installable the deployable belongs to.
            deployable: The name of the deployable item that was not found.

        Raises:
            ErrorNotFound: this exception is raised with a formatted error message suggesting
                           possible solutions.
        """

        what = self._get_deployable_print_name(installable, deployable)
        is_helper = self._insts[installable]["category"] != "drivers"

        err = _get_deploy_suggestion(self._spman, self._prjname, self._toolname, what,
                                     is_helper=is_helper)
        raise ErrorNotFound(err) from None

    def _warn_deployable_out_of_date(self, installable: str, deployable: str):
        """
        Print a warning about the specified deployable not being up-to-date.

        Args:
            installable: The name of the installable the deployable belongs to.
            deployable: The name of the deployable to check.
        """

        what = self._get_deployable_print_name(installable, deployable)

        _LOG.warning("%s may be out of date%s, consider running '%s'",
                     what, self._spman.hostmsg, _get_deploy_cmd(self._spman, self._toolname))

    def _check_deployable_up_to_date(self,
                                     installable: str,
                                     deployable: str,
                                     srcpath: Path,
                                     dstpath: Path):
        """
        Check if a deployable at 'dstpath' on the System Under Test (SUT) is up-to-date by comparing
        its modification time ('mtime') to 'mtime' of the source code of the deployable at 'srcpath'
        on the controller.

        Print a if the deployable is out-of-date.

        Args:
            installable: The name of the installable the deployable belongs to.
            deployable: The name of the deployable to check.
            srcpath: The path to the source code of the deployable on the controller.
            dstpath: The path to the deployable on the SUT.
        """

        if self._time_delta is None:
            if self._spman.is_remote:
                # Take into account the possible time difference between local and remote
                # systems.
                self._time_delta = time.time() - self._spman.time_time()
            else:
                self._time_delta = 0

        src_mtime = self._get_newest_mtime(srcpath)
        dst_mtime = self._spman.get_mtime(dstpath)

        if src_mtime > self._time_delta + dst_mtime:
            _LOG.debug("src mtime %d > %d + dst mtime %d, src: %s, dst %s",
                       src_mtime, self._time_delta, dst_mtime, srcpath, dstpath)
            self._warn_deployable_out_of_date(installable, deployable)

    def _check_deployment(self):
        """
        Checks if all the required installables have been deployed and are up-to-date.

        Raises:
            NotImplementedError: The method is not implemented by the subclass.
        """

        raise NotImplementedError()

    def check_deployment(self):
        """
        Check if all the required installables have been deployed and are up-to-date.

        Raises:
            DeploymentError: If any required installable is not deployed or outdated.
        """

        self._time_delta = None
        self._check_deployment()

class DeployBase(ClassHelpers.SimpleCloseContext):
    """The base class for software deployment sub-classes."""

    def __init__(self,
                 prjname: str,
                 toolname: str,
                 deploy_info: DeployInfoTypedDict,
                 pman: ProcessManagerType | None = None,
                 lbuild: bool = False,
                 tmpdir_path: Path | None = None,
                 keep_tmpdir: bool = False,
                 debug: bool = False):
        """
        Initialize class instance.

        Args:
            prjname: Name of the project 'toolname' belongs to.
            toolname: Name of the tool to deploy.
            deploy_info: A dictionary describing what should be deployed.
            pman: The process manager object that defines the SUT to deploy to (local host by
                  default).
            lbuild: If 'True', build everything on the local host.
            tmpdir_path: Path to use as a temporary directory (a random temporary directory is
                         created by default).
            keep_tmpdir: If 'False', remove the temporary directory when finished. If 'True', do not
                         remove it.
            debug: If 'True', be more verbose.

        The 'deploy_info' dictionary describes the tool to deploy and its dependencies. It should
        have the following structure:

        {
            "installables": {
            "Installable name 1": {
                "category": "category name of the installable (e.g., 'drivers', 'shelpers', etc.)",
                "minkver": "minimum SUT kernel version required for the installable",
                "deployables": ["list of deployables this installable provides"]
            },
            "Installable name 2": {},
            ... etc for every installable ...
            }
        }
        """

        self._prjname = prjname
        self._toolname = toolname
        self._lbuild = lbuild
        self._tmpdir_path = tmpdir_path
        self._keep_tmpdir = keep_tmpdir
        self._debug = debug

        # Process manager associated with the SUT.
        self._spman: ProcessManagerType
        # Process manager associated with the build host.
        self._bpman: ProcessManagerType
        # Process manager associated with the controller (local host).
        self._cpman: ProcessManagerType

        self._close_spman = False
        self._close_cpman = False

        # Installables information.
        self._insts: dict[str, InstallableInfoTypedDict] = {}
        # Lists of installables in every category.
        self._cats: dict[str, dict[str, InstallableInfoTypedDict]] = {}

        # Temporary directory on the SUT.
        self._stmpdir: Path | None = None
        # Temporary directory on the controller (local host).
        self._ctmpdir: Path | None = None
        # Temporary directory on the build host.
        self._btmpdir: Path | None = None

        # Temp. directory on the SUT has been created.
        self._stmpdir_created = False
        # Temp. directory on the controller has been created.
        self._ctmpdir_created = False

        if pman:
            self._spman = pman
            self._cpman = LocalProcessManager.LocalProcessManager()
            self._close_spman = False
            self._close_cpman = True
        else:
            self._spman = LocalProcessManager.LocalProcessManager()
            self._cpman = self._spman
            self._close_spman = True
            self._close_cpman = False

        if self._lbuild:
            self._bpman = self._cpman
        else:
            self._bpman = self._spman

        self._insts, self._cats = _get_insts_cats(deploy_info)

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_spman", "_cpman"), unref_attrs=("_bpman",))

    def _get_deployables(self, category) -> Iterator[str]:
        """
        Yield all deployable items for a given category.

        Args:
            category: The category for which to retrieve deployable items.

        Yields:
            Names of all deployables for the specified category.
        """

        for inst_info in self._cats[category].values():
            yield from inst_info["deployables"]

    def _get_stmpdir(self) -> Path:
        """
        Create a temporary directory on the System Under Test (SUT) and return its path.

        Returns:
            Path: The path to the temporary directory on the SUT.
        """

        if not self._stmpdir:
            self._stmpdir_created = True
            if not self._tmpdir_path:
                self._stmpdir = self._spman.mkdtemp(prefix=f"{self._toolname}-")
            else:
                self._stmpdir = self._tmpdir_path
                try:
                    self._spman.mkdir(self._stmpdir, parents=True, exist_ok=False)
                except ErrorExists:
                    self._stmpdir_created = False

        assert self._stmpdir is not None
        return self._stmpdir

    def _get_ctmpdir(self) -> Path:
        """
        Create a temporary directory on the controller and return its path.

        Returns:
            Path: The path to the temporary directory on the controller.
        """

        if not self._ctmpdir:
            self._ctmpdir_created = True
            if not self._tmpdir_path:
                self._ctmpdir = self._cpman.mkdtemp(prefix=f"{self._toolname}-")
            else:
                self._ctmpdir = self._tmpdir_path
                try:
                    self._cpman.mkdir(self._ctmpdir, parents=True, exist_ok=False)
                except ErrorExists:
                    self._ctmpdir_created = False

        assert self._ctmpdir is not None
        return self._ctmpdir

    def _get_btmpdir(self) -> Path:
        """
        Create a temporary directory on the build host and return its path.

        Returns:
            Path: The path to the temporary directory on the build host.
        """

        if self._lbuild:
            self._btmpdir = self._get_ctmpdir()
        else:
            self._btmpdir = self._get_stmpdir()

        return self._btmpdir

    def _remove_tmpdirs(self):
        """Remove temporary directories."""

        spman: ProcessManagerType | None = getattr(self, "_spman", None)
        cpman: ProcessManagerType | None = getattr(self, "_cpman", None)

        if not cpman or not spman:
            return

        preserved = []
        if self._stmpdir and self._stmpdir_created:
            if not self._keep_tmpdir:
                spman.rmtree(self._stmpdir)
            else:
                preserved.append(f"On the SUT ({spman.hostname}): {self._stmpdir}")
        if self._ctmpdir and cpman is not spman and self._ctmpdir_created:
            if not self._keep_tmpdir:
                cpman.rmtree(self._ctmpdir)
            else:
                preserved.append(f"On the controller ({cpman.hostname}): {self._ctmpdir}")

        if preserved:
            _LOG.info("Preserved the following temporary directories:\n * %s",
                      "\n * ".join(preserved))

    def _drop_installable(self, installable: str):
        """
        Remove an installable from data structures.

        Args:
            installable): The name of the installable to be removed.
        """

        _LOG.debug("Dropping the '%s' installable", installable)

        cat = self._insts[installable]["category"]
        del self._insts[installable]
        del self._cats[cat][installable]
