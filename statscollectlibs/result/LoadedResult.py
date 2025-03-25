
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide a class representing a loaded version of the raw test result.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import json
from pathlib import Path
from typing import Any, Union, TypedDict
import pandas
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat, ErrorNotFound
from statscollectlibs.dfbuilders import _TurbostatDFBuilder, _InterruptsDFBuilder, _ACPowerDFBuilder
from statscollectlibs.dfbuilders import _IPMIDFBuilder
from statscollectlibs.result import RORawResult
from statscollectlibs.mdc.MDCBase import MDTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

DFBuilderType = Union[_TurbostatDFBuilder.TurbostatDFBuilder,
                      _InterruptsDFBuilder.InterruptsDFBuilder,
                      _ACPowerDFBuilder.ACPowerDFBuilder,
                      _IPMIDFBuilder.IPMIDFBuilder]
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

class LoadedLabels:
    """The loaded lables file class."""

    def __init__(self, lpath: Path):
        """
        Initialize a class instance.

        Args:
            lpath: Path to the labels file.
        """

        self._lpath = lpath

        self.labels: list[dict[str, str]] = []

        if not self._lpath.exists():
            raise Error(f"Labels file '{lpath}' does not exist")
        if not self._lpath.is_file():
            raise Error(f"Labels file '{lpath}' is not a regular file")

    def load(self):
        """Load the labels from the labels file."""

        _LOG.debug(f"Loading labels from '{self._lpath}'")

        self.labels = []
        try:
            with open(self._lpath, "r", encoding="utf-8") as fobj:
                for line in fobj:
                    if line.startswith("#"):
                        continue

                    try:
                        self.labels.append(json.loads(line))
                    except json.JSONDecodeError as err:
                        line = line.strip()
                        raise ErrorBadFormat(f"Failed to parse JSON in labels file at path "
                                             f"'{self._lpath}'\nThe bad line is: {line}") from err
        except OSError as err:
            raise Error(f"Failed to read and parse labels file at path '{self._lpath}'") from err

        if not self.labels:
            raise Error(f"Labels file '{self._lpath}' does not contain any labels")

class LoadedStatsitic:
    """
    The loaded statistic class, represents a single statistics (e.g., turbostat). And there are
    multiple statistics per test result.
    """

    def __init__(self,
                 stname: str,
                 res: RORawResult.RORawResult,
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
        labels_path = self.res.get_labels_path(self.stname)
        return dfbldr.load_df(path, labels_path=labels_path, ts_limits=self._ts_limits)

    def load(self):
        """
        Parse and load statistics data and labels, build the dataframe for the statistics. Apply the
        labels and time-stamp limits.
        """

        _LOG.debug(f"Loading statistics '{self.stname}'")

        # Load the lables.
        if self.ll:
            self.ll.load()

        if self.stname == "turbostat":
            turbostat_dfbldr = _TurbostatDFBuilder.TurbostatDFBuilder(cpus=self.cpus)
            self.df = self._build_df(turbostat_dfbldr)

            assert turbostat_dfbldr.mdo is not None
            self.mdd = turbostat_dfbldr.mdo.mdd
            self.categories = turbostat_dfbldr.mdo.categories
        elif self.stname == "interrupts":
            interrupts_dfbldr = _InterruptsDFBuilder.InterruptsDFBuilder(cpus=self.cpus)
            self.df = self._build_df(interrupts_dfbldr)

            assert interrupts_dfbldr.mdo is not None
            self.mdd = interrupts_dfbldr.mdo.mdd
        elif self.stname == "acpower":
            acpower_dfbldr = _ACPowerDFBuilder.ACPowerDFBuilder()
            self.df = self._build_df(acpower_dfbldr)

            assert acpower_dfbldr.mdo is not None
            self.mdd = acpower_dfbldr.mdo.mdd

        elif self.stname in ("ipmi-inband", "ipmi-oob"):
            ipmi_dfbldr = _IPMIDFBuilder.IPMIDFBuilder()
            self.df = self._build_df(ipmi_dfbldr)

            assert ipmi_dfbldr.mdo is not None
            self.mdd = ipmi_dfbldr.mdo.mdd
            self.categories = ipmi_dfbldr.mdo.categories
        else:
            raise Error(f"Unsupported statistic '{self.stname}'")

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

class LoadedResult:
    """The loaded version of a raw test result."""

    def __init__(self, res: RORawResult.RORawResult, cpus: list[int] | None = None):
        """
        Initialize a class instance.

        Args:
            res: a read-only raw test result object that will be loaded and represented by this
                 object.
            cpus: List of CPU numbers to include load the statistics for. Default is to load for all
                  CPUs.
        """

        self.res = res
        self.cpus = cpus

        self.reportid = self.res.reportid

        # Tha labels metrics definition dictionary.
        self.lmdd: dict[str, MDTypedDict] = {}

        # Note. The lables files include data for multiple statsistics, and they are per-statistics
        # collection agent (stc-agent), so there may be only one or 2 labels files (for local
        # stc-agent and remote stc-agent). Therefor, there are at max. two "Lablels" objects.
        self.lls: dict[str, LoadedLabels] = {}

        # Loaded statistics.
        self.lsts: dict[str, LoadedStatsitic] = {}

        # Map labels file paths to 'LoadedLabels' objects.
        lpath2lls: dict[Path, LoadedLabels] = {}

        # Build the loaded lables objects, but do not actually load them yet.
        for stname, stinfo in self.res.info["stinfo"].items():
            if "labels" not in stinfo["paths"]:
                continue

            path = self.res.dirpath / stinfo["paths"]["labels"]

            if path not in lpath2lls:
                lpath2lls[path] = LoadedLabels(path)

            self.lls[stname] = lpath2lls[path]

        if len(lpath2lls) > 2:
            raise Error(f"Too many labels files, expected max. 2 files, got "
                        f"{len(lpath2lls)}")

        # Build the loaded statistics objects, but do not actually load them yet.
        for stname, stinfo in self.res.info["stinfo"].items():
            self.lsts[stname] = LoadedStatsitic(stname, self.res, ll=self.lls.get(stname),
                                                cpus=self.cpus)

    def load_stat(self, stname: str) -> LoadedStatsitic:
        """
        Parse the raw statistics file and build pandas dataframe.

        Args:
            stname: The name of the statistic to load the data frame for.

        Returns:
            LoadedStatsitic: The loaded statistic object containing the parsed data.
        """

        if stname not in self.lsts:
            raise ErrorNotFound(f"Statistic '{stname}' not found in result '{self.reportid}' at "
                                f"'{self.res.dirpath}")

        self.lsts[stname].load()
        return self.lsts[stname]

    def set_timestamp_limits(self, ts_limits: TimeStampLimitsTypedDict):
        """
        Set time-stamp limits for all statistics in the loaded result. Refer to
        'LoadedStatsitic.set_timestamp_limits()' for details.

        Args:
            ts_limits: a dictionary including the time-stamp range limits.
        """

        _LOG.debug("Set time-stamp limits for report ID '%s': begin %s, end %s, absolute %s",
                   self.reportid, ts_limits["begin"], ts_limits["end"], ts_limits["absolute"])

        for lst in self.lsts.values():
            lst.set_timestamp_limits(ts_limits)

    def set_labels_mdd(self, lmdd: dict[str, MDTypedDict]):
        """
        Set the labels metrics definition dictionary.

        Args:
            lmdd: The labels metrics definition dictionary.
        """

        self.lmdd = lmdd
