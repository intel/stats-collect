# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Test logging-related command-line options such as '-q', '-d', and '--debug-modules'."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import re
from pathlib import Path
from tests import common
from statscollectlibs.helperlibs import TestRunner
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import _StatsCollect, ToolInfo

# Path to a test result directory used as the test vehicle for 'stats-collect report'.
_RESULT_DIR: Path = common.get_test_data_base() / "results" / "good" / "adl0"

# Debug messages use the default prefix: [timestamp] [time] [module,lineno].
# Example: "[1745987654.12] [12:34:56] [HTMLReport,226] ..."
# 're.MULTILINE' makes '^' match at the start of each line, not just at the start of the string.
_DEBUG_LINE_REGEX = re.compile(r"^\[[\d.]+\] \[[\d:]+\] \[(\w+),\d+\]", re.MULTILINE)

# ANSI color escape sequence pattern (e.g., '\x1b[32m', '\x1b[1;33m', '\x1b[0m').
_ANSI_COLOR_REGEX = re.compile(r"\x1b\[[0-9;]*m")

def _run(tmp_path: Path,
         options: str = "",
         exp_exc: type[Exception] | None = None,
         capture_output: bool = False) -> tuple[str, str]:
    """
    Run 'stats-collect report <result_dir> <options>' and return (stdout, stderr).

    Args:
        tmp_path: Temporary directory for the report output.
        options: Options to append to the command, e.g. '-d' or '-q -d'.
        exp_exc: Expected exception type. If set, the call must raise this exception.
        capture_output: Whether to capture and return stdout/stderr.

    Returns:
        A tuple of (stdout, stderr) strings.

    Notes:
        - 'report' is used as the test vehicle because it runs locally with no host or root
          access required.
        - Options are placed after the subcommand so the report subparser picks them up via the
          standard 'ArgsParser' option processing, which then validates conflicts.
    """

    cmd = f"report -o {tmp_path} {_RESULT_DIR}"
    arguments = f"{cmd} {options}" if options else cmd
    return TestRunner.run_tool(_StatsCollect, ToolInfo.TOOLNAME, arguments, pman=None,
                               exp_exc=exp_exc, capture_output=capture_output)

def test_quiet(tmp_path: Path):
    """Test that '-q' suppresses all output."""

    stdout, stderr = _run(tmp_path, "-q", capture_output=True)

    assert not stdout, "Expected no stdout output with '-q'"
    assert not stderr, "Expected no stderr output with '-q'"

def _get_debug_modules(text: str) -> set[str]:
    """
    Return the set of module names that appear in debug log lines in 'text'.

    Args:
        text: Log output text to scan for debug messages.

    Returns:
        A set of module name strings extracted from debug message prefixes.
    """

    return set(_DEBUG_LINE_REGEX.findall(text))

def test_debug(tmp_path: Path):
    """Test that '-d' produces debug messages in stderr."""

    _, stderr = _run(tmp_path, "-d", capture_output=True)

    assert _get_debug_modules(stderr), "Expected debug messages in stderr with '-d'"

def test_debug_modules(tmp_path: Path):
    """
    Test that '--debug-modules' limits debug output to the specified module.

    Run 'report' with full debug output and then with '--debug-modules _ScatterPlot'. The filtered
    output must contain only '_ScatterPlot' debug messages, while the unfiltered output must contain
    debug messages from more than one module.
    """

    _, stderr_all = _run(tmp_path / "all", "-d", capture_output=True)
    _, stderr_filtered = _run(tmp_path / "filtered", "-d --debug-modules _ScatterPlot",
                              capture_output=True)

    modules_all = _get_debug_modules(stderr_all)
    modules_filtered = _get_debug_modules(stderr_filtered)

    assert len(modules_all) > 1, \
           "Expected debug messages from multiple modules with '-d' and no '--debug-modules'"
    assert modules_filtered == {"_ScatterPlot"}, \
           f"Expected only '_ScatterPlot' debug messages with '--debug-modules _ScatterPlot', " \
           f"but got: {modules_filtered}"

def test_quiet_debug_conflict(tmp_path: Path):
    """Test that combining '-q' and '-d' raises an error."""

    _run(tmp_path, "-q -d", exp_exc=Error)

def test_debug_modules_requires_debug(tmp_path: Path):
    """Test that '--debug-modules' without '-d' raises an error."""

    _run(tmp_path, "--debug-modules _ScatterPlot", exp_exc=Error)

def test_no_color(tmp_path: Path):
    """
    Test that output to a non-TTY does not contain ANSI color codes by default.

    Notes:
        - 'capture_output=True' redirects output to 'StringIO' buffers. 'StringIO.isatty()'
          returns 'False', making the logger treat the output as non-TTY automatically.
        - Debug mode ('-d') is used to generate enough output to check for color codes.
    """

    stdout, stderr = _run(tmp_path, "-d", capture_output=True)

    assert not _ANSI_COLOR_REGEX.search(stdout + stderr), \
        "Expected no ANSI color codes in non-TTY output without '--force-color'"

def test_force_color(tmp_path: Path):
    """
    Test that '--force-color' enables ANSI color codes in non-TTY output.

    Notes:
        - INFO level messages are never colored, so debug mode ('-d') is used to ensure colored
          output is produced when '--force-color' is active.
    """

    stdout, stderr = _run(tmp_path, "--force-color -d", capture_output=True)

    assert _ANSI_COLOR_REGEX.search(stdout + stderr), \
        "Expected ANSI color codes in output with '--force-color -d'"
