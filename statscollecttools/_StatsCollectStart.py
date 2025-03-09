# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""This module includes the "start" 'stats-collect' command implementation."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import contextlib
import argparse
from pathlib import Path
from typing import NamedTuple
from pepclibs import CPUInfo
from pepclibs.helperlibs import Logging, Trivial, Human, LocalProcessManager
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import _Common, ToolInfo
from statscollectlibs import Runner
from statscollectlibs.collector import StatsCollectBuilder, StatsCollect
from statscollectlibs.deploylibs import _Deploy
from statscollectlibs.deploylibs.DeployBase import DeployInfoType
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.rawresultlibs import RORawResult, WORawResult
from statscollectlibs.htmlreport import _StatsCollectHTMLReport

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class _StartCommandArgsType(NamedTuple):
    """The "stats-collect start" command-line arguments named tuple type."""

    username: str
    hostname: str
    privkey: Path | None
    timeout: int
    cpus: str | None
    tlimit: float | None
    outdir: Path
    reportid: str
    stats: str | None
    list_stats: bool
    stats_intervals: str | None
    report: bool
    cmd_local: bool
    cmd: str

def _format_args(arguments: argparse.Namespace) -> _StartCommandArgsType:
    """
    Validate and format the 'stats-collect start' tool input command-line arguments, then build and
    return the arguments named tuple object.

    Args:
        arguments: The input arguments parsed from the command line.

    Returns:
        _StartCommandArgsType: A named tuple containing the formatted arguments.

    Notes:
        - If the 'tlimit' argument does not have the unit, assum milliseconds.
        - The 'outdir' argument defaults to a directory named after the 'reportid' if not provided.
    """

    # Format the 'tlimit' argument.
    if arguments.tlimit:
        tlimit_str = str(arguments.tlimit)
        if Trivial.is_num(tlimit_str):
            tlimit_str = f"{tlimit_str}m"
        tlimit = Human.parse_human(tlimit_str, unit="s", integer=False, what="time limit")
    else:
        tlimit = None

    hostname = arguments.hostname

    if arguments.privkey:
        privkey = Path(arguments.privkey)
    else:
        privkey = None

    reportid = arguments.reportid

    if not reportid and hostname != "localhost":
        prefix = hostname
    else:
        prefix = None
    reportid = ReportID.format_reportid(prefix=prefix, reportid=reportid,
                                        strftime=f"{ToolInfo.TOOLNAME}-%Y%m%d")

    if arguments.outdir:
        outdir = Path(arguments.outdir)
    else:
        outdir = Path(f"./{reportid}")

    return _StartCommandArgsType(
        username = arguments.username,
        hostname = hostname,
        privkey = privkey,
        timeout = arguments.timeout,
        cpus = arguments.cpus,
        tlimit = tlimit,
        outdir = outdir,
        reportid = reportid,
        stats = arguments.stats,
        list_stats = arguments.list_stats,
        stats_intervals = arguments.stats_intervals,
        report = arguments.report,
        cmd_local = arguments.cmd_local,
        cmd = " ".join(arguments.cmd)
    )

def _substitute_cmd_placeholders(args: _StartCommandArgsType,
                                 cpus: list[int] | None,
                                 stcoll: StatsCollect.StatsCollect | None) -> str:
    """
    Substitute placeholders in 'args.cmd' with the actual values and return the result.

    Args:
        args: The command-line arguments.
        cpus: A list of CPU IDs to be included in the command.
        stcoll: A 'StatsCollect' that is going to be used for collecting the statistics (to get the
                list of statistics names).

    Returns:
        str: The command string with placeholders replaced by actual values.
    """

    if args.privkey:
        privkey = str(args.privkey)
    else:
        privkey = "none"

    if not cpus:
        cpus_str = "none"
    else:
        cpus_str = ",".join(str(cpu) for cpu in cpus)

    if not stcoll:
        stnames = "none"
    else:
        stnames = stcoll.get_enabled_stats()

    cmd = args.cmd
    cmd = cmd.replace("{HOSTNAME}", args.hostname)
    cmd = cmd.replace("{USERNAME}", args.username)
    cmd = cmd.replace("{PRIVKEY}", privkey)
    cmd = cmd.replace("{TIMEOUT}", str(args.timeout))
    cmd = cmd.replace("{CPUS}", cpus_str)
    cmd = cmd.replace("{OUTDIR}", str(args.outdir))
    cmd = cmd.replace("{REPORTID}", args.reportid)
    cmd = cmd.replace("{STATS}", ",".join(stnames))

    return cmd

def start_command(arguments: argparse.Namespace, deploy_info: DeployInfoType):
    """
    Implement the 'stats-collect start' command.

    Args:
        arguments: The command-line arguments passed to the 'start' command.
        deploy_info: The 'stats-collect' tool deployment information, used for checking the
                     deployment status.
    """

    args = _format_args(arguments)

    with contextlib.ExitStack() as stack:
        pman = _Common.get_pman(args)
        stack.enter_context(pman)

        if args.cpus is not None:
            cpuinfo = CPUInfo.CPUInfo(pman=pman)
            stack.enter_context(cpuinfo)
            cpus = Trivial.split_csv_line_int(args.cpus, what="--cpus argument")
            cpus = cpuinfo.normalize_cpus(cpus)
        else:
            cpus = None

        with _Deploy.DeployCheck("stats-collect", ToolInfo.TOOLNAME, deploy_info,
                                 pman=pman) as depl:
            depl.check_deployment()

        res = WORawResult.WORawResult(args.reportid, args.outdir, cpus=cpus)
        stack.enter_context(res)

        if not args.stats or args.stats == "none":
            stcoll = None
            _LOG.warning("No statistics will be collected")
        else:
            stcoll_builder = StatsCollectBuilder.StatsCollectBuilder()
            stack.enter_context(stcoll_builder)

            stcoll_builder.parse_stnames(args.stats)
            if args.stats_intervals:
                stcoll_builder.parse_intervals(args.stats_intervals)

            stcoll = stcoll_builder.build_stcoll(pman, res, local_outdir=args.outdir)
            if not stcoll:
                raise Error("No statistics discovered. Use '--stats=none' to explicitly "
                            "run the tool without statistics collection.")

            if stcoll:
                stack.enter_context(stcoll)

        _Common.configure_log_file(res.logs_path, ToolInfo.TOOLNAME)

        if not args.cmd_local:
            cmd_pman = pman
        else:
            cmd_pman = LocalProcessManager.LocalProcessManager()
            stack.enter_context(cmd_pman)

        runner = Runner.Runner(res, cmd_pman, stcoll)
        stack.enter_context(runner)

        cmd = _substitute_cmd_placeholders(args, cpus, stcoll)

        runner.run(cmd, args.tlimit)

    if args.report:
        ro_res = RORawResult.RORawResult(res.dirpath, res.reportid)
        rep = _StatsCollectHTMLReport.StatsCollectHTMLReport([ro_res], args.outdir / "html-report")
        rep.copy_raw = False
        rep.generate()
