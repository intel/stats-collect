# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides an API to the IPMI definitions (AKA 'defs')."""

from statscollectlibs.defs import _STCDefsBase

class IPMIDefs(_STCDefsBase.STCDefsBase):
    """This class provides an API to the IPMI definitions (AKA 'defs')."""

    @staticmethod
    def get_category(unit):
        """
        Return the metric category name by its unit name. Return 'None' if there is no category for
        the unit. The arguments are as follows.
          * unit - unit name from the raw IPMI file or the definitions dictionary (there is a
                   difference, e.g., "Amps" vs "Amp").

        Get the name of an IPMI metric category by its unit name. Return 'None' if there is no
        category for the unit.
        """

        unit2category = {
            "RPM": "FanSpeed",
            "degrees C": "Temperature",
            "Watts": "Power",
            "Watt": "Power",
            "Amps": "Current",
            "Amp": "Current",
            "Volts": "Voltage",
            "Volt": "Voltage"
        }
        return unit2category.get(unit)

    def __init__(self):
        """The class constructor."""

        super().__init__("ipmi")
        super().mangle()
