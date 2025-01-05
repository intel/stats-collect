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

import json
import logging
import numpy
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat

_LOG = logging.getLogger()

class DFBuilderBase:
    """
    The base class for 'pandas.DataFrame' object builder classes. The goal of dataframe builders is
    to build a 'pandas.DataFrame' object from raw statistics files.

    This base class requires child classes to implement the following methods.
      *  '_read_stats_file()' - read a raw statistics file and convert the statistics data into a
                               'pandas.DataFrame' object.
    """

    def _apply_labels(self, df, labels):
        """
        Apply labels to dataframe 'df'. The arguments are as follows.
          * df - the 'pandas.DataFrame' object to which the labels should be applied.
          * labels - list of label dictionaries.
        """

        ts_col = df[self._ts_colname]

        if labels[0]["ts"] > ts_col.iloc[-1]:
            raise Error("first label's timestamp is after the last datapoint was measured")

        lcnt = len(labels)
        df["label"] = None

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

            if len(filtered_rows) < 1:
                continue

            df["label"] = label.get("name", None)
            for metric, val in label.get("metrics", {}).items():
                # Assign 'val' in the column for the label metric for all of the datapoints which
                # 'label' corresponds to.
                df.loc[filtered_rows, metric] = val

        # Some 'pandas' operations break on 'pandas.DataFrame' instances without consistent
        # indexing. Reset the index to avoid any of these problems.
        df.reset_index(inplace=True)

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

    def _read_stats_file(self, path):
        """
        Return a 'pandas.DataFrame' containing the data stored in the raw statistics file at
        'path'. Must be implemented by child classes.
        """

        raise NotImplementedError()

    def _load_labels(self, labels_path):
        """Parse the labels in the file at 'labels_path'. Return a list of label dictionaries."""

        try:
            with open(labels_path, "r", encoding="utf-8") as f:
                labels = [json.loads(line) for line in f.readlines()[1:]]
        except OSError as err:
            raise Error(f"unable to parse labels file at path '{labels_path}''") from err

        if not labels:
            raise Error(f"labels file '{labels_path}' does not contain any labels")

        return labels

    def load_df(self, path, labels_path=None, ts_limits=None):
        """
        Read the data in the raw statistics file into 'self.df'. The arguments are as follows.
          * path - the path of the raw statistics file to load.
          * labels_path - optional path of the labels file to apply to the loaded data. Loads no
                          labels by default.
          * ts_limits - a dictionary describing the time-stamp limits.

        The following keys are expected to be found in the 'ts_limits' dictionary.
          * begin - the measurements start time-stamps. All data before 'begin' will be discarded.
          * end - the measurements end time-stamp. All data after 'end_ts' will be discarded.
          * absolute - if 'True', then 'begins' and 'end' are absolute time values - the local time
                       since the epoch. Otherwise, they are relative values from the beginning of
                       the measurements in seconds. For example, if 'begin' is 5, this would mean
                       that all metrics collected during the first 5 seconds from the beginning of
                       the measurements should be discarded.
        """

        self._path = path

        if labels_path:
            _LOG.debug("loading labels from '%s'", labels_path)
            labels = self._load_labels(labels_path)
        else:
            labels = None

        _LOG.debug("loading raw statistics file '%s'", path)
        try:
            df = self._read_stats_file(path)
        except ErrorBadFormat:
            raise
        except Exception as err:
            raise Error(f"unable to load raw statistics file at path '{path}':\n"
                        f"{Error(err).indent(2)}") from err

        if self._ts_colname not in df:
            raise Error(f"metric '{self._ts_colname}' was not found in statistics file '{path}'.")

        if labels:
            self._apply_labels(df, labels)

        if ts_limits:
            self._apply_ts_limits(df, ts_limits)

        # Remove any 'infinite' values which can appear in raw statistics files.
        df.replace([numpy.inf, -numpy.inf], numpy.nan, inplace=True)
        if df.isnull().values.any():
            _LOG.warning("dropping one or more 'nan' values from statistics file '%s'", path)
            df.dropna(inplace=True)

            # Some 'pandas' operations break on 'pandas.DataFrame' instances without consistent
            # indexing. Reset the index to avoid any of these problems.
            df.reset_index(inplace=True)

        self.df = df
        return self.df

    def __init__(self, ts_colname, time_colname):
        """
        The class constructor. The arguments are as follows.
          * ts_colname - name of the time since the epoch dataframe column.
          * time_colname - name of the dataframe column for time elapsed since the beginning of the
            measurements.
        """

        self._ts_colname = ts_colname
        self._time_colname = time_colname

        self.df = None
        self._path = None
