# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""The 'stats-collect deploy' command implementation."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
from pepclibs.helperlibs import ProcessManager
from statscollecttools import ToolInfo
from statscollectlibs.deploy import _Deploy

if typing.TYPE_CHECKING:
    from typing import TypedDict
    import argparse

    class _DeployCmdlArgsTypedDict(TypedDict, total=False):
        """
        Typed dictionary for the "stats-collect deploy" command-line arguments.

        Args:
            hostname: The host name to create a process manager object for.
            username: The user name for logging into the host over SSH. Only used for remote hosts.
            privkey: Path to the private key file for logging into the host over SSH. Only used for
                     remote hosts.
            timeout: The SSH connection timeout in seconds.
            tmpdir_path: Path to the temporary directory to use instead of a random one.
            keep_tmpdir: Whether to keep the temporary directory after the deployment is done.
            debug: Whether to enable debug output.
        """

        hostname: str
        username: str
        privkey: Path | None
        timeout: int | float
        tmpdir_path: Path | None
        keep_tmpdir: bool
        debug: bool

def _format_args(args: argparse.Namespace) -> _DeployCmdlArgsTypedDict:
    """
    Validate and format the 'stats-collect deploy' tool input command-line arguments, then build and
    return the arguments typed dictionary.

    Args:
        args: The input arguments parsed from the command line.

    Returns:
        _DeployCommandArgsTypedDict: A typed dictionary containing the formatted arguments.
    """

    cmdl: _DeployCmdlArgsTypedDict = {}

    cmdl["hostname"] = args.hostname
    cmdl["username"] = args.username if args.username else "root"
    cmdl["privkey"] = args.privkey
    cmdl["timeout"] = args.timeout if args.timeout else 8
    cmdl["tmpdir_path"] = args.tmpdir_path
    cmdl["keep_tmpdir"] = args.keep_tmpdir
    cmdl["debug"] = args.debug
    return cmdl

def deploy_command(args, deploy_info):
    """Implements the 'deploy' command."""

    cmdl = _format_args(args)

    with ProcessManager.get_pman(cmdl["hostname"], username=cmdl["username"],
                                 privkeypath=cmdl["privkey"], timeout=cmdl["timeout"]) as pman:
        with _Deploy.Deploy(ToolInfo.TOOLNAME, deploy_info, pman, cmdl["tmpdir_path"],
                            cmdl["keep_tmpdir"], cmdl["debug"]) as depl:
            depl.deploy()
