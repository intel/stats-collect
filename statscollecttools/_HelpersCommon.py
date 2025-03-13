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

def print_module_paths():
    """
    Print paths to all modules other than standard.
    """

    subpaths = ("pepclibs/", "statscollectlibs/", "statscollecttools/")

    for mobj in sys.modules.values():
        path = getattr(mobj, "__file__", None)
        if not path:
            continue

        if not path.endswith(".py"):
            continue

        for subpath in subpaths:
            if subpath in path:
                print(path)
