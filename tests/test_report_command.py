# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Tests for 'pepc report' command."""

from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import TestRunner
from statscollecttools import _StatsCollect
from tests import _Common

_TEST_FILES_DIR = _Common.get_test_data_base() / "results"

def test_report_command_good(tmp_path: Path):
    """
    Test the 'report' command with good input data.
    """

    results_dir = _TEST_FILES_DIR / "good"

    for resdir in results_dir.iterdir():
        outdir = tmp_path / resdir.name
        args = f"report -o {outdir} {resdir}"
        TestRunner.run_tool(_StatsCollect, "stats-collect", args)

def test_report_command_bad(tmp_path: Path):
    """
    Test the 'report' command with bad input data.
    """

    results_dir = _TEST_FILES_DIR / "bad"

    for resdir in results_dir.iterdir():
        outdir = tmp_path / resdir.name
        args = f"report -o {outdir} {resdir}"
        TestRunner.run_tool(_StatsCollect, "stats-collect", args, exp_exc=Error)
