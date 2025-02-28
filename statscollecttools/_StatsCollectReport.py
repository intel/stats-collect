# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
The 'stats-collect report' command implementation.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.rawresultlibs import RORawResult
from statscollectlibs.htmlreport import _StatsCollectHTMLReport
from statscollecttools import ToolInfo, _Common

def open_raw_results(respaths: list[Path],
                     reportids: str | None = None,
                     cpus: str | None = None) -> list[RORawResult.RORawResult]:
    """
    Open the input raw test results and return a list of 'RORawResult' objects.

    Args:
        respaths: List of paths to raw results.
        reportids: Comma-separated list of report IDs to override report IDs in raw results.
        cpus: Comma-separated list of CPU numbers to include in the report.

    Returns:
        list[RORawResult.RORawResult]: List of 'RORawResult' objects.
    """

    if reportids:
        rids = Trivial.split_csv_line(reportids)
    else:
        rids = []

    if len(rids) > len(respaths):
        raise Error(f"There are {len(rids)} report IDs to assign to {len(respaths)} input "
                    f"test results. Please, provide {len(respaths)} or fewer report IDs.")

    if cpus:
        cpus = Trivial.split_csv_line_int(cpus, what="--cpus argument")

    # Append the required amount of 'None's to make the 'rids' list be of the same length as
    # the 'respaths' list.
    rids += [None] * (len(respaths) - len(rids))

    rsts = []
    for respath, reportid in zip(respaths, rids):
        if reportid:
            ReportID.validate_reportid(reportid)

        res = RORawResult.RORawResult(respath, reportid=reportid)
        if ToolInfo.TOOLNAME != res.info["toolname"]:
            raise Error(f"Cannot generate '{ToolInfo.TOOLNAME}' report, results are collected with "
                        f"'{res.info['toolname']}':\n{respath}")
        if cpus:
            res.info["cpus"] = cpus
        rsts.append(res)

    return rsts

def report_command(args):
    """
    Implements the 'report' command.

    Args:
        args: The command-line arguments.
    """

    rsts = open_raw_results(args.respaths, reportids=args.reportids, cpus=args.cpus)

    if not args.outdir:
        args.outdir = args.respaths[0] / "html-report"

    logpath = _Common.configure_log_file(args.outdir, ToolInfo.TOOLNAME)
    logpath = Path(logpath).relative_to(args.outdir)

    rep = _StatsCollectHTMLReport.StatsCollectHTMLReport(rsts, args.outdir, logpath=logpath)
    rep.copy_raw = args.copy_raw
    rep.generate()
