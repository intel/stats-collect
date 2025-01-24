# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Tests for the 'InterruptsParser' module."""

from pathlib import Path

from statscollectlibs.dfbuilders import _InterruptsDFBuilder
from statscollectlibs.rawresultlibs.RORawResult import RORawResult

_TEST_RESULTS_DIR = Path("tests/data/test_module_InterruptsDFBuilder/results/")

def _is_valid_cpu_scope(scope) -> bool:
    """
    Check if the given scope is a valid CPU scope.

    Args:
        scope: The scope to check.

    Returns:
        True if the scope is a valid CPU scope, False otherwise.
    """

    if not scope.startswith("CPU"):
        return False

    try:
        int(scope[3:])
    except ValueError:
        return False

    return True

def test_good_results():
    """
    Test the 'InterruptsDFBuilder' module with well-formatted raw interrupt statistics files.
    """

    for dirpath in _TEST_RESULTS_DIR.iterdir():
        res = RORawResult(dirpath)

        cpunum = res.info.get("cpunum")
        dfbldr = _InterruptsDFBuilder.InterruptsDFBuilder(cpunum=cpunum)

        pfx = f"DataFrame for '{dirpath}'"
        df = res.load_stat("interrupts", dfbldr)

        # The test results in '_TEST_RESULTS_DIR' are crafted to have only 2 datapoints. The
        # dataframe builder should drop the first row, leaving only 1 datapoint.
        assert len(df) == 1, f"{pfx}: Expected 1 datapoint, but got {len(df)}"

        assert "Timestamp" in df.columns, f"{pfx}: Expected 'Timestamp' column"
        assert "TimeElapsed" in df.columns, f"{pfx}: Expected 'TimeElapsed' column"

        # The test results in '_TEST_RESULTS_DIR' are crafted to have many "LOC" interrupts, check
        # the corresponding column names.
        scopes = ["System"]
        if cpunum is not None:
            scopes.append(f"CPU{cpunum}")

        for scope in scopes:
            colname = f"{scope}-LOC"
            assert colname in df.columns, f"{pfx}: Expected '{colname}' column"

        # Ensure that column names are unique.
        assert len(df.columns) == len(set(df.columns)), f"{pfx}: Column names are not unique"

        # Ensure that column names follow the "Scope-Metric" format, check scope names.
        time_colnames = ["Timestamp", "TimeElapsed"]
        for colname in df.columns:
            if colname in time_colnames:
                continue

            split = colname.split("-", 1)
            assert len(split) == 2, \
                   f"{pfx}: Column name '{colname}' does not follow the 'Scope-Metric' format"

            scope = split[0]
            if scope != "System" and not _is_valid_cpu_scope(scope):
                assert False, f"{pfx}: Invalid scope '{scope}' in column name '{colname}'"

        # Ensure that interrupt count metrics have corresponding interrupt rate metrics.
        for colname in df.columns:
            if colname in time_colnames:
                continue
            if colname.endswith("_rate"):
                continue

            rate_colname = f"{colname}_rate"
            assert rate_colname in df.columns, \
                    f"{pfx}: Missing interrupt rate column '{rate_colname}' for '{colname}'"
