#!/usr/bin/python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Common code for stats-collect helper programs (intallables).
"""

import sys
from pathlib import Path

def print_module_paths():
    """
    Print paths to all modules other than standard.
    """

    components = ("statscollectlibs", "statscollecttools", "pepclibs")

    for mobj in sys.modules.values():
        file = getattr(mobj, "__file__", None)
        if not file:
            continue

        path = Path(file)
        if not path.parts[-1].endswith(".py"):
            continue

        for component in components:
            if component in path.parts:
                print(path)
