
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide a class representing a loaded statistic.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from typing import Any, Union, TypedDict
import pandas
import numpy
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat
from statscollectlibs.dfbuilders import _TurbostatDFBuilder, _InterruptsDFBuilder, _ACPowerDFBuilder
from statscollectlibs.dfbuilders import _IPMIDFBuilder
from statscollectlibs.result.RORawResult import RORawResult
from statscollectlibs.result.LoadedLabels import LoadedLabels
from statscollectlibs.mdc.MDCBase import MDTypedDict

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

DFBuilderType = Union[_TurbostatDFBuilder.TurbostatDFBuilder,
                      _InterruptsDFBuilder.InterruptsDFBuilder,
                      _ACPowerDFBuilder.ACPowerDFBuilder,
                      _IPMIDFBuilder.IPMIDFBuilder]

class LoadedStatsitic:
    """
    The loaded statistic class, represents a single statistics (e.g., turbostat). And there are
    multiple statistics per test result.
    """

    def __init__(self,
                 stname: str,
                 res: RORawResult,
                 ll: LoadedLabels | None = None,
                 cpus: list[int] | None = None):
        """
        Initialize a class instance.

        Args:
            stname: The name of the statistic this object represents.
            res: The raw result object containing the statistics data.
            ll: The loaded labels object for this statistic, or 'None' if there are no labels.
            cpus: List of CPU numbers to include load the statistics for. Default is to load for all
                  CPUs.
        """

        self.stname = stname
        self.res = res
        self.ll = ll
        self.cpus = cpus

        self.ldd: dict[str, MDTypedDict] = {}

        # Name of the dataframe column containing the time since the epoch time-stamps.
        self.ts_colname: str = f"BUG: ts_colname not set for {self.stname}"
        # Name of the dataframe column containing the time elapsed since the beginning of the
        # measurements.
        self.time_colname: str = f"BUG: time_colname not set for {self.stname}"

        self._ts_limits: TimeStampLimitsTypedDict = {}

        self.df = pandas.DataFrame()

        self.mdd: dict[str, MDTypedDict] = {}
        self.categories: dict[str, Any] = {}

    def _apply_labels(self):
        """
        Apply labels to a statistics dataframe.

        Notes:
            - The "skip" lable removes all dataframe rows with timestamps starting from the label's
              timestamp and ending at the "start" label timestamp.
            - The "start" label sets the metrics for all dataframe rows with timestamps starting
              from the label's timestamp and ending at the next label's timestamp.
        """

        if not self.ll:
            return

        labels = self.ll.labels
        ts_col = self.df[self.ts_colname]

        if labels[0]["ts"] > ts_col.iloc[-1]:
            raise Error("Frst label's timestamp is after the last datapoint timestamp")

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
                self.df.drop(self.df.loc[filtered_rows].index, inplace=True)
                continue
            elif label["name"] != "start":
                raise Error(f"BUG: usupported label name {label['name']}")

            if len(filtered_rows) < 1:
                continue

            for metric, val in label.get("metrics", {}).items():
                # Assign 'val' in the column for the label metric for all of the datapoints which
                # 'label' corresponds to.
                self.df.loc[filtered_rows, metric] = val

    def _apply_ts_limits(self):
        """Apply time-stamp limits to the statistics dataframe."""

        if not self._ts_limits:
            return

        if self._ts_limits["absolute"]:
            colname = self.ts_colname
        else:
            colname = self.time_colname

        self.df.drop(self.df.loc[self.df[colname] < self._ts_limits["begin"]].index, inplace=True)
        self.df.drop(self.df.loc[self.df[colname] > self._ts_limits["end"]].index, inplace=True)

        # Normalize the Elapsed time column to start from 0.
        self.df[self.time_colname] -= self.df[self.time_colname].iloc[0]

    def _build_df(self, dfbldr: DFBuilderType):
        """
        Build the statistics dataframe.

        Args:
            dfbldr: The dataframe builder object responsible for loading the data.

        Returns:
            pandas.DataFrame: The constructed dataframe containing the loaded data.
        """

        path = self.res.get_stats_path(self.stname)

        _LOG.debug("Loading raw statistics file '%s'", path)

        try:
            self.df = dfbldr.build_df(path)
        except ErrorBadFormat:
            raise
        except Exception as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Unable to load raw statistics file at path '{path}':\n{errmsg}") from err

        if self.ts_colname not in self.df:
            raise Error(f"Metric '{self.ts_colname}' was not found in statistics file '{path}'.")

        self._apply_labels()

        self._apply_ts_limits()

        # Convert the elapsed time metric to the "datetime" format so that diagrams use a
        # human-readable format.
        self.df[self.time_colname] = pandas.to_datetime(self.df[self.time_colname], unit="s")

        # Remove any 'infinite' values which can appear in raw statistics files.
        self.df.replace([numpy.inf, -numpy.inf], numpy.nan, inplace=True)
        if self.df.isnull().values.any():
            _LOG.warning("Dropping one or more 'nan' values from statistics file '%s'", path)
            self.df.dropna(inplace=True)

        # Some pandas operations break on dataframes without consistent indexing. Reset it.
        self.df = self.df.reset_index(drop=True)

    def load(self):
        """
        Parse and load statistics data and labels, build the dataframe for the statistics. Apply the
        labels and time-stamp limits.
        """

        _LOG.debug(f"Loading statistics '{self.stname}'")

        # Load the lables.
        if self.ll:
            self.ll.load()

        dfbldr: DFBuilderType

        if self.stname == "turbostat":
            dfbldr = _TurbostatDFBuilder.TurbostatDFBuilder(cpus=self.cpus)
        elif self.stname == "interrupts":
            dfbldr = _InterruptsDFBuilder.InterruptsDFBuilder(cpus=self.cpus)
        elif self.stname == "acpower":
            dfbldr = _ACPowerDFBuilder.ACPowerDFBuilder()
        elif self.stname in ("ipmi-inband", "ipmi-oob"):
            dfbldr = _IPMIDFBuilder.IPMIDFBuilder()
        else:
            raise Error(f"Unsupported statistic '{self.stname}'")

        self.ts_colname = dfbldr.ts_colname
        self.time_colname = dfbldr.time_colname

        self._build_df(dfbldr)

        assert dfbldr.mdo is not None
        self.mdd = dfbldr.mdo.mdd
        self.categories = dfbldr.mdo.categories

        if self.ll:
            for lname in self.ldd:
                if lname in self.df:
                    self.mdd[lname] = self.ldd[lname].copy()

    def set_timestamp_limits(self, ts_limits: TimeStampLimitsTypedDict):
        """
        Set time-stamp limits the statistic.

        Restrict the time range of the collected metrics. Raw statistics files typically consist of
        a series of time-stamps and corresponding metric values. By default, the entire time range
        is used from the raw statistics file is loaded. This method enables limiting the range of
        data that will be loaded.

        Args:
            ts_limits: a dictionary including the time-stamp range limits. The dictionary is
                       expected to have the following keys.
                * begin_ts: The start time-stamp. Discards all data collected before this time.
                * end_ts: The end time-stamp. Discards all data collected after this time.
                * absolute: If True, interpret 'begin_ts' and 'end_ts' as absolute time values
                            (local time since the epoch). If False, interpret them as relative
                            values in seconds from the beginning of the measurements.
        """

        # The 'ts_limits' dictionary sanity check.
        for key in ("begin", "end", "absolute"):
            if key not in ts_limits:
                raise Error(f"BUG: bad time-stamp limits dictionary, key {key} is missing")

        if ts_limits["begin"] >= ts_limits["end"]:
            raise Error(f"Bad raw statistics time-stamp limits: begin time-stamp "
                        f"({ts_limits['begin']}) must be smaller than the end time-stamp "
                        f"({ts_limits['end']})")

        self._ts_limits = ts_limits.copy()

    def set_ldd(self, ldd: dict[str, MDTypedDict]):
        """
        Set the labels definition dictionary. It has the same format as MDD, but describes the
        metrics provided by the labels.

        Args:
            ldd: The labels definition dictionary.
        """

        if self.df:
            raise Error(f"Refusing to set labels definition dictionary for already loaded "
                        f"{self.stname} statistics")

        if self.ldd:
            raise Error(f"The labels definition dictionary was already set for the {self.stname} "
                        f"statistics")

        if not self.ll:
            raise Error(f"BUG: Cannot set labels definition dictionary because there are no lables "
                        f"for the {self.stname} statistics")

        self.ldd = ldd
        self.ll.ldd = ldd
