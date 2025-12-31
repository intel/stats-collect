# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@linux.intel.com>

"""
Provide constants for information about the 'stats-collect' tool, such as its
name and version.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing

if typing.TYPE_CHECKING:
    from typing import Final

VERSION: Final[str] = "1.0.65"
TOOLNAME: Final[str] = "stats-collect"
