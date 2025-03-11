# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the API for deploying the installables of tools in the 'stats-collect' project."""

from pathlib import Path
from typing import Callable, Any
from pepclibs.helperlibs import Logging, ArgParse, ProjectFiles
from pepclibs.helperlibs.ProcessManager import ProcessManagerType
from pepclibs.helperlibs.Exceptions import ErrorNotFound
from statscollectlibs.deploylibs import DeployBase, _DeployPyHelpers, DeployHelpersBase
from statscollectlibs.deploylibs.DeployBase import DeployInfoType

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

def add_deploy_cmdline_args(toolname: str,
                            subparsers: ArgParse.SubParsersType,
                            func: Callable,
                            argcomplete: Any = None) -> ArgParse.ArgsParser:
    """
    Adds the 'deploy' command to the a "subparsers" object of 'argparse'.

    Args:
        toolname: Name of the tool to add the 'deploy' command for.
        subparsers: The argparse "subparsers" object to add the 'deploy' command to.
        func: The 'deploy' command handling function.
        argcomplete: Optional 'argcomplete' command-line arguments completer object.

    Returns:
        The argparse parser for the 'deploy' command.
    """

    text = f"Deploy {toolname} helpers."
    descr = f"""Deploy {toolname} helpers to a remote SUT (System Under Test)."""
    parser = subparsers.add_parser("deploy", help=text, description=descr)

    text = f"""When '{toolname}' is deployed, a random temporary directory is used. Use this option
               provide a custom path instead. It will be used as a temporary directory on both
               local and remote hosts. This option is meant for debugging purposes."""
    arg = parser.add_argument("--tmpdir-path", help=text)
    if argcomplete:
        arg.completer = argcomplete.completers.DirectoriesCompleter()

    text = f"""Do not remove the temporary directories created while deploying '{toolname}'. This
               option is meant for debugging purposes."""
    parser.add_argument("--keep-tmpdir", action="store_true", help=text)

    ArgParse.add_ssh_options(parser)

    parser.set_defaults(func=func)
    return parser

class DeployCheck(DeployBase.DeployCheckBase):
    """
    Provide API for verifying that all the required deployables are in place and up-to-date.
    """

    def __init__(self,
                 prjname: str,
                 toolname: str,
                 deploy_info: DeployInfoType,
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

        super().__init__(prjname, toolname, deploy_info, pman=pman)

    def _check_deployment(self):
        """
        Checks if all the required installables have been deployed and are up-to-date.

        Raises:
            ErrorNotFound: If the source path or deployable path is not found.
        """

        for pyhelper in self._cats["pyhelpers"]:
            try:
                subpath = DeployHelpersBase.HELPERS_SRC_SUBDIR / pyhelper
                what = f"the '{pyhelper}' python helper program"
                srcpath = ProjectFiles.find_project_data("stats-collect", subpath, what=what)
            except ErrorNotFound:
                continue

            for installable, inst_info in self._cats["pyhelpers"].items():
                for deployable in inst_info["deployables"]:
                    try:
                        deployable_path = self._get_installed_deployable_path(deployable)
                    except ErrorNotFound:
                        self._deployable_not_found(installable, deployable)
                        break

                    if srcpath:
                        self._check_deployable_up_to_date(installable, deployable, srcpath,
                                                          deployable_path)

class Deploy(DeployBase.DeployBase):
    """Provide the API for deploying the installables of tools in the 'stats-collect' project."""

    def __init__(self,
                 toolname: str,
                 deploy_info: DeployInfoType,
                 pman: ProcessManagerType | None = None,
                 tmpdir_path: Path | None = None,
                 keep_tmpdir: bool = False,
                 debug: bool = False):
        """
        Initialize class instance.

        Args:
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

        Refer to 'DeployBase' class constructor docstring for more information.
        """

        super().__init__("stats-collect", toolname, deploy_info, pman=pman, tmpdir_path=tmpdir_path,
                         keep_tmpdir=keep_tmpdir, debug=debug)

        # Python helpers need to be deployed only to a remote host. The local host should already
        # have them:
        #   * either deployed via 'setup.py'.
        #   * or if running from source code, present in the source code.
        if not self._spman.is_remote:
            for installable in self._cats["pyhelpers"]:
                del self._insts[installable]
            self._cats["pyhelpers"] = {}

    def _deploy(self):
        """Deploy python helpers to the SUT."""

        stmpdir = self._get_stmpdir()
        btmpdir = self._get_btmpdir()
        ctmpdir = self._get_ctmpdir()

        with _DeployPyHelpers.DeployPyHelpers("stats-collect", self._toolname,
                                              self._spman, self._bpman, stmpdir,
                                              btmpdir, cpman=self._cpman, ctmpdir=ctmpdir,
                                              debug=self._debug) as depl:
            depl.deploy(self._cats["pyhelpers"])

    def deploy(self):
        """Deploy all the installables to the SUT."""

        if not self._cats["pyhelpers"]:
            _LOG.info("Nothing to deploy to %s.", self._spman.hostname)
            return

        try:
            self._deploy()
        finally:
            self._remove_tmpdirs()
