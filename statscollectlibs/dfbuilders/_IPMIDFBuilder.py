# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the capability of building a 'pandas.DataFrames' object out of IPMI statistics files.

Terminology.
  * column name - the dataframe column name.
  * metric name - name of the IPMI metric as per the raw IPMI statistics file.
  * category - the metric category (e.g., "Temperature"). Column names are constructed as
               "category, dash, metric name".
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.mdc import IPMIMDC
from statscollectlibs.parsers import IPMIParser

if typing.TYPE_CHECKING:
    from typing import Any

class IPMIDFBuilder:
    """
    Provide the capability of building a 'pandas.DataFrames' object out of IPMI statistics files.
    """

    def __init__(self):
        """The class constructor."""

        self.mdo: IPMIMDC.IPMIMDC | None = None

        # Name of the dataframe column containing the time since the epoch time-stamps.
        self.ts_colname = "timestamp"
        # Name of the dataframe column containing the time elapsed since the beginning of the
        # measurements.
        self.time_colname = "TimeElapsed"

    # TODO: annotate IPMIparser, use correct type in this module.
    @staticmethod
    def _dataset_to_df(dataset: dict[str, tuple[Any, str]],
                       include_metrics: set[str] | None = None):
        """
        Convert a dataset dictionary from 'IPMIParser' to a pandas dataframe.

        Args:
            dataset: A dataset dictionary from the 'IPMIParser'.
            include_metrics: A set of metric names to include in the dataframe. If None, include all
                             metrics.

        Returns:
            pandas.DataFrame: A dataframe containing the metrics as columns and their values in the
                              rows.
        """

        def _reduce_dp():
            """
            Reduce the parsed IPMI datapoint dictionary to only include metrics in
            'include_metrics'.
            """

            for metric, pair in dataset.items():
                val = pair[0]
                if val is None:
                    # If "no reading" is parsed in a line of a raw IPMI file, 'None' is returned. In
                    # this case, we should exclude that IPMI metric.
                    continue
                if include_metrics and metric not in include_metrics:
                    continue
                yield metric, val

        reduced_dp = {metric:[val] for metric, val in _reduce_dp()}
        return pandas.DataFrame.from_dict(reduced_dp)

    def build_df(self, path: Path) -> pandas.DataFrame:
        """
        Build the IPMI statistics dataframe from the raw statistics file.

        Args:
            path: The file path to the raw IPMI statistics file.

        Returns:
            pandas.DataFrame: A DataFrame containing the data from the IPMI statistics file.
        """

        parser = IPMIParser.IPMIParser(path, derivatives=True).next()

        try:
            # Read the first data point from raw statistics file.
            dataset = next(parser)
        except StopIteration as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"empty or incorrectly formatted IPMI raw statistics file:\n"
                        f"{errmsg}") from err

        self.mdo = IPMIMDC.IPMIMDC(dataset)

        include_metrics = set(self.mdo.mdd.keys())

        sdf = self._dataset_to_df(dataset, include_metrics=include_metrics)

        # Add the rest of the data from the raw IPMI statistics file to 'sdf'.
        for dataset in parser:
            df = self._dataset_to_df(dataset, include_metrics=include_metrics)
            sdf = pandas.concat([sdf, df], ignore_index=True)

        return sdf
