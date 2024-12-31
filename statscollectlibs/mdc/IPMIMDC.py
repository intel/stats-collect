# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""Provide the IPMI metrics definition class."""

from statscollectlibs.mdc import MDCBase

class IPMIMDC(MDCBase.MDCBase):
    """
    The IPMI metrics definition class provides API to IPMI metrics definitions, which describe the
    metrics provided by the IPMI raw statistics files.
    """

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

        super().__init__("stats-collect", "ipmi", defsdir="defs/statscollect")
        super().mangle()
