# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the API for deploying the installables of tools in the 'stats-collect' project."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import sys
import types
import typing
from pathlib import Path

try:
    argcomplete: types.ModuleType | None
    import argcomplete
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    argcomplete = None

from pepclibs.helperlibs import Logging, ArgParse
from statscollectlibs.deploy import DeployBase, _DeployPyHelpers

if typing.TYPE_CHECKING:
    from typing import Callable
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

def add_deploy_cmdline_args(toolname: str,
                            subparsers: ArgParse.SubParsersType,
                            func: Callable) -> ArgParse.ArgsParser:
    """
    Adds the 'deploy' command to a "subparsers" object of 'argparse'.

    Args:
        toolname: Name of the tool to add the 'deploy' command for.
        subparsers: The argparse "subparsers" object to add the 'deploy' command to.
        func: The 'deploy' command handling function.

    Returns:
        The argparse parser for the 'deploy' command.
    """

    if argcomplete is not None:
        completer = getattr(getattr(argcomplete, "completers"), "DirectoriesCompleter")()
    else:
        completer = None

    text = f"Deploy {toolname} helpers."
    descr = f"""Deploy {toolname} helpers to a remote SUT (System Under Test)."""
    parser = subparsers.add_parser("deploy", help=text, description=descr)

    text = f"""When '{toolname}' is deployed, a random temporary directory is used. Use this option
               provide a custom path instead. It will be used as a temporary directory on both
               local and remote hosts. This option is meant for debugging purposes."""
    parser.add_argument("--tmpdir-path",
                        help=text).completer = completer # type: ignore[attr-defined]

    text = f"""Do not remove the temporary directories created while deploying '{toolname}'. This
               option is meant for debugging purposes."""
    parser.add_argument("--keep-tmpdir", action="store_true", help=text)

    ArgParse.add_ssh_options(parser)

    parser.set_defaults(func=func)
    return parser

class Deploy(DeployBase.DeployBase):
    """Provide the API for deploying the installables of tools in the 'stats-collect' project."""

    def __init__(self,
                 toolname: str,
                 deploy_info: DeployInfoTypedDict,
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
            tmpdir_path: Path to use as a temporary directory (a random temporary directory is
                         created by default).
            keep_tmpdir: If 'False', remove the temporary directory when finished. If 'True', do not
                         remove it.
            debug: If 'True', be more verbose.

        Refer to 'DeployBase' class constructor docstring for more information.
        """

        super().__init__("stats-collect", toolname, deploy_info, pman=pman, lbuild=True,
                         tmpdir_path=tmpdir_path, keep_tmpdir=keep_tmpdir, debug=debug)

        # Python helpers need to be deployed only to a remote host. The local host should already
        # have them:
        #   * either deployed via 'setup.py'.
        #   * or if running from source code, present in the source code.
        if not self._spman.is_remote:
            for installable in self._cats["pyhelpers"]:
                del self._insts[installable]
            self._cats["pyhelpers"] = {}

    def _deploy(self):
        """Deploy Python helpers to the SUT."""

        stmpdir = self._get_stmpdir()
        btmpdir = self._get_btmpdir()
        ctmpdir = self._get_ctmpdir()

        with _DeployPyHelpers.DeployPyHelpers("stats-collect", self._toolname,
                                              spman=self._spman, bpman=self._bpman,
                                              stmpdir=stmpdir, btmpdir=btmpdir,
                                              cpman=self._cpman, ctmpdir=ctmpdir,
                                              debug=self._debug) as depl:
            # The base directory of python helpers is the same as the directory containing the
            # running script.
            insts_basedir = Path(sys.argv[0]).absolute().parent
            depl.deploy(self._cats["pyhelpers"], insts_basedir=insts_basedir)

    def deploy(self):
        """Deploy all the installables to the SUT."""

        if not self._cats["pyhelpers"]:
            _LOG.info("Nothing to deploy to %s.", self._spman.hostname)
            return

        try:
            self._deploy()
        finally:
            self._remove_tmpdirs()
