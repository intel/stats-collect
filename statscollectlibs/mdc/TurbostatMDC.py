# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the turbostat metrics definition class."""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from typing import Any
from statscollectlibs.mdc import MDCBase
from statscollectlibs.mdc.MDCBase import MDTypedDict

class TurbostatMDC(MDCBase.MDCBase):
    """
    Provide an API for turbostat metrics definitions.
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

            assert isinstance(leaf, list)
            leaf.append(metric)

    def _sort_mdd(self):
        """
        Sort the metrics definition dictionary.

        The MDD is sorted in the definitions order, and it is mostly OK. However, the C-state
        requests count metrics are grouped so that first go all the counters (e.g., POLL, C1, C1E,
        etc.), then go the too deep request counts (e.g., C1-, C1E-, etc.), then got the too shallow
        request counts (e.g., C1+, C1E+, etc.). This is not the most intuitive order. Re-arrange it
        so that the too deep requests go first, then the counters, and then the too shallow requests
        (e.g., POLL, POLL+, C1-, C1, C1+, C1E-, C1E, C1E+, etc.).
        """

        req_cstates_list: list[str] = []
        req_cstates_set: set[str] = set()
        too_shallow_set: set[str] = set()
        too_deep_set: set[str] = set()

        # Prepare the list or requested C-state names.
        for metric, md in self.mdd.items():
            if md.get("categories") != ["C-state", "Requested", "Count"]:
                # Not a requestable C-state metric.
                continue
            if metric.endswith("+"):
                too_shallow_set.add(metric)
            elif metric.endswith("-"):
                too_deep_set.add(metric)
            else:
                req_cstates_list.append(metric)
                req_cstates_set.add(metric)

        if not req_cstates_list:
            return

        # Sort the MDD dictionary by inserting the keys in the wanted order into a new dictionary.
        new_mdd: dict[str, MDTypedDict] = {}

        for metric in list(self.mdd):
            if metric not in self.mdd:
                # The metric was already moved to the new dictionary.
                continue

            if metric in req_cstates_list:
                too_deep = f"{metric}-"
                too_shallow = f"{metric}+"
            elif metric in too_shallow_set:
                too_shallow = metric
                metric = metric[:-1]
                too_deep = f"{metric}-"
            elif metric in too_deep_set:
                too_deep = metric
                metric = metric[:-1]
                too_shallow = f"{metric}+"
            else:
                # The metric is not a C-state request count, do not change the order.
                new_mdd[metric] = self.mdd[metric]
                continue

            # The metric is a C-state request count. Insert its "-" metric first.
            if too_deep in self.mdd:
                new_mdd[too_deep] = self.mdd.pop(too_deep)

            # Then insert the counter.
            if metric in self.mdd:
                new_mdd[metric] = self.mdd.pop(metric)

            # Finally, insert the "+" metric.
            if too_shallow in self.mdd:
                new_mdd[too_shallow] = self.mdd.pop(too_shallow)

        self.mdd = new_mdd

    def __init__(self, metrics: list[str]):
        """
        Initialize a class instance.

        Args:
            metrics: A list of metric names used for substituting patterns in the metrics definition
            dictionary.
        """

        # Metric names arrange by the category.
        self.categories: dict[str, Any] = {}

        super().__init__("stats-collect", Path("defs/statscollect/turbostat.yml"))
        self.mangle(metrics)

        self._sort_mdd()
        self._categorize()
