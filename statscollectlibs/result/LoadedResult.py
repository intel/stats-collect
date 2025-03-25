
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
from typing import Any, Union
import pandas
from pepclibs.helperlibs import Logging, Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat, ErrorNotFound
from statscollectlibs.dfbuilders import _TurbostatDFBuilder, _InterruptsDFBuilder, _ACPowerDFBuilder
from statscollectlibs.dfbuilders import _IPMIDFBuilder
from statscollectlibs.dfbuilders._DFBuilderBase import TimeStampLimitsTypedDict
from statscollectlibs.dfbuilders._DFBuilderBase import LoadedLablesTypedDict
from statscollectlibs.result import RORawResult
from statscollectlibs.mdc.MDCBase import MDTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

DFBuilderType = Union[_TurbostatDFBuilder.TurbostatDFBuilder,
                      _InterruptsDFBuilder.InterruptsDFBuilder,
                      _ACPowerDFBuilder.ACPowerDFBuilder,
                      _IPMIDFBuilder.IPMIDFBuilder]
class LoadedLabels:
    """The loaded lables file class."""

    def __init__(self, lpath: Path):
        """
        Initialize a class instance.

        Args:
            lpath: Path to the labels file.
        """

        self._lpath = lpath

        self.ldd: dict[str, MDTypedDict] = {}
        self.labels: list[LoadedLablesTypedDict] = []

        self._allowed_label_keys = set(LoadedLablesTypedDict.__annotations__.keys())

        if not self._lpath.exists():
            raise Error(f"Labels file '{lpath}' does not exist")
        if not self._lpath.is_file():
            raise Error(f"Labels file '{lpath}' is not a regular file")

    def _validate_label(self, label: LoadedLablesTypedDict, lnum: int, line: str):
        """
        Validate the label dictionary.

        Args:
            label: The label dictionary to validate.
            lnum: The line number in the labels file where the label was read from.
            line: The JSON line that was read from the labels file and parsed into 'label'.

        Raises:
            ErrorBadFormat: If the label is invalid.
        """

        if not isinstance(label, dict):
            raise ErrorBadFormat(f"Label at line {lnum} in '{self._lpath}' is not a dictionary\n"
                                 f"The bad line is: {line}")

        for key, value in label.items():
            if not isinstance(key, str):
                raise ErrorBadFormat(f"Label key at line {lnum} in '{self._lpath}' is not a "
                                     f"string\nThe bad line is: {line}")

            if key not in self._allowed_label_keys:
                allowed = ", ".join(self._allowed_label_keys)
                raise ErrorBadFormat(f"Label key '{key}' at line {lnum} in '{self._lpath}' is not "
                                     f"allowed\nThe allowed keys are: {allowed}\n"
                                     f"The bad line is: {line}")

        # Validate the label name.
        if "name" not in label:
            raise ErrorBadFormat(f"Label at line {lnum} in '{self._lpath}' does not contain a "
                                 f"'name' key\nThe bad line is: {line}")

        supported_names = ("start", "skip")
        if label["name"] not in supported_names:
            supported = ", ".join(supported_names)
            raise ErrorBadFormat(f"Label at line {lnum} in '{self._lpath}' has an unsupported "
                                 f"name '{label['name']}'\nThe supported names are: {supported}.\n"
                                 f"The bad line is: {line}")

        # Validate label timestamp.
        if "ts" not in label:
            raise ErrorBadFormat(f"Label at line {lnum} in '{self._lpath}' does not contain a "
                                 f"'ts' key\nThe bad line is: {line}")

        if not isinstance(label["ts"], (int, float)):
            raise ErrorBadFormat(f"Label time-stamp at line {lnum} in '{self._lpath}' is not an "
                                 f"integer or a float\nThe bad line is: {line}")


        if label["name"] == "skip":
            return

        # Validate the "start" label metrics.
        if "metrics" not in label:
            return

        for metric, value in label["metrics"].items():
            if metric not in self.ldd:
                raise ErrorBadFormat(f"Label metric '{metric}' at line {lnum} in '{self._lpath}' "
                                     f"does not have a corresponding metric definition\nThe bad "
                                     f"line is: {line}")
            if not isinstance(metric, str):
                raise ErrorBadFormat(f"Label metric at line {lnum} in '{self._lpath}' is not a "
                                     f"string\nThe bad line is: {line}")
            if not Trivial.is_num(value):
                raise ErrorBadFormat(f"Metric {metric} value at line {lnum} in '{self._lpath}' is "
                                     f"not a number\nThe bad line is: {line}")

    def load(self):
        """Load the labels from the labels file."""

        _LOG.debug(f"Loading labels from '{self._lpath}'")

        if not self.ldd:
            raise Error(f"Cannot load lables from '{self._lpath}' because the labels definition "
                        f"dictionary was not set")
        try:
            with open(self._lpath, "r", encoding="utf-8") as fobj:
                for lnum, line in enumerate(fobj):
                    if line.startswith("#"):
                        continue

                    try:
                        label = json.loads(line)
                    except json.JSONDecodeError as err:
                        line = line.strip()
                        raise ErrorBadFormat(f"Failed to parse JSON in labels file at path "
                                             f"'{self._lpath}'\nThe bad line is: {line}") from err

                    self._validate_label(label, lnum, line)
                    self.labels.append(label)
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
        self.ldd: dict[str, MDTypedDict] = {}

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
        self.ldd: dict[str, MDTypedDict] = {}

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

    def set_ldd(self, ldd: dict[str, MDTypedDict]):
        """
        Set the labels definition dictionary. It has the same format as MDD, but describes the
        metrics provided by the labels.

        Args:
            ldd: The labels definition dictionary.
        """

        self.ldd = ldd
        for lst in self.lsts.values():
            lst.set_ldd(ldd)
