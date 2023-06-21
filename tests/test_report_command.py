# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module contains the tests for the 'stats-collect report' command."""

from pepclibs.helperlibs import Exceptions
import common

def test_all_stats(tmpdir, data_path):
    """Test 'report' command for good input data with all statistics."""

    good_data_path = data_path / "good" / "all-stats"
    args = f"report -o {tmpdir} {good_data_path}"
    common.run_stats_collect(args)

def test_only_sysinfo(tmpdir, data_path):
    """Test 'report' command for good input data with only 'SysInfo' statistics."""

    good_data_path = data_path / "good" / "sysinfo"
    args = f"report -o {tmpdir} {good_data_path}"
    common.run_stats_collect(args)

def test_bad_ac_power_file(tmpdir, data_path):
    """
    Test that a badly-formatted 'Ac Power' raw statistics file does not cause 'stats-collect report'
    to crash.
    """

    data_path = data_path / "bad" / "bad-ac-power-file"
    args = f"report -o {tmpdir} {data_path}"
    common.run_stats_collect(args)

def test_missing_info_file(tmpdir, data_path):
    """
    Test 'report' command for a bad dataset which does not contain the required 'info.yml' file.
    """

    data_path = data_path / "bad" / "missing-info-file"
    args = f"report -o {tmpdir} {data_path}"
    common.run_stats_collect(args, Exceptions.Error)
