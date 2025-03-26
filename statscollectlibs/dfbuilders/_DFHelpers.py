# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Miscellaneous helper functions shared by dataframe builder classes.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

def split_colname(colname: str) -> tuple[str | None, str]:
    """
    Split a dataframe column name into scope and metric parts.

    Dataframe columns for some statistics follow the "<scope>-<metric>" format, where "<scope>"
    represents the scope name (e.g., "CPU0") and "<metric>" represents the metric name (e.g.,
    "PkgPower"). Split the column name into its scope and metric components and returns them as a
    tuple.

    Args:
        colname: The dataframe column name to split.

    Returns:
        A tuple containing:
        - The scope part of the column name, or None if no scope is present.
        - The metric part of the column name.
    """

    split = colname.split("-", 1)
    if len(split) == 1:
        return None, colname

    return split[0], split[1]
