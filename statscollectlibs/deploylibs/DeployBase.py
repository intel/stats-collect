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
    * category - type of an installable. Currently, there are 4 categories: drivers, simple helpers
                 shelpers), python helpers (pyhelpers), and eBPF helpers (bpfhelpers).
    * installable - a sub-project to install on the SUT (System Under Test).
    * deployable - each installable provides one or multiple deployables. For example, one or
                   multiple drivers.
    * helper - a special type of deployable. Helpers are stand-alone programs that are not part of
               the main tool but are used by the tool. Examples of deployables that are not helpers:
               kernel drivers. Examples of deployables that are also helpers: a C program which
               comes in form of source code, a Python script.

Installable vs Deployable:
    * Installables come in the form of source code. Deployables are individual executable programs
      (script, binary) or kernel drivers.
    * An installable corresponds to a directory with source code and/or scripts. The source code may
      need to be compiled. The compilation results in one or several deployables. The scripts in the
      installable directory may be deployables.
    * Deployables are ultimately copied to the SUT and executed on the SUT.

Helpers Types:
    1. Simple helpers (shelpers) are stand-alone independent programs, which come in the form of a
       single executable file.
    2. eBPF helpers (bpfhelpers) consist of 2 components: the user-space component and the eBPF
       component. The user-space component is distributed as source code and must be compiled.
       The eBPF component is distributed as both source code and binary.
    3. Python helpers (pyhelpers) are helper programs written in Python. Unlike simple helpers,
       they are not totally independent but depend on various Python modules. Deploying a Python
       helper is trickier because all Python modules should also be deployed.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import os
import time
import copy
from typing import TypedDict, Literal, cast, Iterator
from pathlib import Path
from pepclibs.helperlibs import Logging, ClassHelpers, ProcessManager, LocalProcessManager
from pepclibs.helperlibs import ProjectFiles
from pepclibs.helperlibs.ProcessManager import ProcessManagerType
from pepclibs.helperlibs.Exceptions import Error, ErrorExists, ErrorNotFound

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

# The supported installable categories.
InstallableCategoriesType = Literal["drivers", "shelpers", "pyhelpers", "bpfhelpers"]

class InstallableInfoType(TypedDict, total=False):
    """
    The type of the dictionary that describes an installable.

    Attributes:
        category: Category name of the installable ("drivers", "shelpers", etc).
        minkver: Minimum SUT kernel version required for the installable.
        deployables: List of deployables this installable provides.
    """

    category: InstallableCategoriesType
    minkver: str
    deployables: tuple[str, ...]

# The tool deploy information type.
class DeployInfoType(TypedDict):
    """
    The deployment description dictionary type.

    Attributes:
        installables: Dictionary of installables. The key is the installable name, and the value is
                      the installable information dictionary.
    """
    installables: dict[str, InstallableInfoType]

# The supported installable categories.
CATEGORIES: dict[InstallableCategoriesType, str] = {"drivers"    : "kernel driver",
                                                    "shelpers"   : "simple helper program",
                                                    "pyhelpers"  : "python helper program",
                                                    "bpfhelpers" : "eBPF helper program"}

class _ExtInstInfoType(InstallableInfoType, total=False):
    """
    The extended installable information dictionary type.

    Attributes:
        name: The name of the installable.
        category_descr: The description of the installable category.
    """

    name: str
    category_descr: str

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
                           is_helper: bool) -> str:
    """
    Generate and return a suggestion message for deployment errors.

    Args:
        pman: The process manager object for the host where the deployable was supposed to be found.
        prjname: The name of the project the deployable belongs to.
        toolname: The name of the tool the deployable belongs to.
        what: A human-readable name of the deployable.
        is_helper: If 'True', the deployable is a helper program.

    Returns:
        str: A suggestion message with steps to resolve the deployment issue.
    """

    if not is_helper:
        return f"Please run '{_get_deploy_cmd(pman, toolname)}'"

    envvar = ProjectFiles.get_project_helpers_envvar(prjname)
    msg = f"Here are the options to try:\n" \
          f" * Run '{_get_deploy_cmd(pman, toolname)}'.\n" \
          f" * Ensure that {what} is in 'PATH'{pman.hostmsg}.\n" \
          f" * Set the '{envvar}' environment variable to the path of {what}{pman.hostmsg}."
    return msg

def get_installed_helper_path(prjname: str,
                              toolname: str,
                              helper: str,
                              pman: ProcessManagerType | None = None) -> Path:
    """
    Search for a helper program named 'helper' that belongs to the 'prjname' project.

    Args:
        prjname: The name of the project the helper program belongs to.
        toolname: The name of the tool the helper program belongs to.
        helper: The name of the helper program to find.
        pman: The process manager object for the host to find the helper on (the local host by
              default).

    Returns:
        Path: The path to the helper program if found.

    Raises:
        ErrorNotFound: If the helper program cannot be found.
    """

    with ProcessManager.pman_or_local(pman) as wpman:
        try:
            return ProjectFiles.find_project_helper(prjname, helper, pman=wpman)
        except ErrorNotFound as err:
            what = f"the '{helper}' helper program"
            errmsg = f"{err}\n"
            errmsg += _get_deploy_suggestion(wpman, prjname, toolname, what, is_helper=True)
            raise ErrorNotFound(errmsg) from None

def _get_insts_cats(deploy_info: DeployInfoType) -> tuple[dict[str, _ExtInstInfoType],
                                                          dict[str, dict[str, _ExtInstInfoType]]]:
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

    insts: dict[str, _ExtInstInfoType] = {}
    cats: dict[str, dict[str, _ExtInstInfoType]] = {cat: {} for cat in CATEGORIES}

    for name, info in deploy_info["installables"].items():
        info = cast(_ExtInstInfoType, copy.deepcopy(info))
        info["name"] = name

        # Add category description to the installable information dictionary.
        catname = info["category"]
        info["category_descr"] = CATEGORIES[catname]

        insts[name] = info
        cats[catname][name] = info

    return insts, cats

class DeployCheckBase(ClassHelpers.SimpleCloseContext):
    """
    This is a base class for verifying whether all the required installables have been deployed and
    up-to-date.
    """

    @staticmethod
    def _get_newest_mtime(path):
        """Find and return the most recent modification time of files of 'path'."""

        newest = 0
        if not path.is_dir():
            mtime = path.stat().st_mtime
            if mtime > newest:
                newest = mtime
        else:
            for root, _, files in os.walk(path):
                for file in files:
                    mtime = Path(root, file).stat().st_mtime
                    if mtime > newest:
                        newest = mtime

        if not newest:
            raise Error(f"no files found in the '{path}'")
        return newest

    def _get_deployables(self, category):
        """Yield all deployable names for category 'category' (e.g., "drivers")."""

        for inst_info in self._cats[category].values():
            for deployable in inst_info["deployables"]:
                yield deployable

    def _get_installed_deployable_path(self, deployable):
        """Same as 'DeployBase.get_installed_helper_path()'."""
        return get_installed_helper_path(self._prjname, self._toolname, deployable,
                                         pman=self._spman)

    def _get_installable_by_deployable(self, deployable):
        """Returns installable name and information dictionary for a deployable."""

        for installable, inst_info in self._insts.items():
            if deployable in inst_info["deployables"]:
                break
        else:
            raise Error(f"bad deployable name '{deployable}'")

        return installable # pylint: disable=undefined-loop-variable

    def _get_deployable_print_name(self, installable, deployable):
        """Returns a nice, printable human-readable name of a deployable."""

        cat_descr = self._insts[installable]["category_descr"]
        if deployable != installable:
            return f"the '{deployable}' component of the '{installable}' {cat_descr}"
        return f"the '{deployable}' {cat_descr}"

    def _deployable_not_found(self, deployable):
        """
        Called in a situation when 'deployable' was not found. Formats an error message and
        raises 'ErrorNotFound'.
        """

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)
        is_helper = self._insts[installable]["category"] != "drivers"

        err = _get_deploy_suggestion(self._spman, self._prjname, self._toolname, what, is_helper)
        raise ErrorNotFound(err) from None

    def _warn_deployable_out_of_date(self, deployable):
        """Print a warning about the 'what' deployable not being up-to-date."""

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)

        _LOG.warning("%s may be out of date%s, consider running '%s'",
                     what, self._spman.hostmsg, _get_deploy_cmd(self._spman, self._toolname))

    def _check_deployable_up_to_date(self, deployable, srcpath, dstpath):
        """
        Check that a deployable at 'dstpath' on SUT is up-to-date by comparing its 'mtime' to the
        source (code) of the deployable at 'srcpath' on the controller.
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
            self._warn_deployable_out_of_date(deployable)

    def _check_deployment(self):
        """
        Check if all the required installables have been deployed and up-to-date. Has to be
        implemented by the sub-class.
        """

        raise NotImplementedError()

    def check_deployment(self):
        """Check if all the required installables have been deployed and up-to-date."""

        self._time_delta = None
        self._check_deployment()

    def __init__(self, prjname, toolname, deploy_info, pman=None):
        """
        The class constructor. The arguments are as follows.
          * prjname - name of the project 'toolname' belongs to.
          * toolname - name of the tool to check the deployment for.
          * deploy_info - a dictionary describing the tool to deploy. Check 'DeployBase.__init__()'
                          for more information.
          * pman - the process manager object that defines the SUT to check the deployment at (local
            host by default).
        """

        self._prjname = prjname
        self._toolname = toolname

        self._insts = None # Installables information.
        self._cats = None  # Lists of installables in every category.
        self._time_delta = None

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

class DeployBase(ClassHelpers.SimpleCloseContext):
    """The base class for software deployment sub-classes."""

    def __init__(self,
                 prjname: str,
                 toolname: str,
                 deploy_info: DeployInfoType,
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
            debug: If 'True', be more verbose. Defaults to False.

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
        self._insts: dict[str, _ExtInstInfoType] = {}
        # Lists of installables in every category.
        self._cats: dict[str, dict[str, _ExtInstInfoType]] = {}

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
