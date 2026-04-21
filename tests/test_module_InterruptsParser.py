# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Tests for the 'InterruptsParser' module."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pepclibs.helperlibs.Exceptions import ErrorBadFormat
from pepclibs.helperlibs import Trivial
from statscollectlibs.parsers import InterruptsParser

from tests import _Common

if typing.TYPE_CHECKING:
    from typing import TypedDict

    class _GoodInputEntry(TypedDict):
        yield_cnt: int
        input: str

_TEST_FILES_DIR = _Common.get_test_data_base() / "test_module_InterruptsParser" / "files"

def test_cut_files():
    """
    Test that 'InterruptsParser' handles files from '_TEST_FILES_DIR' with the last
    '/proc/interrupts' snapshot cut.
    """

    def _do_asserts(first_snapshot, last_snapshot):
        """
        Compare the first and last '/proc/interrupts' snapshots, ensure they are valid and the
        same number of CPUs and IRQs are present.
        """

        assert "timestamp" in first_snapshot, f"{pfx}: Missing 'timestamp' in first snapshot"
        assert "timestamp" in last_snapshot, f"{pfx}: Missing 'timestamp' in last snapshot"

        assert first_snapshot["timestamp"] < last_snapshot["timestamp"], \
               f"{pfx}: Expected increasing timestamps, but got '{first_snapshot['timestamp']}'"\
               f" followed by '{last_snapshot['timestamp']}'"

        assert "cpu2irqs" in first_snapshot, f"{pfx}: Missing 'cpu2irqs' in first snapshot"
        assert "cpu2irqs" in last_snapshot, f"{pfx}: Missing 'cpu2irqs' in last snapshot"

        assert len(first_snapshot["cpu2irqs"]) == len(last_snapshot["cpu2irqs"]), \
               f"{pfx}: Expected the same number of CPUs, but got " \
               f"{Trivial.rangify(list(first_snapshot['cpu2irqs']))} and " \
               f"{Trivial.rangify(list(last_snapshot['cpu2irqs']))}"

        assert len(first_snapshot["irq_info"]) == len(last_snapshot["irq_info"]), \
               f"{pfx}: Expected the same number of IRQs, but got " \
               f"{list(first_snapshot['irq_info'])} and {list(last_snapshot['irq_info'])}"

    for test_file in _TEST_FILES_DIR.iterdir():
        if "-cut" not in test_file.name:
            continue

        pfx = str(test_file)
        parser = InterruptsParser.InterruptsParser(path=test_file)
        generator = parser.next()

        first_snapshot = next(generator)
        last_snapshot = None
        for last_snapshot in generator:
            pass

        assert last_snapshot is not None, \
               f"{pfx}: Expected multiple '/proc/interrupts' snapshots, but got only one"

        _do_asserts(first_snapshot, last_snapshot)

        first_snapshot, last_snapshot = parser.get_first_and_last()

        _do_asserts(first_snapshot, last_snapshot)

def test_complete_files():
    """
    Test that 'InterruptsParser' handles files from '_TEST_FILES_DIR' with complete
    '/proc/interrupts' snapshots.
    """

    for test_file in _TEST_FILES_DIR.iterdir():
        if "-cut" in test_file.name:
            continue

        parser = InterruptsParser.InterruptsParser(path=test_file)
        for data_set in parser.next():
            assert "timestamp" in data_set
            assert "cpu2irqs" in data_set
            assert "irq_info" in data_set

            assert data_set["timestamp"] > 0
            assert data_set["cpu2irqs"]
            assert data_set["irq_info"]

            for cpu, cpu_irqs in data_set["cpu2irqs"].items():
                assert cpu >= 0, f"Negative CPU number '{cpu}'"
                for irqname, cnt in cpu_irqs.items():
                    assert cnt >= 0, \
                           f"Negative interrupts count '{cnt}' for '{irqname}' on CPU '{cpu}'"

            for name, info in data_set["irq_info"].items():
                assert "irq_num" in info, f"Missing 'irq_num' for '{name}'"
                assert "chip_name" in info, f"Missing 'chip_name' for '{name}'"
                assert "hwirq" in info, f"Missing 'hwirq' for '{name}'"
                assert "action" in info, f"Missing 'action' for '{name}'"

_BAD_INPUT: dict[str, str] = {
    "Too short input #1": "Timestamp: 1234567890",

    "Too short input #2": "Timestamp: 1234567890\nCPU1 CPU2",

    "Too short input #3": """Timestamp: 1234567890.1
CPU1 CPU2
Interrupted, exiting""",

    "Too short input #4": "",

    "Too short input #5": "  # comment",

    "Bad timestamp": r"""Timestamp: K1
CPU1 CPU2
1: 1 1""",

    "Bad CPU number": r"""Timestamp: 1234567890.1
CPU-1 CPU2
1: x""",

    "Bad interrupts count value": r"""Timestamp: 1234567890.1
CPU1 CPU2
1: x""",
}

def test_bad_input():
    """
    Test that 'InterruptsParser' fails with invalid input.
    """

    for name, bad_input in _BAD_INPUT.items():
        parser = InterruptsParser.InterruptsParser(lines=iter(bad_input.splitlines()))
        try:
            for _ in parser.next():
                pass
        except ErrorBadFormat:
            continue

        assert False, f"Did not get 'ErrorBadFormat' with the following bad input: '{name}'"

_GOOD_INPUT: dict[str, _GoodInputEntry] = {
    "Good input #1": {
        "yield_cnt": 1,
        "input": r"""Timestamp: 1234567890.1
CPU1 CPU2
1: 1 3""",
    },

    "Good input #2": {
        "yield_cnt": 1,
        "input": r"""Timestamp: 1234567890.1
CPU1 CPU2
1: 1 3
Timestamp: 1234567890.2""",
    },

    "Good input #3": {
        "yield_cnt": 1,
        "input": r"""Timestamp: 1234567890.1
CPU1 CPU2
1: 1 3
Timestamp: 1234567890.2
CPU1 CPU2""",
    },

    "Good input #4": {
        "yield_cnt": 1,
        "input": r"""Timestamp: 1234567890.1
CPU1 CPU2
1: 1 3
Timestamp: 1234567890.2
CPU1 CPU2
Interrupted, exiting""",
    },

    "Good input #5": {
        "yield_cnt": 2,
        "input": r"""Timestamp: 1234567890.1
CPU1
1: 1
Timestamp: 1234567890.2
CPU1
1: 2
Interrupted, exiting""",
    },
}

def test_good_input():
    """
    Test that 'InterruptsParser' handles valid input.
    """

    for name, good_input in _GOOD_INPUT.items():
        parser = InterruptsParser.InterruptsParser(lines=iter(good_input["input"].splitlines()))
        cnt = 0
        try:
            for _ in parser.next():
                cnt += 1
        except ErrorBadFormat:
            assert False, f"Got 'ErrorBadFormat' with the following good input: '{name}'"

        assert cnt == good_input["yield_cnt"], \
               f"Did not get the expected number of yields with good input: '{name}'"

# TODO: Remove this test in 2027 when old 'timestamp:' format support is dropped.
def test_old_timestamp_format():
    """
    Test that 'InterruptsParser' accepts the old lowercase 'timestamp:' format.
    """

    old_format_input = """timestamp: 1234567890.1
CPU1 CPU2
1: 1 3
timestamp: 1234567890.2
CPU1 CPU2
1: 2 4
Interrupted, exiting"""

    parser = InterruptsParser.InterruptsParser(lines=iter(old_format_input.splitlines()))
    cnt = 0
    try:
        for _ in parser.next():
            cnt += 1
    except ErrorBadFormat:
        assert False, "Got 'ErrorBadFormat' with old-format 'timestamp:' input"

    assert cnt == 2, f"Expected 2 datasets from old-format input, got {cnt}"
