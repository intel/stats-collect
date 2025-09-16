
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

import typing
from pathlib import Path
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.result.LoadedLabels import LoadedLabels
from statscollectlibs.result.LoadedStatistic import LoadedStatsitic
from statscollectlibs.result import RORawResult

if typing.TYPE_CHECKING:
    from statscollectlibs.mdc.MDCBase import MDTypedDict
    from statscollectlibs.result.LoadedStatistic import TimeStampLimitsTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

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
            if "MDD" in res.info["wlinfo"]:
                self.lsts[stname].set_ldd(res.info["wlinfo"]["MDD"])


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

        for lst in self.lsts.values():
            lst.set_ldd(ldd)
