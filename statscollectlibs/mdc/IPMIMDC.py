# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""Provide the IPMI metrics definition class."""

from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.mdc import MDCBase

class IPMIMDC(MDCBase.MDCBase):
    """
    The IPMI metrics definition class provides API to IPMI metrics definitions, which describe the
    metrics provided by the IPMI raw statistics files.
    """

    @staticmethod
    def _get_category(unit):
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
            "Amps": "Current",
            "Volts": "Voltage",
        }
        return unit2category.get(unit)

    def _populate(self, parsed_dp):
        """
        Populate the 'self.mdd' dictionary with metric names and categories.
        """

        # The IPMI metrics definition file includes only category names, except for "TimeElapsed"
        # and "timestamp", which are metric names.
        for category in self.mdd:
            if category in ("TimeElapsed", "timestamp"):
                # Put time-stamp metrics to the "Timestamp" category.
                category = "Timestamp"
            if category in self.categories:
                continue
            self.categories[category] = []

        new_mdd = {}

        for metric, val in parsed_dp.items():
            unit = val[1]

            category = self._get_category(unit)
            if not category:
                if metric in ("TimeElapsed", "timestamp"):
                    md = self.mdd.get(metric)
                    category = "Timestamp"
                else:
                    # Just drop metrics that do not fit a pre-defined category.
                    continue
            else:
                md = self.mdd.get(category)
                if not md:
                    raise Error(f"IPMI category '{category}' was not found in '{self.path}'")

            new_mdd[metric] = md.copy()
            new_mdd[metric]["Title"] = metric
            new_mdd[metric]["category"] = category

            self.categories[category].append(metric)

        self.mdd = new_mdd

    def __init__(self, parsed_dp):
        """
        The class constructor. The arguments are as follows.
          * parsed_dp - the parsed datapoint dictionary from the 'IPMIParser'.

        IMPI metrics are not known in advance, and metrics definitions dictionary is built
        on-the-fly from the 'parsed_dp' dictionary.
        """

        self.categories = {}

        super().__init__("stats-collect", "ipmi", defsdir=Path("defs/statscollect"))
        self._populate(parsed_dp)
        super().mangle()
