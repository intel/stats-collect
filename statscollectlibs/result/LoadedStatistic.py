
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

from typing import Any, Union
import pandas
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.dfbuilders import _TurbostatDFBuilder, _InterruptsDFBuilder, _ACPowerDFBuilder
from statscollectlibs.dfbuilders import _IPMIDFBuilder
from statscollectlibs.dfbuilders._DFBuilderBase import TimeStampLimitsTypedDict
from statscollectlibs.dfbuilders._DFBuilderBase import LoadedLablesTypedDict
from statscollectlibs.result.RORawResult import RORawResult
from statscollectlibs.result.LoadedLabels import LoadedLabels
from statscollectlibs.mdc.MDCBase import MDTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

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
        self.ts_colname: str | None = None
        # Name of the dataframe column containing the time elapsed since the beginning of the
        # measurements.
        self.time_colname: str | None = None

        self._ts_limits: TimeStampLimitsTypedDict = {}

        self.df = pandas.DataFrame()

        self.mdd: dict[str, MDTypedDict] = {}
        self.categories: dict[str, Any] = {}

    def _build_df(self, dfbldr: DFBuilderType) -> pandas.DataFrame:
        """
        Build and return a pandas DataFrame using the provided dataframe builder.

        Args:
            dfbldr: The dataframe builder object responsible for loading the data.

        Returns:
            pandas.DataFrame: The constructed dataframe containing the loaded data.
        """

        path = self.res.get_stats_path(self.stname)
        labels: list[LoadedLablesTypedDict] | None  = None
        if self.ll:
            labels = self.ll.labels
        return dfbldr.load_df(path, labels=labels, ts_limits=self._ts_limits)

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

        self.df = self._build_df(dfbldr)

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

        if self.mdd:
            # Do not allow setting lables if they were already set and used for building the MDD.
            raise Error(f"The labels definition dictionary was already set for the {self.stname} "
                        f"statistics")

        if not self.ll:
            raise Error(f"BUG: Cannot set labels definition dictionary because there are no lables "
                        f"for the {self.stname} statistics")

        self.ldd = ldd
        self.ll.ldd = ldd
