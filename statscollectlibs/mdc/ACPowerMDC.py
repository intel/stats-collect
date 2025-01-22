# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""Provide the AC power metrics definition class."""

from pathlib import Path
from statscollectlibs.mdc import MDCBase

class ACPowerMDC(MDCBase.MDCBase):
    """
    The AC power metrics definition class provides API to AC power metrics definitions, which
    describe the metrics provided by the "acpower" raw statistics files.
    """

    def __init__(self):
        """The class constructor."""

        super().__init__("stats-collect", Path("defs/statscollect/acpower.yml"))
