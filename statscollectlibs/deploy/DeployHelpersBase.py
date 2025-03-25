# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide base class for deploying non-driver installables (helpers). Refer to the 'DeployBase' module
docstring for terminology reference.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import os
from pathlib import Path
from pepclibs.helperlibs import Logging, ProjectFiles, ToolChecker
from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs.ProcessManager import ProcessManagerType
from statscollectlibs.deploy import DeployInstallableBase
from statscollectlibs.deploy.DeployBase import InstallableInfoTypedDict

HELPERS_DEPLOY_SUBDIR = Path(".local")
HELPERS_SRC_SUBDIR = Path("helpers")

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class DeployHelpersBase(DeployInstallableBase.DeployInstallableBase):
    """Base class for deploying non-driver installables (helpers)."""

    def __init__(self,
                 prjname: str,
                 toolname: str,
                 what: str,
                 spman: ProcessManagerType,
                 bpman: ProcessManagerType,
                 stmpdir: Path,
                 btmpdir: Path,
                 cpman: ProcessManagerType | None = None,
                 ctmpdir: Path | None = None,
                 btchk: ToolChecker.ToolChecker | None = None,
                 debug: bool = False):
        """
        Initialize a class instance.

        Args:
            prjname: Name of the project the helpers and 'toolname' belong to.
            toolname: Name of the tool the helpers belong to.
            spman: A process manager object associated with the SUT (System Under Test).
            bpman: A process manager object associated with the build host (the host where the
                   helper should be built).
            stmpdir: A temporary directory on the SUT.
            btmpdir: Path to a temporary directory on the build host.
            cpman: A process manager object associated with the controller (local host). Defaults to
                   'spman'.
            ctmpdir: Path to a temporary directory on the controller. Defaults to 'stmpdir'.
            btchk: An instance of 'ToolChecker' that can be used for checking the availability of
                   various tools on the build host. Will be created if not provided.
            debug: A boolean variable for enabling additional debugging messages.
        """

        self._what = what
        super().__init__(prjname, toolname, spman, bpman, stmpdir, btmpdir, cpman=cpman,
                         ctmpdir=ctmpdir, btchk=btchk, debug=debug)

    def _prepare(self, insts_info: dict[str, InstallableInfoTypedDict], installables_basedir: Path):
        """
        Build and prepare installables for deployment.

        Args:
            insts_info: The installables information dictionary.
            installables_basedir: Path to the base directory that contains the installables on the
                                  controller.

        Raises:
            NotImplementedError: The method is not implemented by the subclass.
        """

        raise NotImplementedError()

    def _get_deploy_path(self) -> Path:
        """
        Return the path to the directory where the helper deployables should be deployed.

        Returns:
            Path: The path to the directory where the helper programs should be deployed.
        """

        envar = ProjectFiles.get_project_helpers_envar("stats-collect")
        stdout, _ = self._spman.run_verify(f"echo ${envar}")
        helpers_path = stdout.strip()
        if not helpers_path:
            helpers_path = os.environ.get(envar)
        if not helpers_path:
            homedir = self._spman.get_envar("HOME")
            if homedir:
                helpers_path =  Path(homedir) / HELPERS_DEPLOY_SUBDIR / "bin"
        return Path(helpers_path)

    def deploy(self, insts_info: dict[str, InstallableInfoTypedDict]):
        """
        Deploy installables to the System Under Test (SUT).

        Args:
            insts_info: The installables information dictionary.
        """

        # Find the installables base directory. We assume all installables are located in the same
        # base directory.
        some_installable = next(iter(insts_info))
        some_installable_path = HELPERS_SRC_SUBDIR/f"{some_installable}"
        what = f"sources of {self._what}"
        some_installable_path = ProjectFiles.find_project_data(self._prjname, some_installable_path,
                                                               what=what)
        installables_basedir = some_installable_path.parent

        # Make sure all helpers are available.
        for installable in insts_info:
            installabledir = installables_basedir / installable
            if not installabledir.is_dir():
                raise Error(f"Path '{installabledir}' does not exist or it is not a directory")

        self._prepare(insts_info, installables_basedir)

        deploy_path = self._get_deploy_path()

        # Make sure the the destination deployment directory exists.
        self._spman.mkdir(deploy_path, parents=True, exist_ok=True)

        # Deploy all helpers.
        _LOG.info("Deploying %s to '%s'%s", self._what, deploy_path, self._spman.hostmsg)

        for installable in insts_info:
            installable_dstdir = self._stmpdir / f"{installable}-deployed"
            _LOG.debug("deploying helper installable helper '%s' to '%s'%s",
                       installable, installable_dstdir, self._spman.hostmsg)

            binstpath = f"{self._btmpdir}/{installable}"
            sinstpath = f"{self._stmpdir}/{installable}"

            if not self._bpman.is_remote and self._spman.is_remote:
                # The installables were built locally (in 'self._prepare()), but they should be
                # installed on the SUT. Copy them to the SUT first.
                self._spman.rsync(str(binstpath) + "/", sinstpath,
                                  remotesrc=self._bpman.is_remote, remotedst=self._spman.is_remote)

            cmd = f"make -C '{sinstpath}' install PREFIX='{installable_dstdir}'"
            stdout, stderr = self._spman.run_verify(cmd)
            self._log_cmd_output(stdout, stderr)

            self._spman.rsync(str(installable_dstdir) + "/bin/", deploy_path,
                              remotesrc=self._spman.is_remote,
                              remotedst=self._spman.is_remote)
