# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Tests for 'pepc report' command."""

from pathlib import Path
import common
from pepclibs.helperlibs.Exceptions import Error

_TEST_FILES_DIR = Path("tests/data/results")

def test_report_command_good(tmp_path: Path):
    """
    Test the 'report' command with good input data.
    """

    results_dir = _TEST_FILES_DIR / "good"

    for resdir in results_dir.iterdir():
        outdir = tmp_path / resdir.name
        args = f"report -o {outdir} {resdir}"
        common.run_stats_collect(args)

def test_report_command_bad(tmp_path: Path):
    """
    Test the 'report' command with bad input data.
    """

    results_dir = _TEST_FILES_DIR / "bad"

    for resdir in results_dir.iterdir():
        outdir = tmp_path / resdir.name
        args = f"report -o {outdir} {resdir}"
        common.run_stats_collect(args, Error)
