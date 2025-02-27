# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""This module includes the "start" 'stats-collect' command implementation."""

import contextlib
from pathlib import Path
from pepclibs import CPUInfo
from pepclibs.helperlibs import Logging, Trivial, Human, LocalProcessManager
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import _Common
from statscollectlibs import Runner
from statscollectlibs.collector import StatsCollectBuilder
from statscollectlibs.deploylibs import _Deploy
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.rawresultlibs import RORawResult, WORawResult
from statscollectlibs.htmlreport import _StatsCollectHTMLReport

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

def generate_reportid(args, pman):
    """
    If user provided report ID for the 'start' command, this function validates it and returns.
    Otherwise, it generates the default report ID and returns it.
    """

    if not args.reportid and pman.is_remote:
        prefix = pman.hostname
    else:
        prefix = None

    return ReportID.format_reportid(prefix=prefix, reportid=args.reportid,
                                    strftime=f"{args.toolname}-%Y%m%d")

def start_command(args):
    """Implements the 'start' command."""

    if args.list_stats:
        from statscollectlibs.collector import StatsCollect #pylint: disable=import-outside-toplevel
        StatsCollect.list_stats()
        return

    with contextlib.ExitStack() as stack:
        pman = _Common.get_pman(args)
        stack.enter_context(pman)

        if args.tlimit:
            if Trivial.is_num(args.tlimit):
                args.tlimit = f"{args.tlimit}m"
            args.tlimit = Human.parse_human(args.tlimit, unit="s", integer=True, name="time limit")

        args.reportid = generate_reportid(args, pman)

        if not args.outdir:
            args.outdir = Path(f"./{args.reportid}")

        if args.cpunum is not None:
            cpuinfo = CPUInfo.CPUInfo(pman=pman)
            stack.enter_context(cpuinfo)
            args.cpunum = cpuinfo.normalize_cpu(args.cpunum)

        with _Deploy.DeployCheck("stats-collect", args.toolname, args.deploy_info,
                                 pman=pman) as depl:
            depl.check_deployment()

        res = WORawResult.WORawResult(args.reportid, args.outdir, cmd=args.cmd, cpunum=args.cpunum)
        stack.enter_context(res)

        if not args.stats or args.stats == "none":
            args.stats = None
            stcoll = None
            _LOG.warning("no statistics will be collected")
        else:
            stcoll_builder = StatsCollectBuilder.StatsCollectBuilder()
            stack.enter_context(stcoll_builder)

            stcoll_builder.parse_stnames(args.stats)
            if args.stats_intervals:
                stcoll_builder.parse_intervals(args.stats_intervals)

            stcoll = stcoll_builder.build_stcoll(pman, res, local_outdir=args.outdir)
            if not stcoll:
                raise Error("no statistics discovered. Use '--stats=none' to explicitly "
                            "run the tool without statistics collection.")

            if stcoll:
                stack.enter_context(stcoll)

        _Common.configure_log_file(res.logs_path, args.toolname)

        if not args.cmd_local:
            cmd_pman = pman
        else:
            cmd_pman = LocalProcessManager.LocalProcessManager()
            stack.enter_context(cmd_pman)

        runner = Runner.Runner(res, cmd_pman, stcoll)
        stack.enter_context(runner)

        runner.run(args.cmd, args.tlimit)

    if args.report:
        ro_res = RORawResult.RORawResult(res.dirpath, res.reportid)
        rep = _StatsCollectHTMLReport.StatsCollectHTMLReport([ro_res], args.outdir / "html-report")
        rep.copy_raw = False
        rep.generate()
