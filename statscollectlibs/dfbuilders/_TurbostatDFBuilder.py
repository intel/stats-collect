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
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import TurbostatParser

def split_colname(colname):
    """
    Turbostat dataframe columns have the "<scope>-<metric>" format, where "<scope>" is the scope
    name, such as "CPU0", and "<metric>" is the metric name, such as "PkgPower". Split a turbostat
    dataframe column name and return the "<scope>" and "<metric>" parts as a tuple. The arguments
    are as follows.
      * colname - a dataframe column name to split.
    """

    split = colname.split("-", 1)
    if len(split) == 1:
        return None, colname

    return split[0], split[1]

def format_colname(metric, sname):
    """Format and return a dataframe column name for metric 'metric' and scope 'sname'."""

    if metric in {"Time_Of_Day_Seconds", "TimeElapsed"}:
        return metric
    return f"{sname}-{metric}"

class TurbostatDFBuilder(_DFBuilderBase.DFBuilderBase):
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

        super().__init__("Time_Of_Day_Seconds", "TimeElapsed")

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
        dont_prefix_metrics = {"Time_Of_Day_Seconds", "TimeElapsed"}

        if scope == "System":
            prefix = "System"
        elif scope == "CPU":
            assert cpu is not None
            prefix = f"CPU{cpu}"
        else:
            raise Error("BUG: unsupported scope '{scope}'")

        for metric, value in tstat.items():
            if metric in dont_prefix_metrics:
                colname = metric
            else:
                colname = f"{prefix}-{metric}"

            cols_dict[colname] = [value]

        return cols_dict

    def _extract_cpu_data(self, cpu: int, parsed_dp):
        """
        Extract turbostat data for a specific CPU number.

        Args:
            cpu: The CPU number.
            parsed_dp: The parsed turbostat datapoint dictionary from 'TurbostatParser'.

        Returns:
            dict: A dictionary containing the turbostat data for the specified CPU.
        """

        try:
            cpu_tstat = parsed_dp["cpus"][cpu]
        except KeyError:
            raise Error(f"No data for CPU '{cpu}' found in turbostat statistics file "
                        f"'{self._path}") from None

        return cpu_tstat

    # TODO: implement proper type hint for parsed_dp and add it.
    def _turbostat_to_df(self, parsed_dp: dict[Any, Any]) -> pandas.DataFrame:
        """
        Convert a parsed turbostat datapoint dictionary to a pandas dataframe. The DataFrame
        columns will be prefixed with the scope name.

        Args:
            parsed_dp: The parsed turbostat datapoint dictionary from 'TurbostatParser'.

        Returns:
            pandas.DataFrame: A dataframe containing the turbostat data with appropriate column
                   prefixes.
        """

        # Prepare the "columns dictionary", which has the '{colname: [value]}' format. This format
        # is required by 'pandas.DataFrame.from_dict()'. Start with the system-wide scope metrics.
        cols_dict = self._build_cols_dict(parsed_dp["totals"], "System")
        if self._cpus is not None:
            for cpu in self._cpus:
                cpu_tstat = self._extract_cpu_data(cpu, parsed_dp)
                cols_dict.update(self._build_cols_dict(cpu_tstat, "CPU", cpu=cpu))

        return pandas.DataFrame.from_dict(cols_dict)

    def _read_stats_file(self, path: Path) -> pandas.DataFrame:
        """
        Read a raw turbostat statistics file and return its data as a pandas dataframe.

        Args:
            path: The file path to the raw turbostat statistics file.

        Returns:
            pandas.DataFrame: A DataFrame containing the data from the turbostat statistics file.

        Raises:
            ErrorBadFormat: If the raw statistics file does not include time-stamps.
        """

        parser = TurbostatParser.TurbostatParser(path, derivatives=True)
        generator = parser.next()

        try:
            # Try to read the first data point from raw statistics file.
            parsed_dp = next(generator)
        except StopIteration:
            raise Error(f"Empty or incorrectly formatted 'turbostat' statistics file "
                        f"'{path}") from None

        # Sanity check.
        if "Time_Of_Day_Seconds" not in parsed_dp["totals"]:
            raise ErrorBadFormat(f"Rejecting turbostat statistics file '{path}' - it does not "
                                 f"include time-stamps.\nCollect turbostat statistics with the "
                                 f"'--enable Time_Of_Day_Seconds' option to include time-stamps.")

        # Initialise 'df' with the first datapoint in the raw statistics file.
        df = self._turbostat_to_df(parsed_dp)

        # Add the rest of the data from the raw turbostat statistics file to 'sdf'.
        for parsed_dp in generator:
            next_row_df = self._turbostat_to_df(parsed_dp)
            df = pandas.concat([df, next_row_df], ignore_index=True)

        return df
