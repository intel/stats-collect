# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the turbostat metrics definition class."""

from statscollectlibs.defs import MDCBase
from statscollectlibs.parsers import TurbostatParser

class TurbostatMDC(MDCBase.MDCBase):
    """
    The turbostat metrics definition class provides API to turbostat metrics definitions, which
    describe the metrics provided by the turbostat raw statistics files.
    """

    def mangle_descriptions(self):
        """Mangle turbostat metric descriptions to describe how they are summarized by turbostat."""

        for metric, mdef in self.info.items():
            name = TurbostatParser.get_totals_func_name(metric)
            if name is not None:
                name = TurbostatParser.TOTALS_FUNCS[name] # Get user-friendly name.
                mdef["descr"] = f"{mdef['descr']} Calculated by finding the {name} of " \
                                f"\"{mdef['name']}\" across the system."

    def _categorize(self):
        """Arrange metrics into a multi-level dictionary by their categories."""

        for metric, info in self.info.items():
            catnames = info.get("categories")
            if not catnames:
                continue

            last = len(info["categories"]) - 1
            leaf = self.categories

            for idx, category in enumerate(catnames):
                if category not in leaf:
                    if idx == last:
                        leaf[category] = []
                    else:
                        leaf[category] = {}

                leaf = leaf[category]

            leaf.append(metric)

    def __init__(self, metrics):
        """
        The class constructor. The arguments are as follows:
          * metrics - a collection of metric names to use for substituting patterns in the metrics
                      definition dictionary ('self.info').
        """

        # Metric names arrange by the category.
        self.categories = {}

        super().__init__("stats-collect", "turbostat", defsdir="defs/statscollect")
        self.mangle(metrics=metrics)

        self._categorize()
