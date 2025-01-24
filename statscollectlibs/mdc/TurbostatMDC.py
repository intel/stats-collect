# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the turbostat metrics definition class."""

from pathlib import Path
from statscollectlibs.mdc import MDCBase

class TurbostatMDC(MDCBase.MDCBase):
    """
    The turbostat metrics definition class provides API to turbostat metrics definitions, which
    describe the metrics provided by the turbostat raw statistics files.
    """

    def _categorize(self):
        """Arrange metrics into a multi-level dictionary by their categories."""

        for metric, md in self.mdd.items():
            catnames = md.get("categories")
            if not catnames:
                continue

            last = len(md["categories"]) - 1
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
                      definition dictionary ('self.mdd').
        """

        # Metric names arrange by the category.
        self.categories = {}

        super().__init__("stats-collect", Path("defs/statscollect/turbostat.yml"))
        self.mangle(metrics)

        self._categorize()
