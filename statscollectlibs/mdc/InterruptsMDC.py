# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the interrupts metrics definition class.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from statscollectlibs.mdc import MDCBase

class InterruptsMDC(MDCBase.MDCBase):
    """
    The interrupts metrics definition class that provides the metrics definitions for the interrupts
    metrics read from the '/proc/interrupts' file.
    """

    def __init__(self, metrics: list[str]):
        """
        The class constructor.

        Args:
            metrics: List of metric names to use for substituting the pattern in the metric
                     definition dictionary.
        """

        super().__init__("stats-collect", Path("defs/statscollect/interrupts.yml"))
        self.mangle(metrics)

    def mangle(self, metrics: list[str], drop_missing: bool = True):
        """
        Modify the metrics definition dictionary. In addition to what the base class does, add the
        metrics missing from the YAML file.

        Args:
            metrics: List of metric names to use for substituting the pattern in the metric
                     definition dictionary.
            drop_missing: If 'True', keep only metrics in 'metrics' in the MDD, and drop all other
                          metrics from the MDD. If 'False', keep all metrics.
        """

        super().mangle(metrics, drop_missing=drop_missing)

        # Add the missing metrics.
        for metric in metrics:
            if metric in self.mdd:
                continue

            if metric.endswith("_rate"):
                name = metric[:-len("_rate")]
                self.mdd[metric] = {
                    "name": metric,
                    "title": f"{name} interrupts rate",
                    "descr": f"The average rate of {name} interrupts during the measurement "
                             f"interval.",
                    "scope": "CPU",
                    "unit": "interrupts/s",
                    "short_unit": "intr/s",
                }
            else:
                self.mdd[metric] = {
                    "name": metric,
                    "title": f"{metric} interrupts count",
                    "descr": f"Number of {metric} interrupts serviced during the measurement "
                             f"interval.",
                    "scope": "CPU",
                }
