# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
Implement the 'stats-collect start' command.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
import contextlib
from pathlib import Path
from pepclibs.helperlibs import Logging, Trivial, Human, LocalProcessManager, ProcessManager
from pepclibs.helperlibs import ArgParse
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import _Common, ToolInfo
from statscollectlibs import _Runner
from statscollectlibs.collector import StatsCollectBuilder, StatsCollect
from statscollectlibs.deploy import _Deploy
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.result import RORawResult, _WORawResult
from statscollectlibs.htmlreport import _StatsCollectHTMLReport

if typing.TYPE_CHECKING:
    import argparse
    from typing import cast
    from pepclibs.helperlibs.ArgParse import SSHArgsTypedDict
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict

    class _StartCmdlArgsTypedDict(SSHArgsTypedDict, total=False):
        """
        Typed dictionary for the "stats-collect start" command-line arguments.

        Attributes:
            (All attributes from 'SSHArgsTypedDict')
            tlimit: The time limit for the command execution in seconds.
            outdir: The output directory path.
            reportid: The report ID.
            stats: The comma-separated list of statistics to collect.
            list_stats: Whether to list the available statistics and exit.
            stats_intervals: The comma-separated list of statistics collection intervals.
            report: Whether to generate the HTML report after the command execution.
            cmd_local: Whether to run the command locally instead of on the remote host.
            pipe_path: The path to the named pipe for inter-process communication.
            pipe_timeout: The timeout for waiting for the named pipe to be opened in seconds.
            cmd: The command to execute.
        """

        tlimit: float | None
        outdir: Path
        reportid: str
        stats: str | None
        list_stats: bool
        stats_intervals: str | None
        report: bool
        cmd_local: bool
        pipe_path: Path | None
        pipe_timeout: int | float
        cmd: str

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

def _format_args(args: argparse.Namespace) -> _StartCmdlArgsTypedDict:
    """
    Validate and format the 'stats-collect start' tool input command-line arguments, then build and
    return the arguments typed dictionary.

    Args:
        args: The command-line arguments.

    Returns:
        _StartCmdlArgsTypedDict: A typed dictionary containing the formatted arguments.

    Notes:
        - If the 'tlimit' argument does not have the unit, assume milliseconds.
        - The 'outdir' argument defaults to a directory named after the 'reportid' if not provided.
    """

    if typing.TYPE_CHECKING:
        cmdl = cast(_StartCmdlArgsTypedDict, ArgParse.format_ssh_args(args))
    else:
        cmdl = ArgParse.format_ssh_args(args)

    # Format the 'tlimit' argument.
    if args.tlimit:
        tlimit_str = str(args.tlimit)
        if Trivial.is_num(tlimit_str):
            tlimit_str = f"{tlimit_str}m"
        tlimit = Human.parse_human(tlimit_str, unit="s", integer=False, what="time limit")
    else:
        tlimit = None

    reportid = args.reportid

    if not reportid and cmdl["hostname"] != "localhost":
        prefix = cmdl["hostname"]
    else:
        prefix = None
    reportid = ReportID.format_reportid(prefix=prefix, reportid=reportid,
                                        strftime=f"{ToolInfo.TOOLNAME}-%Y%m%d")

    if args.outdir:
        outdir = Path(args.outdir)
    else:
        outdir = Path(f"./{reportid}")

    if args.pipe_path:
        pipe_path = Path(args.pipe_path)
    else:
        pipe_path = None

    pipe_timeout = Human.parse_human(args.pipe_timeout, unit="s", what="pipe timeout")

    cmdl["tlimit"] = tlimit
    cmdl["outdir"] = outdir
    cmdl["reportid"] = reportid
    cmdl["stats"] = args.stats
    cmdl["list_stats"] = args.list_stats
    cmdl["stats_intervals"] = args.stats_intervals
    cmdl["report"] = args.report
    cmdl["cmd_local"] = args.cmd_local
    cmdl["pipe_path"] = pipe_path
    cmdl["pipe_timeout"] = pipe_timeout
    cmdl["cmd"] = " ".join(args.cmd)
    return cmdl

def _substitute_cmd_placeholders(cmdl: _StartCmdlArgsTypedDict,
                                 stcoll: StatsCollect.StatsCollect | None,
                                 pipe_path: Path | None) -> str:
    """
    Substitute placeholders in 'args.cmd' with the actual values and return the result.

    Args:
        cmdl: The command-line arguments.
        stcoll: A 'StatsCollect' that is going to be used for collecting the statistics (to get the
                list of statistics names).

    Returns:
        str: The command string with placeholders replaced by actual values.
    """

    if cmdl["privkey"]:
        privkey_str = str(cmdl["privkey"])
    else:
        privkey_str = "none"

    if not stcoll:
        stnames_str = "none"
    else:
        stnames_str = stcoll.get_enabled_stats()

    if pipe_path:
        pipe_path_str = str(pipe_path)
    else:
        pipe_path_str = "none"

    cmd = cmdl["cmd"]
    cmd = cmd.replace("{HOSTNAME}", cmdl["hostname"])
    cmd = cmd.replace("{USERNAME}", cmdl["username"])
    cmd = cmd.replace("{PRIVKEY}", privkey_str)
    cmd = cmd.replace("{TIMEOUT}", str(cmdl["timeout"]))
    cmd = cmd.replace("{OUTDIR}", str(cmdl["outdir"]))
    cmd = cmd.replace("{REPORTID}", cmdl["reportid"])
    cmd = cmd.replace("{STATS}", ",".join(stnames_str))
    cmd = cmd.replace("{PIPE_PATH}", pipe_path_str)

    return cmd

class _NamedPipe:
    """
    A class representing a named pipe. Enacpsulates the named pipe creation and removal, depending
    on the user input.

    Use the user-provided named pipe path or create a unique temporary named pipe if necessary. In
    the latter case, delete the temporary named pipe when exiting the context.
    """

    def __init__(self, pipe_path: Path, pman: ProcessManagerType):
        """
        Initialize the class instance.

        Args:
            pipe_path: The path to the named pipe file.
            pman: The process manager instance.
        """

        self.pipe_path = pipe_path
        self._pman = pman

        self._tmpdir: Path | None = None
        self._ran_mkfifo = False

    def __enter__(self):
        """Create a uniqu named pipe if necessary."""

        if self.pipe_path == Path("auto"):
            self._tmpdir = self._pman.mkdtemp(prefix="stats-collect-pipe-dir")

            self.pipe_path = self._tmpdir / "pipe"
            self._pman.mkfifo(self.pipe_path)
        elif not self._pman.exists(self.pipe_path):
            self._pman.mkfifo(self.pipe_path)
            self._ran_mkfifo = True

        return self

    def __exit__(self, *_):
        """Delete the named pipe if it was created when entering the context."""

        if self._tmpdir:
            self._pman.rmtree(self._tmpdir)
        elif self._ran_mkfifo:
            self._pman.unlink(self.pipe_path)

def start_command(args: argparse.Namespace, deploy_info: DeployInfoTypedDict):
    """
    Implement the 'stats-collect start' command.

    Args:
        args: The command-line arguments.
        deploy_info: The 'stats-collect' tool deployment information, used for checking the
                     deployment status.
    """

    cmdl = _format_args(args)

    with contextlib.ExitStack() as stack:
        pman = ProcessManager.get_pman(cmdl["hostname"], username=cmdl["username"],
                                       privkeypath=cmdl["privkey"], timeout=cmdl["timeout"])
        stack.enter_context(pman)

        with _Deploy.DeployCheck("stats-collect", ToolInfo.TOOLNAME, deploy_info,
                                 pman=pman) as depl:
            depl.check_deployment()

        res = _WORawResult.WORawResult(cmdl["reportid"], cmdl["outdir"])
        stack.enter_context(res)

        if not cmdl["stats"] or cmdl["stats"] == "none":
            stcoll = None
            _LOG.warning("No statistics will be collected")
        else:
            stcoll_builder = StatsCollectBuilder.StatsCollectBuilder()
            stack.enter_context(stcoll_builder)

            stcoll_builder.parse_stnames(cmdl["stats"])
            if cmdl["stats_intervals"]:
                stcoll_builder.parse_intervals(cmdl["stats_intervals"])

            stcoll = stcoll_builder.build_stcoll(pman, res, local_outdir=cmdl["outdir"])
            if not stcoll:
                raise Error("No statistics discovered. Use '--stats=none' to explicitly "
                            "run the tool without statistics collection.")

            if stcoll:
                stack.enter_context(stcoll)

        _Common.configure_log_file(res.logs_path, ToolInfo.TOOLNAME)

        if not cmdl["cmd_local"]:
            cmd_pman = pman
        else:
            cmd_pman = LocalProcessManager.LocalProcessManager()
            stack.enter_context(cmd_pman)

        pipe_path: Path | None = None
        if cmdl["pipe_path"]:
            pipe = _NamedPipe(cmdl["pipe_path"], cmd_pman)
            stack.enter_context(pipe)
            pipe_path = pipe.pipe_path

        runner = _Runner.Runner(res, cmd_pman, stcoll, pipe_path=pipe_path,
                                pipe_timeout=cmdl["pipe_timeout"])
        stack.enter_context(runner)

        cmd = _substitute_cmd_placeholders(cmdl, stcoll, pipe_path)

        runner.run(cmd, cmdl["tlimit"])

    if cmdl["report"]:
        ro_res = RORawResult.RORawResult(res.dirpath, res.reportid)
        rep = _StatsCollectHTMLReport.StatsCollectHTMLReport([ro_res],
                                                             cmdl["outdir"] / "html-report")
        rep.copy_raw = False
        rep.generate()
