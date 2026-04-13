# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""Common bits for the tests."""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path

def get_prj_src_path() -> Path:
    """
    Return the path to the stats-collect project source tree root directory.

    Returns:
        Path to the project source tree root directory.
    """

    return Path(__file__).parent.parent.resolve()

def get_test_data_base() -> Path:
    """
    Return the path to the test data base directory.

    Returns:
        Path to the test data base directory.
    """

    return get_prj_src_path() / "tests" / "data"
