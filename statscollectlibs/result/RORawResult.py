# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the read-only 'stats-collect' raw result class."""

 # TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

from typing import TypedDict
from pathlib import Path
from pepclibs.helperlibs import Logging, Trivial, YAML
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorBadFormat
from statscollectlibs.parsers import SPECjbb2015CtrlOutParser, SPECjbb2015CtrlLogParser
from statscollectlibs.helperlibs import FSHelpers
from statscollectlibs.result import _RawResultBase
from statscollectlibs.result._RawResultBase import RawResultWLInfoTypedDict
from statscollectlibs.mdc.MDCBase import MDTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

# Supported workload types.
SUPPORTED_WORKLOADS = {
    "generic": "generic workload",
    "specjbb2015": "SPECjbb2015 benchmark"
}

class _TimeStampRangeTypedDict(TypedDict, total=False):
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

def reportids_dedup(rsts: list[RORawResult]):
    """
    Deduplicate report IDs by appending '-X' to the duplicates, where 'X' is an integer. Modify the
    'reportid' attribut of the raw test results objects in-place.

    Args:
        rsts: A list of test results objects ('RORawResult') to de-duplicate the report IDs for.
    """

    reportids = set()
    for res in rsts:
        reportid = res.reportid
        if reportid in reportids:
            # Try to construct a unique report ID.
            for idx in range(1, 20):
                new_reportid = f"{reportid}-{idx:02}"
                if new_reportid not in reportids:
                    _LOG.warning("Duplicate reportid '%s', using '%s' instead",
                                 reportid, new_reportid)
                    res.reportid = new_reportid
                    break
            else:
                raise Error(f"Too many duplicate report IDs, e.g., '{reportid}' is problematic")

        reportids.add(res.reportid)
class RORawResult(_RawResultBase.RawResultBase):
    """The read-only 'stats-collect' raw result class."""

    def __init__(self, dirpath: Path, reportid: str | None = None):
        """
        Initialize a class instance.

        Args:
            dirpath: Path to the directory containing the raw test result to initalize a class
                     instance for.
            reportid: Override the report ID of the raw test result. If provided, it will be used
                      instead of the report ID stored in "dirpath/info.yml". The provided report ID
                      is not validated, so the caller must ensure it has format.
        """

        super().__init__(dirpath)

        # Basic 'info.yml' file check.
        if not self.info_path.exists():
            raise ErrorNotFound(f"No 'info.yml' file found in '{self.dirpath}'")
        if not self.info_path.is_file():
            raise ErrorBadFormat(f"Path '{self.info_path}' exists, but it is not a regular file")
        if not self.info_path.stat().st_size:
            raise ErrorBadFormat(f"File '{self.info_path}' is empty")

        # Basic 'logs' and 'stats' sub-directories check (they do not have to exist).
        if self.logs_path and self.logs_path.exists():
            if not self.logs_path.is_dir():
                raise ErrorBadFormat(f"The '{self.logs_path}' logs path has to be a directory")
        else:
            self.logs_path = None

        if self.stats_path and self.stats_path.exists():
            if not self.stats_path.is_dir():
                raise ErrorBadFormat(f"The '{self.stats_path}' statistics path has to be a "
                                     f"directory")
        else:
            self.stats_path = None

        # Path to the workload data.
        self.wldata_path: Path | None = None
        # Type of the workload that was running while statistics were collected.
        self.wltype = ""

        # Label definitions.
        self._labels_defs: dict[str, MDTypedDict] = {}

        # The time-stamp range dictionary.
        self._ts_range: _TimeStampRangeTypedDict = {}

        self._load_info_yml()

        if reportid:
            self.info["reportid"] = reportid

        self.reportid = self.info["reportid"]

        if not self.wltype:
            self._detect_wltype()

    def set_label_defs(self, stname, defs):
        """
        Set label definitions. The arguments are as follows.
          * stname - name of the statistics to set label for.
          * defs - the definitions to set for the label.
        """

        self._labels_defs[stname] = defs

    def get_label_defs(self, stname):
        """
        Return label definitions. The arguments are as follows.
          * stname - name of the statistics to return the label definitions for.
        """

        return self._labels_defs.get(stname, {})

    def set_timestamp_limits(self, begin_ts, end_ts, absolute=True):
        """
        The statistics track metrics over a period of time. Typically raw statistics files include a
        timestamp, and metric values at that time, then ext time-stamp and metric values, and so on.
        In other words, the raw statistics file provide metrics values from time-stamp A to
        time-stamp B. The time-stamp format is local time since the epoch.

        Sometimes it is desirable to limit the time-stamps. For example, if a workload is known to
        have some long and uninteresting preparation phases, it may be desirable to exclude them.
        Provide the new time-stamps A ('begin_ts') and B ('end_ts') to use instead of the full
        time-stamps range from the raw statistics file. The arguments are as follows.
          * begin_ts - the measurements start time-stamps. All data collected before 'begin_ts'
                       will be discarded.
          * end_ts - the measurements end time-stamp. All data collected after 'end_ts' will be
                     discarded.
          * absolute - if 'True', then 'begin_ts' and 'end_ts' are absolute time values - the local
                       time since the epoch. Otherwise, they are relative values from the beginning
                       of the measurements in seconds. For example, if 'begin_ts' is 5, this would
                       mean that all metrics collected during the first 5 seconds from the beginning
                       of the measurements should be discarded.
        """

        if begin_ts >= end_ts:
            raise Error(f"bad raw statistics time-stamp limits: begin time-stamp ({begin_ts}) must "
                        f"be smaller than the end time-stamp ({end_ts})")

        self._ts_range["begin"] = begin_ts
        self._ts_range["end"] = end_ts
        self._ts_range["absolute"] = absolute

        _LOG.debug("set time-stamp limits for report ID '%s': begin %s, end %s, absolute %s",
                   self.reportid, begin_ts, end_ts, absolute)

    def get_stats_path(self, stname):
        """
        Return path to the raw statistics file for statistic 'stname'. The arguments are as follows.
          * stname - the name of the statistic for which paths should be found.
        """

        try:
            subpath = self.info["stinfo"][stname]["paths"]["stats"]
        except KeyError:
            raise ErrorNotFound(f"raw '{stname}' statistics file path not found in "
                                f"'{self.info_path}'") from None

        if not self.stats_path:
            raise ErrorNotFound(f"'{self.dirpath}' does not have the statistics sub-directory")

        path = self.stats_path / subpath
        if path.exists():
            return path

        raise ErrorNotFound(f"raw '{stname}' statistics file not found at path: {path}")

    def _get_labels_path(self, stname):
        """Return path to the labels file for statistic 'stname'."""

        try:
            subpath = self.info["stinfo"][stname]["paths"]["labels"]
        except KeyError:
            return None

        path = self.dirpath / subpath
        if path.exists():
            return path

        raise ErrorNotFound(f"no labels file found for statistic '{stname}' at path: {path} '")

    def load_stat(self, stname, dfbldr):
        """
        Load data for statistic 'stname'. Returns a 'pandas.DataFrame' containing statistics data.
        The arguments are as follows.
          * stname - the name of the statistic for which a 'pandas.DataFrame' should be retrieved.
          * dfbldr - an instance of '_DFBuilderBase.DFBuilderBase' to use to build a
                     'pandas.DataFrame' from the raw statistics file.
        """

        path = self.get_stats_path(stname)
        labels_path = self._get_labels_path(stname)
        return dfbldr.load_df(path, labels_path=labels_path, ts_limits=self._ts_range)

    def _is_specjbb2015(self) -> bool:
        """
        Determine if the workload is SPECjbb2015.

        Returns:
            bool: True if the workload is identified as SPECjbb2015, False otherwise.
        """

        if not self.wldata_path:
            return False

        # Both SPECjbb2015 controller log and stdout outputs are necessary.
        stdout_path = self.wldata_path / "controller.out"
        if not stdout_path.exists():
            return False

        log_path = self.wldata_path / "controller.log"
        if not log_path.exists():
            return False

        stdout_parser = SPECjbb2015CtrlOutParser.SPECjbb2015CtrlOutParser(path=stdout_path)
        log_parser = SPECjbb2015CtrlLogParser.SPECjbb2015CtrlLogParser(path=log_path)

        try:
            stdout_parser.probe()
            return log_parser.probe()
        except ErrorBadFormat as err:
            _LOG.debug("SPECjbb2015 probe is negative: %s", err)
            return False

    def _detect_wltype(self):
        """
        Detect the type of workload that was running during the collection of statistics in this raw
        result.
        """

        self.wltype = "generic"

        # Check the default workload data path.
        path = self.dirpath.joinpath("wldata")
        if not path.exists():
            return

        if not path.is_dir():
            raise ErrorBadFormat(f"Bad workload data path in '{path}' - not a directory")

        self.wldata_path = path

        try:
            if self._is_specjbb2015():
                self.wltype = "specjbb2015"
        except (Error, OSError) as err:
            _LOG.warning("workload type detection failed:\n%s", Error(str(err)).indent(2))

        _LOG.debug("%s: workload type is '%s (%s)'",
                   self.reportid, self.wltype, SUPPORTED_WORKLOADS[self.wltype])

    def link_wldata(self, dstpath: Path):
        """
        Create a symbolic link to the workload data directory.

        Args:
            dstpath: The destination directory where the symbolic link will be created.
        """

        if self.wldata_path:
            FSHelpers.symlink(dstpath / self.wldata_path.name, self.wldata_path, relative=True)

    def copy_logs(self, dstpath: Path):
        """
        Copy the raw test result logs associated with this class instance to the specified
        directory.

        Args:
            dstpath: The destination directory where the logs will be copied.
        """

        srcpaths = []
        if self.logs_path:
            srcpaths.append(self.logs_path)

        for path in srcpaths:
            FSHelpers.copy(path, dstpath / path.name, is_dir=True)

    @staticmethod
    def _check_info_yml(dirpath: Path):
        """
        Ensure that the specified directory does not contain an 'info.yml' file.

        Args:
            dirpath: The path to the directory to check.
        """

        path = dirpath / "info.yml"

        try:
            exists = path.exists()
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"failed to check if '{path}' exists:\n{errmsg}") from None

        if not exists:
            return

        raise Error(f"the destination directory '{dirpath}' already contains 'info.yml', refusing "
                    f"to overwrite an existing test result")

    def copy(self, dstpath: Path):
        """
        Copy the raw test result to the specified destination directory.

        Args:
            dstpath: The destination directory where the raw test result will be copied.
        """

        self._check_info_yml(dstpath)

        srcpaths = [self.info_path]
        if self.stats_path:
            srcpaths.append(self.stats_path)
        if self.logs_path:
            srcpaths.append(self.logs_path)
        if self.wldata_path:
            srcpaths.append(self.wldata_path)

        for path in srcpaths:
            FSHelpers.copy(path, dstpath / path.name)

    def _validate_wlinfo(self, wlinfo: RawResultWLInfoTypedDict):
        """
        Validate the workload information provided in the 'info.yml' file.

        Args:
            wlinfo: A dictionary containing workload information from 'info.yml'.
        """

        if "wldata_path" not in wlinfo:
            raise ErrorBadFormat(f"Bad '{self.info_path}' format - the 'workload.wldata_path' key "
                                 f"is missing")

        self.wldata_path = Path(wlinfo["wldata_path"])

        if not self.wldata_path:
            raise ErrorBadFormat(f"Bad workload data path in '{self.info_path}' - "
                                 f"'workload.wldata_path' is empty")

        if not self.wldata_path.is_absolute():
            # Assume that the path is relative to the raw results directory path.
            self.wldata_path = self.dirpath / self.wldata_path

        if not self.wldata_path.is_dir():
            raise ErrorBadFormat(f"Bad workload data path in '{self.info_path}':\n"
                                 f"  '{self.wldata_path}' does not exist or it is not a directory")

        wlinfo["wldata_path"] = self.wldata_path

        if "wltype" not in wlinfo:
            raise ErrorBadFormat(f"Bad '{self.info_path}' format - the 'workload.wltype' key is "
                                 f"missing")

        self.wltype = wlinfo["wltype"]
        if not self.wltype:
            raise ErrorBadFormat(f"Bad workload type in '{self.info_path}':\n"
                                 f"  'workload.wltype' is empty")

        if self.wltype not in SUPPORTED_WORKLOADS:
            raise ErrorBadFormat(f"Unsupported workload type '{self.wltype}' in '{self.info_path}'")

    def _load_info_yml(self):
        """Load and validate the contents of the 'info.yml' file."""

        info = YAML.load(self.info_path)

        for key in ("toolname", "toolver", "reportid"):
            if key not in info:
                raise ErrorBadFormat(f"Bad '{self.info_path}' format - the '{key}' key is missing")
            if not info[key]:
                raise ErrorBadFormat(f"Bad '{self.info_path}' format - the '{key}' key is empty")

        # TODO: Compatibility code. Remove in 2026. In version 1.0.47 the "cpunum" key was renamed
        # to "cpus".
        if "cpunum" in info:
            info["cpus"] = info.pop("cpunum")
        if info.get("cpus"):
            what=f"'cpus' key in '{self.info_path}'"
            info["cpus"] = Trivial.split_csv_line_int(info["cpus"], what=what)

        if "wlinfo" in info:
            self._validate_wlinfo(info["wlinfo"])

        self.info = info
