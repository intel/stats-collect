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

import argparse
from pathlib import Path
from typing import NamedTuple
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.rawresultlibs import RORawResult
from statscollectlibs.htmlreport import _StatsCollectHTMLReport
from statscollecttools import ToolInfo, _Common

class _ReportCommandArgsType(NamedTuple):
    """The "stats-collect report" command-line arguments named tuple type."""

    outdir: Path
    reportids: list[str]
    copy_raw: bool
    respaths: list[Path]
    cpus: list[int] | None

def _open_raw_results(args: _ReportCommandArgsType) -> list[RORawResult.RORawResult]:
    """
    Open the input raw test results and return a list of 'RORawResult' objects.

    Args:
        args: The command-line arguments.

    Returns:
        list[RORawResult.RORawResult]: List of 'RORawResult' objects.
    """

    rids = list(args.reportids)

    # Append the required amount of empty strings to make the 'rids' list be of the same length as #
    # the 'respaths' list.
    rids += [""] * (len(args.respaths) - len(rids))

    rsts = []
    for respath, reportid in zip(args.respaths, rids):
        if reportid:
            ReportID.validate_reportid(reportid)

        res = RORawResult.RORawResult(respath, reportid=reportid)
        if ToolInfo.TOOLNAME != res.info["toolname"]:
            raise Error(f"Cannot generate '{ToolInfo.TOOLNAME}' report, results are collected with "
                        f"'{res.info['toolname']}':\n{respath}")
        if args.cpus:
            res.info["cpus"] = args.cpus

        rsts.append(res)

    return rsts

def _format_args(arguments: argparse.Namespace) -> _ReportCommandArgsType:
    """
    Validate and format the 'stats-collect report' tool input command-line arguments, then build and
    return the arguments named tuple object.

    Args:
        arguments: The input arguments parsed from the command line.

    Returns:
        _ReportCommandArgsType: A named tuple containing the formatted arguments.
    """

    if len(arguments.respaths) == 0:
        # This should have been ensured by the command line parser.
        raise Error("BUG: no raw results paths provided")

    if not arguments.outdir:
        outdir = arguments.respaths[0] / "html-report"
    else:
        outdir = arguments.outdir

    reportids: list[str] = []
    if arguments.reportids:
        reportids = Trivial.split_csv_line(arguments.reportids)

    respaths: list[Path] = []
    if arguments.respaths:
        respaths = arguments.respaths

    if len(reportids) > len(respaths):
        raise Error(f"There are {len(reportids)} report IDs to assign to {len(respaths)} input "
                    f"test results. Please, provide {len(respaths)} or fewer report IDs.")

    cpus: list[int] | None = []
    if arguments.cpus:
        cpus = Trivial.split_csv_line_int(arguments.cpus, what="--cpus argument")

    return _ReportCommandArgsType(
        outdir = outdir,
        reportids = reportids,
        copy_raw = arguments.copy_raw,
        respaths = respaths,
        cpus = cpus,
    )

def report_command(arguments):
    """
    Implements the 'report' command.

    Args:
        arguments: The command-line arguments.
    """

    args = _format_args(arguments)

    rsts = _open_raw_results(args)

    logpath = _Common.configure_log_file(args.outdir, ToolInfo.TOOLNAME)
    logpath = Path(logpath).relative_to(args.outdir)

    rep = _StatsCollectHTMLReport.StatsCollectHTMLReport(rsts, args.outdir, logpath=logpath)
    rep.copy_raw = args.copy_raw
    rep.generate()
