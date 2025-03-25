# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the base class for 'pandas.DataFrame' object builder classes. The goal of dataframe builders
is to build a 'pandas.DataFrame' object from raw statistics files.
"""

# TODO: finish annotating this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from typing import TypedDict
import numpy
import pandas
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class TimeStampLimitsTypedDict(TypedDict, total=False):
    """
    Type for a dictionary for storing the time-stamp range for valid or interesting measurement
    data.

    Attributes:
        begin: The start time-stamp for measurements. Data collected before this time are not valid
               or interesting, and should be discarded.
        end: The end time-stamp for measurements. Data collected after this time are not valid or
             interesting and should be discarded.
        absolute: Whether 'begin' and 'end' are absolute or relative time-stamp values. If True, the
                  values are absolute time since the epoch. If False, the values are relative to the
                  start of the measurements in seconds. For example, if 'begin' is 5, it means data
                  collected during the first 5 seconds from the start of the measurements are not
                  valid or interesting and should be discarded.
    """

    begin: int
    end: int
    absolute: bool

class LoadedLablesTypedDict(TypedDict, total=False):
    """
    Type for a dictionary for storing loaded labels.

    Attributes:
        name: The name of the label.
        ts: The time-stamp of the label.
        metrics: The metrics the lable defines.
    """

    ts: int
    name: str
    metrics: dict[str, str]

def split_colname(colname: str) -> tuple[str | None, str]:
    """
    Split a dataframe column name into scope and metric parts.

    Dataframe columns for some statistics follow the "<scope>-<metric>" format, where "<scope>"
    represents the scope name (e.g., "CPU0") and "<metric>" represents the metric name (e.g.,
    "PkgPower"). Split the column name into its scope and metric components and returns them as a
    tuple.

    Args:
        colname: The dataframe column name to split.

    Returns:
        A tuple containing:
        - The scope part of the column name, or None if no scope is present.
        - The metric part of the column name.
    """

    split = colname.split("-", 1)
    if len(split) == 1:
        return None, colname

    return split[0], split[1]

class DFBuilderBase:
    """
    The base class for 'pandas.DataFrame' object builder classes. The goal of dataframe builders is
    to build a 'pandas.DataFrame' object from raw statistics files.

    This base class requires child classes to implement the following methods.
      *  '_read_stats_file()' - read a raw statistics file and convert the statistics data into a
                               'pandas.DataFrame' object.
    """

    def __init__(self, ts_colname, time_colname):
        """
        The class constructor. The arguments are as follows.
          * ts_colname - name of the time since the epoch dataframe column.
          * time_colname - name of the dataframe column for time elapsed since the beginning of the
            measurements.
        """

        self._ts_colname = ts_colname
        self._time_colname = time_colname

        self.df: pandas.DataFrame | None = None
        self._path: Path | None = None

    def _apply_ts_limits(self, df, ts_limits):
        """Apply time-stamp limits to the 'df' dataframe."""

        # The 'ts_limits' dictionary sanity check.
        for key in ("begin", "end", "absolute"):
            if key not in ts_limits:
                raise Error(f"BUG: bad time-stamp limits dictionary, key {key} is missing")

        if ts_limits["absolute"]:
            colname = self._ts_colname
        else:
            colname = self._time_colname

        df.drop(df.loc[df[colname] < ts_limits["begin"]].index, inplace=True)
        df.drop(df.loc[df[colname] > ts_limits["end"]].index, inplace=True)

        # Normalize the Elapsed time column to start from 0.
        df[self._time_colname] -= df[self._time_colname].iloc[0]

    def _apply_labels(self, df: pandas.DataFrame, labels: list[LoadedLablesTypedDict]):
        """
        Apply labels to a statistics dataframe.

        Args:
            df: The the statistics datafram to which the labels should be applied.
            labels: The lables to apply.

        Notes:
            - The "skip" lable removes all dataframe rows with timestamps starting from the label's
              timestamp and ending at the "start" label timestamp.
            - The "start" label sets the metrics for all dataframe rows with timestamps starting
              from the label's timestamp and ending at the next label's timestamp.
        """

        ts_col = df[self._ts_colname]

        if labels[0]["ts"] > ts_col.iloc[-1]:
            raise Error("fFrst label's timestamp is after the last datapoint timestamp")

        lcnt = len(labels)

        for i, label in enumerate(labels):
            # 'filtered_rows' contains an index of all of the datapoints which 'label' applies to.
            filtered_rows = ts_col >= label["ts"]

            if i < lcnt - 1:
                # Only one label is applicable at a time. Therefore, if there is still at least one
                # label to apply, only apply 'label' to datapoints before the next one is
                # applicable.
                next_label = labels[i + 1]
                filtered_rows &= ts_col < next_label["ts"]

            if label["name"] == "skip":
                # Datapoints labelled 'skip' are dropped from the 'pandas.DataFrame'.
                df.drop(df.loc[filtered_rows].index, inplace=True)
                continue
            elif label["name"] != "start":
                raise Error(f"BUG: usupported label name {label['name']}")

            if len(filtered_rows) < 1:
                continue

            for metric, val in label.get("metrics", {}).items():
                # Assign 'val' in the column for the label metric for all of the datapoints which
                # 'label' corresponds to.
                df.loc[filtered_rows, metric] = val

        # Some 'pandas' operations break on 'pandas.DataFrame' instances without consistent
        # indexing. Reindex the dataframe.
        df = df.reset_index(drop=True)

    def _read_stats_file(self, path: Path) -> pandas.DataFrame:
        """
        Parse the raw interrupt statistics file and build the dataframe.

        Args:
            path: Raw interrupts statistics file path.

        Returns:
            Pandas dataframe including the parsed interrupt statistics data.
        """

        raise NotImplementedError()

    def load_df(self,
                path: Path,
                labels: list[LoadedLablesTypedDict] | None = None,
                ts_limits: TimeStampLimitsTypedDict | None = None):
        """
        Load data from a raw statistics file into a dataframe.

        Args:
            path: Path to the raw statistics file to load.
            labels: Optional list of dictionaries containing labels to apply to the loaded data.
            ts_limits: Optional dictionary specifying time-stamp limits for filtering the data.

        Returns:
            The dataframe containing the loaded statistic data.
        """

        self._path = path

        _LOG.debug("Loading raw statistics file '%s'", path)
        try:
            df = self._read_stats_file(path)
        except ErrorBadFormat:
            raise
        except Exception as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Unable to load raw statistics file at path '{path}':\n{errmsg}") from err

        if self._ts_colname not in df:
            raise Error(f"Metric '{self._ts_colname}' was not found in statistics file '{path}'.")

        if labels:
            self._apply_labels(df, labels)

        if ts_limits:
            self._apply_ts_limits(df, ts_limits)

        # Remove any 'infinite' values which can appear in raw statistics files.
        df.replace([numpy.inf, -numpy.inf], numpy.nan, inplace=True)
        if df.isnull().values.any():
            _LOG.warning("Dropping one or more 'nan' values from statistics file '%s'", path)
            df.dropna(inplace=True)

            # Some 'pandas' operations break on 'pandas.DataFrame' instances without consistent
            # indexing. Reset the index to avoid any of these problems.
            df.reset_index(inplace=True)

        self.df = df
        return self.df
