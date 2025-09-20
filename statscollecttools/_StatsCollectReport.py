# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
Implement the 'stats-collect report' command.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.result import RORawResult
from statscollectlibs.htmlreport import _StatsCollectHTMLReport
from statscollecttools import ToolInfo, _Common

if typing.TYPE_CHECKING:
    import argparse
    from typing import TypedDict

    class _ReportCmdlArgsTypedDict(TypedDict, total=False):
        """
        Typed dictionary for the "stats-collect start" command-line arguments.

        Attributes:
            outdir: The output directory path.
            reportids: Report IDs to assign to the raw test results.
            copy_raw: Whether to copy the raw test results to the HTML report directory.
            respaths: Paths to the raw test results.
            cpus: CPU numbers to use for generating CPU-specific charts. By default, use CPUs
                  numbers found in the raw test results.
        """

        outdir: Path
        reportids: list[str]
        copy_raw: bool
        respaths: list[Path]
        cpus: list[int] | None

def _open_raw_results(cmdl: _ReportCmdlArgsTypedDict) -> list[RORawResult.RORawResult]:
    """
    Open the raw test results and return a list of 'RORawResult' objects.

    Args:
        cmdl: The command-line arguments.

    Returns:
        list[RORawResult.RORawResult]: List of 'RORawResult' objects.
    """

    rids = list(cmdl["reportids"])

    # Append the required amount of empty strings to make the 'rids' list be of the same length as #
    # the 'respaths' list.
    rids += [""] * (len(cmdl["respaths"]) - len(rids))

    rsts = []
    for respath, reportid in zip(cmdl["respaths"], rids):
        if reportid:
            ReportID.validate_reportid(reportid)

        res = RORawResult.RORawResult(respath, reportid=reportid)
        if ToolInfo.TOOLNAME != res.info["toolname"]:
            raise Error(f"Cannot generate '{ToolInfo.TOOLNAME}' report, results are collected with "
                        f"'{res.info['toolname']}':\n{respath}")

        rsts.append(res)

    RORawResult.reportids_dedup(rsts)

    return rsts

def _format_args(args: argparse.Namespace) -> _ReportCmdlArgsTypedDict:
    """
    Validate and format the 'stats-collect report' tool input command-line arguments, then build and
    return the arguments named tuple object.

    Args:
        args: The command-line arguments.

    Returns:
        _ReportCmdlTypedDict: A typed dictionary containing the formatted arguments.
    """

    if len(args.respaths) == 0:
        # This should have been ensured by the command line parser.
        raise Error("BUG: no raw results paths provided")

    if not args.outdir:
        outdir = args.respaths[0] / "html-report"
    else:
        outdir = args.outdir

    reportids: list[str] = []
    if args.reportids:
        reportids = Trivial.split_csv_line(args.reportids)

    respaths: list[Path] = []
    if args.respaths:
        respaths = args.respaths

    if len(reportids) > len(respaths):
        raise Error(f"There are {len(reportids)} report IDs to assign to {len(respaths)} raw "
                    f"test results. Please, provide {len(respaths)} or fewer report IDs.")

    cpus: list[int] | None = []
    if args.cpus:
        cpus = Trivial.split_csv_line_int(args.cpus, what="--cpus argument")

    cmdl: _ReportCmdlArgsTypedDict = {}
    cmdl["outdir"] = outdir
    cmdl["reportids"] = reportids
    cmdl["copy_raw"] = args.copy_raw
    cmdl["respaths"] = respaths
    cmdl["cpus"] = cpus
    return cmdl

def report_command(args: argparse.Namespace):
    """
    Implements the 'report' command.

    Args:
        args: The command-line arguments.
    """

    cmdl = _format_args(args)

    rsts = _open_raw_results(cmdl)

    logpath = _Common.configure_log_file(cmdl["outdir"], ToolInfo.TOOLNAME)
    logpath = Path(logpath).relative_to(cmdl["outdir"])

    rep = _StatsCollectHTMLReport.StatsCollectHTMLReport(rsts, cmdl["outdir"], cpus=cmdl["cpus"],
                                                         logpath=logpath)
    rep.copy_raw = cmdl["copy_raw"]
    rep.generate()
