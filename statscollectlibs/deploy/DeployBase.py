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
    - category: type of an installable. Currently, there are 3 categories: drivers, simple helpers
                (shelpers) and python helpers (pyhelpers).
    - installable: a sub-project to install on the SUT (System Under Test). An installable may
                   include one or more deployable. For example, a driver installable may include
                   multiple drivers. A python helper installable may include multiple python helper
                   scripts.
    - deployable: each installable provides one or multiple deployables of the same category as the
                  installable.
    - helper: somewhat poorly defined term. In the context of this module, a helper may refer to a
              non-driver installable. For example, a python helper installable. But also a helper
              may refer to a single non-driver deployable. For example, a python helper script.

Installable vs Deployable:
    - Installables come in the form of source code. Deployables are individual executable programs
      (script, binary) or kernel drivers.
    - An installable corresponds to a directory with source code and/or scripts. The source code may
      need to be compiled. The compilation results in one or several deployables. The scripts in the
      installable directory may be deployables.
    - Deployables are ultimately copied to the SUT and executed on the SUT.

Helper deployable types:
    1. Simple helpers (shelpers) are stand-alone independent programs, which come in the form of a
       single executable file.
    2. Python helpers (pyhelpers) are helper programs written in Python. Unlike simple helpers,
       they are not totally independent but depend on various Python modules. Deploying a Python
       helper is trickier because all Python modules should also be deployed.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import copy
import typing
from pathlib import Path
from pepclibs.helperlibs import Logging, ClassHelpers, ProcessManager, LocalProcessManager
from pepclibs.helperlibs import ProjectFiles
from pepclibs.helperlibs.Exceptions import ErrorExists, ErrorNotFound

if typing.TYPE_CHECKING:
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from typing import TypedDict, Literal, cast, Iterator

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
            subdir: Optional sub-directory under the project helpers search roots where the
                    deployables reside (e.g. 'workloads'). An empty string or a missing key means
                    the deployables are located directly under the search root.
        """

        name: str
        category: InstallableCategoriesType
        category_descr: str
        minkver: str
        deployables: tuple[str, ...]
        subdir: str

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
_CATEGORIES: dict[InstallableCategoriesType, str] = {"drivers": "kernel driver",
                                                     "shelpers": "simple helper program",
                                                     "pyhelpers": "python helper program"}

def _get_deploy_cmd(pman: ProcessManagerType, toolname: str) -> str:
    """
    Generate the deployment command for a given tool.

    Args:
        pman: The process manager object representing the host where the tool will be deployed.
        toolname: The name of the tool for which the deployment command is generated.

    Returns:
        The command that should be run to deploy the specified tool.
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
        A suggestion message with steps to resolve the deployment issue.
    """

    if not is_helper:
        return f"Please run '{_get_deploy_cmd(pman, toolname)}'"

    envar = ProjectFiles.get_project_helpers_envar(prjname)
    msg = f"Here are the options to try:\n" \
          f" - Run '{_get_deploy_cmd(pman, toolname)}'.\n" \
          f" - Ensure that {what} is in 'PATH'{pman.hostmsg}.\n" \
          f" - Set the '{envar}' environment variable to the path of {what}{pman.hostmsg}."
    return msg

def get_installed_deployable_path(prjname: str,
                                  toolname: str,
                                  deployable: str,
                                  pman: ProcessManagerType | None = None) -> Path:
    """
    Find and return the path to a deployable that belongs to the 'prjname' project.

    Args:
        prjname: The name of the project the deployable belongs to.
        toolname: The name of the tool the deployable belongs to.
        deployable: The name of the deployable to find.
        pman: The process manager object for the host to find the deployable on (the local host by
              default).

    Returns:
        The path to the deployable if found.

    Raises:
        ErrorNotFound: The deployable cannot be found.
    """

    with ProcessManager.pman_or_local(pman) as wpman:
        try:
            return ProjectFiles.find_project_helper(prjname, deployable, pman=wpman)
        except ErrorNotFound as err:
            what = f"the '{deployable}' helper program"
            errmsg = f"{err}\n"
            errmsg += _get_deploy_suggestion(wpman, prjname, toolname, what, is_helper=True)
            raise ErrorNotFound(errmsg) from err

def _get_insts_cats(deploy_info: DeployInfoTypedDict) -> \
                                             tuple[dict[str, InstallableInfoTypedDict],
                                                   dict[str, dict[str, InstallableInfoTypedDict]]]:
    """
    Build and return dictionaries for installables and categories based on 'deploy_info'.

    Args:
        deploy_info: A dictionary containing deployment information, including installables and
                     their categories.

    Returns:
        A tuple containing two dictionaries:
            - insts: A dictionary where keys are installable names and values are installable
                     information dictionaries.
            - cats: A dictionary where keys are category names and values are sub-dictionaries,
                    where keys are installable names and values are installable information
                    dictionaries for all the installables in the category.

    Examples:
        Input:
            deploy_info = {
                "installables": {
                    "stc-agent": {
                        "category": "pyhelpers",
                        "deployables": ("stc-agent", "stc-agent-ipmi-helper"),
                    },
                },
            }

        Output:
            insts = {
                "stc-agent": {
                    "name": "stc-agent",
                    "category": "pyhelpers",
                    "category_descr": "python helper program",
                    "deployables": ("stc-agent", "stc-agent-ipmi-helper"),
                },
            }

            cats = {
                "drivers": {},
                "shelpers": {},
                "pyhelpers": {
                    "stc-agent": {
                        "name": "stc-agent",
                        "category": "pyhelpers",
                        "category_descr": "python helper program",
                        "deployables": ("stc-agent", "stc-agent-ipmi-helper"),
                    },
                },
            }
    """

    insts: dict[str, InstallableInfoTypedDict] = {}
    cats: dict[str, dict[str, InstallableInfoTypedDict]] = {cat: {} for cat in _CATEGORIES}

    for name, info in deploy_info["installables"].items():
        _info = copy.deepcopy(info)
        if typing.TYPE_CHECKING:
            info = cast(InstallableInfoTypedDict, _info)
        else:
            info = _info

        info["name"] = name

        # Add category description to the installable information dictionary.
        catname = info["category"]
        info["category_descr"] = _CATEGORIES[catname]

        insts[name] = info
        cats[catname][name] = info

    return insts, cats

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
            deploy_info: A dictionary describing the tool's installables and their deployables. See
                         'Examples' for the expected structure.
            pman: The process manager object that defines the SUT to deploy to (local host by
                  default).
            lbuild: If 'True', build everything on the local host.
            tmpdir_path: The path to use as a temporary directory on each involved host (SUT, build
                         host, and controller). The directory is created if it does not exist. A
                         random temporary directory is created on each host by default.
            keep_tmpdir: If 'True', temporary directories are preserved after deployment finishes.
                         If 'False', they are removed. Useful for debugging.
            debug: If 'True', be more verbose.

        Examples:
            A 'deploy_info' dictionary for a tool with all three installable categories - a kernel
            driver, a simple helper, and a python helper:

                deploy_info = {
                    "installables": {
                        "ndl": {
                            "category": "drivers",
                            "minkver": "5.2",
                            "deployables": ("ndl",),
                        },
                        "ndl-helper": {
                            "category": "shelpers",
                            "deployables": ("ndl-helper",),
                        },
                        "stc-agent": {
                            "category": "pyhelpers",
                            "deployables": ("stc-agent", "stc-agent-ipmi-helper"),
                        },
                        "stc-wl-cpu-wake-walk": {
                            "category": "pyhelpers",
                            "deployables": ("stc-wl-cpu-wake-walk",),
                            "subdir": "workloads",
                        },
                    },
                }

            The optional "minkver" key specifies the minimum SUT kernel version required for the
            installable. The optional "subdir" key specifies a sub-directory under the project
            helpers search roots where the deployables reside.
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
            The path to the temporary directory on the SUT.
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
            The path to the temporary directory on the controller.
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
            The path to the temporary directory on the build host.
        """

        if self._lbuild:
            self._btmpdir = self._get_ctmpdir()
        else:
            self._btmpdir = self._get_stmpdir()

        return self._btmpdir

    def _remove_tmpdirs(self):
        """
        Remove temporary directories created during deployment.

        Subclasses are responsible for calling this method when deployment finishes. If
        'keep_tmpdir' is 'True', the directories are preserved instead of removed.
        """

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
            installable: The name of the installable to be removed.
        """

        _LOG.debug("Dropping the '%s' installable", installable)

        cat = self._insts[installable]["category"]
        del self._insts[installable]
        del self._cats[cat][installable]
