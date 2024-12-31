# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides an API to the AC Power definitions (AKA 'defs')."""

from statscollectlibs.defs import DefsBase

class ACPowerDefs(DefsBase.DefsBase):
    """This class provides an API to the AC Power definitions (AKA 'defs')."""

    def __init__(self):
        """The class constructor."""

        super().__init__("stats-collect", "acpower", defsdir="defs/statscollect")
        self.mangle()
