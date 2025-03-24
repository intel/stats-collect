
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
from typing import Any
import pandas
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat
from statscollectlibs.result import RORawResult
from statscollectlibs.mdc.MDCBase import MDTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

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

        self.df = pandas.DataFrame()

        self.mdd: dict[str, MDTypedDict] = {}
        self.categories: dict[str, Any] = {}

    def load(self):
        """TODO"""

        _LOG.debug(f"Loading statistics '{self.stname}'")

        # Load the lables.
        if self.ll:
            self.ll.load()

        # pylint: disable=import-outside-toplevel
        if self.stname == "turbostat":
            from statscollectlibs.dfbuilders import _TurbostatDFBuilder

            turbostat_dfbldr = _TurbostatDFBuilder.TurbostatDFBuilder(cpus=self.cpus)
            self.df = self.res.load_stat(self.stname, turbostat_dfbldr)

            assert turbostat_dfbldr.mdo is not None
            self.mdd = turbostat_dfbldr.mdo.mdd
            self.categories = turbostat_dfbldr.mdo.categories
        elif self.stname == "interrupts":
            from statscollectlibs.dfbuilders import _InterruptsDFBuilder

            interrupts_dfbldr = _InterruptsDFBuilder.InterruptsDFBuilder(cpus=self.cpus)
            self.df = self.res.load_stat(self.stname, interrupts_dfbldr)

            assert interrupts_dfbldr.mdo is not None
            self.mdd = interrupts_dfbldr.mdo.mdd
        elif self.stname == "acpower":
            from statscollectlibs.dfbuilders import _ACPowerDFBuilder

            acpower_dfbldr = _ACPowerDFBuilder.ACPowerDFBuilder()
            self.df = self.res.load_stat(self.stname, acpower_dfbldr)

            assert acpower_dfbldr.mdo is not None
            self.mdd = acpower_dfbldr.mdo.mdd

        elif self.stname in ("ipmi-inband", "ipmi-oob"):
            from statscollectlibs.dfbuilders import _IPMIDFBuilder

            ipmi_dfbldr = _IPMIDFBuilder.IPMIDFBuilder()
            self.df = self.res.load_stat(self.stname, ipmi_dfbldr)

            assert ipmi_dfbldr.mdo is not None
            self.mdd = ipmi_dfbldr.mdo.mdd
            self.categories = ipmi_dfbldr.mdo.categories
        else:
            raise Error(f"Unsupported statistic '{self.stname}'")

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

    def load_stat(self, stname: str):
        """
        Parse the raw statistics file and build pandas dataframe.

        Args:
            stname: The name of the statistic to load the data frame for.
        """

        if stname not in self.lsts:
            return

        self.lsts[stname].load()
