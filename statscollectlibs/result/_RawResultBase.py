# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the base class for raw test result classes.

A raw test result is a directory containing the following files:
 * info.yml - a YAML file containing miscellaneous test information, such as the report ID.
 * logs - an optional directory for workload logs.
 * stats - an optional directory containing raw statistics data, such as turbostat.

A raw result class is a class representing a raw result directory and its contents.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from typing import TypedDict, Literal
from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error

# The latest supported raw results directory format version.
FORMAT_VERSION = "1.3"

# The supported keys in the 'stinfo.name.paths' dictionary of the 'info.yml' files. These are paths
# to the raw statistics file and the labels file.
RawResultSTInfoPathsType = Literal["stats", "labels"]
class RawResultSTInfoTypedDict(TypedDict, total=False):
    """
    A typed dictionary representing the statistics information from of the 'info.yml' file.

    Attributes:
        interval: The interval between statistics snapshots, seconds.
        inband: Whether the statistics were collected in-band (the collector tool was running on the
                SUT, e.g., turbostat) or out-of-band (the collector tool was running on the
                controlling machine, e.g., ipmi-oob statistics collected by 'ipmitool' running on
                the controller and reading SUT data over the network from SUT's BMC).
        toolpath: The file path to the tool used for data collection on the SUT in case of an
                  in-band collector, and on the controller in case of an out-of-band collector.
        description: A brief description of the statistics data.
        paths: A dictionary containing paths to raw statistics data files.
    """

    interval: float
    inband: bool
    toolpath: Path
    description: str
    paths: dict[RawResultSTInfoPathsType, Path]

class RawResultWLInfoTypedDict(TypedDict, total=False):
    """
    A typed dictionary representing workload information in the 'info.yml' file of a raw test
    result. This information is applicable only for certain workloads supported by this project.

    Attributes:
        wldata_path: The file system path to the workload data directory.
        wltype: The type of the workload.
    """

    wldata_path: Path
    wltype: str

class RawResultInfoTypedDict(TypedDict, total=False):
    """
    A type representing contents of the 'info.yml' file of a raw test result.

    Attributes:
        toolname: The name of the tool used to generate the raw test result.
        toolver: The version of the tool.
        reportid: A unique identifier for the raw test result, also referred to as "report ID".
        wlinfo: Workload information associated with the raw test result. Applicable only for
                certain workloads supported by this project. None of unsupported ("generic")
                workloads.
    """

    toolname: str
    toolver: str
    reportid: str
    stinfo: dict[str, RawResultSTInfoTypedDict]
    wlinfo: RawResultWLInfoTypedDict | None

class RawResultBase:
    """Base class for raw test result classes."""

    def __init__(self, dirpath: Path):
        """
        Initialize a class instance.

        Args:
            dirpath: Path to the raw test result directory.
        """

        self.reportid = ""

        # This dictionary represents the info file.
        self.info: RawResultInfoTypedDict = {}

        if not dirpath:
            raise Error("Raw test results directory path was not specified")

        self.dirpath = dirpath

        if self.dirpath.exists() and not self.dirpath.is_dir():
            raise Error(f"Path '{self.dirpath}' is not a directory")

        # These are the paths that are used for the corresponding files/directories. But they do not
        # have to exist at the moment this class is created.
        self.info_path: Path = self.dirpath.joinpath("info.yml")
        self.logs_path: Path | None = self.dirpath.joinpath("logs")
        self.stats_path: Path | None = self.dirpath.joinpath("stats")
