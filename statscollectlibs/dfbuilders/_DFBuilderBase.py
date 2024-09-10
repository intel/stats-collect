# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides a base class that will help child classes to build a 'pandas.DataFrame' out of
a raw statistics file.
"""

import json
import logging
import numpy
import pandas
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound

_LOG = logging.getLogger()

class DFBuilderBase:
    """
    This base class provides common methods that will help child classes to build a
    'pandas.DataFrame' out of a raw statistics file.
    
    This base class requires child classes to implement the following method:
    1. Read a raw statistics file and convert the statistics data into a 'pandas.DataFrame'.
       * '_read_stats_file()'
    """

    def _apply_labels(self, df, labels):
        """
        Apply 'labels' to 'pandas.DataFrame' 'df'. Arguments are as follows:
         * df - the 'pandas.DataFrame' to which the labels should be applied.
         * labels - a list of label dictionaries parsed from the labels file.
        """

        time_col = df[self._time_metric]

        if labels[0]["ts"] > time_col.iloc[-1]:
            raise Error("first label's timestamp is after the last datapoint was measured")

        lcnt = len(labels)
        df["label"] = None

        for i, label in enumerate(labels):
            # 'filtered_rows' contains an index of all of the datapoints which 'label' applies to.
            filtered_rows = time_col >= label["ts"]

            if i < lcnt - 1:
                # Only one label is applicable at a time. Therefore, if there is still at least one
                # label to apply, only apply 'label' to datapoints before the next one is
                # applicable.
                next_label = labels[i + 1]
                filtered_rows &= time_col < next_label["ts"]

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

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw statistics file at
        'path'.
        """

        raise NotImplementedError()

    def _load_labels(self, labels_path):
        """
        Helper function for 'load_df()'. Parses the labels in the file at 'labels_path'. Returns
        a list of label dictionaries.
        """

        try:
            with open(labels_path, "r", encoding="utf-8") as f:
                labels = [json.loads(line) for line in f.readlines()[1:]]
        except OSError as err:
            raise Error(f"unable to parse labels file at path '{labels_path}''") from err

        if not labels:
            raise Error(f"labels file '{labels_path}' does not contain any labels")

        return labels

    def load_df(self, path, labels_path=None):
        """
        Read the data in the raw statistics file into 'self.df'. Arguments are as follows:
         * path - the path of the raw statistics file to load.
         * labels_path - optional path of the labels file to apply to the loaded data. Loads no
                         labels by default.
        """

        if not path.exists():
            raise ErrorNotFound(f"failed to load raw statistics file at path '{path}': file does "
                                f"not exist.")

        if labels_path:
            labels = self._load_labels(labels_path)
        else:
            labels = None

        try:
            sdf = self._read_stats_file(path)
        except Exception as err:
            raise Error(f"unable to load raw statistics file at path '{path}':\n"
                        f"{Error(err).indent(2)}") from None

        # Confirm that the time column is in the 'pandas.DataFrame'.
        if self._time_metric not in sdf:
            raise Error(f"column '{self._time_metric}' not found in statistics file '{path}'.")

        if labels:
            self._apply_labels(sdf, labels)

        # Remove any 'infinite' values which can appear in raw statistics files.
        sdf.replace([numpy.inf, -numpy.inf], numpy.nan, inplace=True)
        if sdf.isnull().values.any():
            _LOG.warning("dropping one or more 'nan' values from statistics file '%s'", path)
            sdf.dropna(inplace=True)

            # Some 'pandas' operations break on 'pandas.DataFrame' instances without consistent
            # indexing. Reset the index to avoid any of these problems.
            sdf.reset_index(inplace=True)

        # Convert Time column from time stamp to time since the first data point was recorded.
        sdf[self._time_metric] = sdf[self._time_metric] - sdf[self._time_metric].iloc[0]
        sdf[self._time_metric] = pandas.to_datetime(sdf[self._time_metric], unit="s")

        self.df = sdf
        return self.df

    def __init__(self, time_metric):
        """
        The class constructor. Arguments are as follows:
         * time_metric - the name of the metric which represents the time at which the datapoints
                         in the raw statistics file(s) were recorded.
        """

        self.df = None
        self._time_metric = time_metric
