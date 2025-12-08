# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Implement the 'stats-collect deploy' command.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
from pepclibs.helperlibs import ProcessManager, ArgParse
from statscollecttools import ToolInfo
from statscollectlibs.deploy import _Deploy

if typing.TYPE_CHECKING:
    import argparse
    from typing import cast
    from pepclibs.helperlibs.ArgParse import CommonArgsTypedDict, SSHArgsTypedDict
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict

    class _DeployCmdlArgsTypedDict(CommonArgsTypedDict, SSHArgsTypedDict, total=False):
        """
        Typed dictionary for the "stats-collect deploy" command-line arguments.

        Attributes:
            (All attributes from 'CommonArgsTypedDict')
            (All attributes from 'SSHArgsTypedDict')
            tmpdir_path: Path to the temporary directory to use instead of a random one.
            keep_tmpdir: Whether to keep the temporary directory after the deployment is done.
            debug: Whether to enable debug output.
        """

        tmpdir_path: Path | None
        keep_tmpdir: bool

def _format_args(args: argparse.Namespace) -> _DeployCmdlArgsTypedDict:
    """
    Validate and format the 'stats-collect deploy' tool input command-line arguments, then build and
    return the arguments typed dictionary.

    Args:
        args: The command-line arguments.

    Returns:
        A typed dictionary containing the formatted arguments.
    """

    if typing.TYPE_CHECKING:
        cmdl1 = cast(dict, ArgParse.format_common_args(args))
        cmdl2 = cast(dict, ArgParse.format_ssh_args(args))
        # Merge the two dictionaries.
        cmdl = cast(_DeployCmdlArgsTypedDict, cmdl1 | cmdl2)
    else:
        cmdl1 = ArgParse.format_common_args(args)
        cmdl2 = ArgParse.format_ssh_args(args)
        cmdl = cmdl1 | cmdl2

    cmdl["tmpdir_path"] = Path(args.tmpdir_path) if args.tmpdir_path else None
    cmdl["keep_tmpdir"] = args.keep_tmpdir
    return cmdl

def deploy_command(args: argparse.Namespace, deploy_info: DeployInfoTypedDict):
    """
    Implement the 'stats-collect deploy' command.

    Args:
        args: The command-line arguments.
        deploy_info: The 'stats-collect' tool deployment information.
    """

    cmdl = _format_args(args)

    with ProcessManager.get_pman(cmdl["hostname"], username=cmdl["username"],
                                 privkeypath=cmdl["privkey"], timeout=cmdl["timeout"]) as pman:
        with _Deploy.Deploy(ToolInfo.TOOLNAME, deploy_info, pman, cmdl["tmpdir_path"],
                            cmdl["keep_tmpdir"], cmdl["debug"]) as depl:
            depl.deploy()
