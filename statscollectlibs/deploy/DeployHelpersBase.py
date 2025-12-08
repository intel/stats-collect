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
import typing
from pathlib import Path
from pepclibs.helperlibs import Logging, ProjectFiles, ToolChecker
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.deploy import DeployInstallableBase

if typing.TYPE_CHECKING:
    from typing import Final
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from statscollectlibs.deploy.DeployBase import InstallableInfoTypedDict

HELPERS_DEPLOY_SUBDIR: Final[Path] = Path(".local")
HELPERS_SRC_SUBDIR: Final[Path] = Path("helpers")

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

    def _prepare(self, insts_info: dict[str, InstallableInfoTypedDict], insts_basedir: Path):
        """
        Build and prepare installables for deployment.

        Args:
            insts_info: The installables information dictionary.
            insts_basedir: Path to the base directory that contains the installables on the
                           controller (local host).

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
        stdout, _ = self._spman.run_verify_join(f"echo ${envar}")
        helpers_path: str | Path = stdout.strip()
        if not helpers_path:
            if envar in os.environ:
                helpers_path = os.environ[envar]
            else:
                homedir = self._spman.get_envar("HOME")
                if homedir:
                    helpers_path =  Path(homedir) / HELPERS_DEPLOY_SUBDIR / "bin"
        return Path(helpers_path)

    def deploy(self, insts_info: dict[str, InstallableInfoTypedDict],
               insts_basedir: Path | None = None):
        """
        Deploy installables to the System Under Test (SUT).

        Args:
            insts_info: The installables information dictionary.
            insts_basedir: Path to the base directory that contains the installables on the
                           controller (local host).
        """

        if not insts_basedir:
            # Find the installables base directory. We assume all installables are located in the
            # same base directory.
            some_installable = next(iter(insts_info))
            some_installable_path = HELPERS_SRC_SUBDIR/f"{some_installable}"
            what = f"sources of {self._what}"
            some_installable_path = ProjectFiles.find_project_data(self._prjname,
                                                                   some_installable_path,
                                                                   what=what)
            insts_basedir = some_installable_path.parent

            # Make sure all helpers are available.
            for installable in insts_info:
                installabledir = insts_basedir / installable
                if not installabledir.is_dir():
                    raise Error(f"Path '{installabledir}' does not exist or it is not a directory")

        assert insts_basedir is not None
        self._prepare(insts_info, insts_basedir)

        deploy_path = self._get_deploy_path()

        # Make sure the the destination deployment directory exists.
        self._spman.mkdir(deploy_path, parents=True, exist_ok=True)

        # Deploy all helpers.
        _LOG.info("Deploying %s to '%s'%s", self._what, deploy_path, self._spman.hostmsg)

        for installable in insts_info:
            binstpath = f"{self._btmpdir}/{installable}"
            sinstpath = f"{self._stmpdir}/{installable}"

            _LOG.debug("Deploying installable '%s' to '%s'%s",
                       installable, deploy_path, self._spman.hostmsg)

            if not self._bpman.is_remote and self._spman.is_remote:
                # The installables were built locally (in 'self._prepare()), but they should be
                # installed on the SUT. Copy them to the SUT first.
                self._spman.rsync(str(binstpath) + "/", sinstpath,
                                  remotesrc=self._bpman.is_remote, remotedst=self._spman.is_remote)

            if self._spman.exists(f"{sinstpath}/Makefile"):
                inst_dstdir = self._stmpdir / f"{installable}-deployed"
                # Install by running 'make install'.
                cmd = f"make -C '{sinstpath}' install PREFIX='{inst_dstdir}'"
                stdout, stderr = self._spman.run_verify_join(cmd)
                self._log_cmd_output(stdout, stderr)

                self._spman.rsync(str(inst_dstdir) + "/bin/", deploy_path,
                                  remotesrc=self._spman.is_remote,
                                  remotedst=self._spman.is_remote)
            else:
                # Just copy the deployable files.
                for deployable in insts_info[installable]["deployables"]:
                    _LOG.debug("Deploying '%s' to '%s'%s",
                               deployable, deploy_path, self._spman.hostmsg)
                    srcpath = f"{sinstpath}/{deployable}"
                    dstpath = deploy_path / deployable
                    self._spman.rsync(srcpath, dstpath,
                                      remotesrc=self._spman.is_remote,
                                      remotedst=self._spman.is_remote)
