# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the IPMI metrics definition class."""

from __future__ import annotations # Remove when switching to Python 3.10+.

from typing import Any
from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.mdc import MDCBase
from statscollectlibs.mdc.MDCBase import MDTypedDict

class IPMIMDC(MDCBase.MDCBase):
    """
    The IPMI metrics definition class provides API to IPMI metrics definitions, which describe the
    metrics provided by the IPMI raw statistics files.
    """

    # TODO: annotate IPMIparser, use correct type in this module.
    # TODO: consistently use the same terminology as in InterruptsParser: the dictionary from the
    #       parser is a "dataset", not a "datapoint".
    def __init__(self, parsed_dp: dict[str, tuple[Any, str]]):
        """
        Initialize a class instance.

        Args:
            parsed_dp: Parsed datapoint dictionary from the 'IPMIParser'.

        Notes:
            IPMI metrics are not predefined. The metrics definitions dictionary is dynamically
            constructed from the 'parsed_dp' dictionary.
        """

        self.categories: dict[str, list[str]] = {}

        super().__init__("stats-collect", Path("defs/statscollect/ipmi.yml"))
        self._populate(parsed_dp)

    @staticmethod
    def _get_category(unit: str) -> str | None:
        """
        Metrics are categorized based on the unit. For example, "RPM" metrics are categorized as fan
        speed. Return the category name based on the unit.

        Args:
            unit: The unit name of a metric.

        Returns:
            str: The name of the metric category, or 'None' if no category exists for the unit.
        """

        unit2category = {
            "RPM": "FanSpeed",
            "degrees C": "Temperature",
            "Watts": "Power",
            "Amps": "Current",
            "Volts": "Voltage",
        }
        return unit2category.get(unit)

    def _populate(self, parsed_dp: dict[str, tuple[Any, str]]):
        """
        Populate the 'self.mdd' dictionary with metric information using a parsed IPMI datapoint
        from the IPMI parser.

        Args:
            parsed_dp: Parsed datapoint dictionary from the 'IPMIParser'.
        """

        category: str | None

        # The IPMI metrics definition file includes only category names, except for "TimeElapsed"
        # and "timestamp", which are metric names.
        for category in self.mdd:
            if category in ("TimeElapsed", "timestamp"):
                # Put time-stamp metrics to the "Timestamp" category.
                category = "Timestamp"
            if category in self.categories:
                continue
            self.categories[category] = []

        new_mdd: dict[str, MDTypedDict] = {}

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
            new_mdd[metric]["title"] = metric
            new_mdd[metric]["categories"] = [category]

            self.categories[category].append(metric)

        self.mdd = new_mdd
