# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the capability of building 'pandas.DataFrames' out of raw turbostat statistics files.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from typing import Any
from pathlib import Path
import pandas
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat
from statscollectlibs.dfbuilders import _DFHelpers
from statscollectlibs.parsers import TurbostatParser
from statscollectlibs.mdc import TurbostatMDC

class TurbostatDFBuilder:
    """
    Provide the capability of building a 'pandas.DataFrames' out of raw turbostat statistics files.
    """

    def __init__(self, cpus: list[int] | None = None):
        """
        Initialize the class instance.

        Args:
            cpus: The measured CPU numbers.
        """

        self._cpus = cpus
        self.mdo: TurbostatMDC.TurbostatMDC | None = None

        # Name of the dataframe column containing the time since the epoch time-stamps.
        self.ts_colname = "Time_Of_Day_Seconds"
        # Name of the dataframe column containing the time elapsed since the beginning of the
        # measurements.
        self.time_colname = "TimeElapsed"

        # Theis is initialized in 'build_df()'.
        self._path: Path

    def _build_cols_dict(self,
                         tstat: dict[str, Any],
                         scope: str, cpu: int | None = None) -> dict[str, list[Any]]:
        """
        Build a columns dictionary for 'pandas.DataFrame.from_dict()'. Prefix the turbostat metrics
        with the scope name.

        Args:
            tstat: Dictionary containing turbostat metrics in the format '{metric: value}'.
            scope: The scope of the metrics, either "System" or "CPU".
            cpu: The CPU number if the scope is "CPU".

        Returns:
            dict: A dictionary in the format '{column_name: [value]}' suitable for use with
                  'pandas.DataFrame.from_dict()'.
        """

        cols_dict = {}
        dont_prefix_metrics = {self.ts_colname, self.time_colname}

        if scope == "System":
            prefix = "System"
        elif scope == "CPU":
            assert cpu is not None
            prefix = f"CPU{cpu}"
        else:
            raise Error("BUG: unsupported scope '{scope}'")

        for metric, value in tstat.items():
            if self.mdo and metric not in self.mdo.mdd:
                continue

            if metric in dont_prefix_metrics:
                colname = metric
            else:
                colname = f"{prefix}-{metric}"

            cols_dict[colname] = [value]

        return cols_dict

    def _extract_cpu_data(self, cpu: int, dataset):
        """
        Extract data for a specific CPU number from a dataset.

        Args:
            cpu: The CPU number.
            dataset: The dataset dictionary from 'TurbostatParser'.

        Returns:
            dict: A dictionary containing the turbostat data for the specified CPU.
        """

        try:
            cpu_tstat = dataset["cpus"][cpu]
        except KeyError:
            raise Error(f"No data for CPU '{cpu}' found in turbostat statistics file "
                        f"'{self._path}") from None

        return cpu_tstat

    # TODO: implement proper type hint for dataset and add it.
    def _dataset_to_df(self, dataset: dict[Any, Any]) -> pandas.DataFrame:
        """
        Convert a dataset dictionary from 'TurbostatParser' to a pandas dataframe. The dataframe
        columns will be prefixed with the scope name.

        Args:
            dataset: The dataset dictionary from 'TurbostatParser'.

        Returns:
            pandas.DataFrame: A dataframe containing the turbostat data with appropriate column
                   prefixes.
        """

        # Prepare the "columns dictionary", which has the '{colname: [value]}' format. This format
        # is required by 'pandas.DataFrame.from_dict()'. Start with the system-wide scope metrics.
        cols_dict = self._build_cols_dict(dataset["totals"], "System")
        if self._cpus is not None:
            for cpu in self._cpus:
                cpu_tstat = self._extract_cpu_data(cpu, dataset)
                cols_dict.update(self._build_cols_dict(cpu_tstat, "CPU", cpu=cpu))

        return pandas.DataFrame.from_dict(cols_dict)

    def build_df(self, path: Path) -> pandas.DataFrame:
        """
        Build the turbostat statistics dataframe from the raw statistics file.

        Args:
            path: The file path to the raw turbostat statistics file.

        Returns:
            pandas.DataFrame: A DataFrame containing the data from the turbostat statistics file.

        Raises:
            ErrorBadFormat: If the raw statistics file does not include time-stamps.
        """

        self._path = path

        parser = TurbostatParser.TurbostatParser(path, derivatives=True)
        generator = parser.next()

        try:
            # Try to read the first data point from raw statistics file.
            dataset = next(generator)
        except StopIteration:
            raise Error(f"Empty or incorrectly formatted 'turbostat' statistics file "
                        f"'{path}") from None

        # Sanity check.
        if self.ts_colname not in dataset["totals"]:
            raise ErrorBadFormat(f"Rejecting turbostat statistics file '{path}' - it does not "
                                 f"include time-stamps.\nCollect turbostat statistics with the "
                                 f"'--enable Time_Of_Day_Seconds' option to include time-stamps.")

        # Initialise 'df' with the first datapoint in the raw statistics file.
        df = self._dataset_to_df(dataset)

        self.mdo = TurbostatMDC.TurbostatMDC(list(dataset["totals"]))

        # The very first dataframe was built without taking into account that some metrics are not
        # needed. Remove the corresponding columns.
        for colname in df.columns:
            _, metric = _DFHelpers.split_colname(colname)
            if metric not in self.mdo.mdd:
                df.drop(columns=[colname], inplace=True)

        # Add the rest of the data from the raw turbostat statistics file to 'sdf'.
        for dataset in generator:
            next_row_df = self._dataset_to_df(dataset)
            df = pandas.concat([df, next_row_df], ignore_index=True)

        return df
