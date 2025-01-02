# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""API for reading raw 'stats-collect' test results."""

import logging
from pathlib import Path
from pepclibs.helperlibs import YAML
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported, ErrorNotFound
from statscollectlibs.parsers import SPECjbb2015Parser
from statscollectlibs.helperlibs import ReportID, FSHelpers
from statscollectlibs.rawresultlibs import _RawResultBase
from statscollecttools import ToolInfo

_LOG = logging.getLogger()

# Supported workload types.
SUPPORTED_WORKLOADS = {
    "generic": "generic workload",
    "specjbb2015": "SPECjbb2015 benchmark"
}

class RORawResult(_RawResultBase.RawResultBase):
    """
    A read-only raw test result class. Class API works with the following concepts:
      * labels - labels are created during statistics collection and provide extra information about
                 datapoints.
      * label definitions - dictionaries defining the metrics which label data measure. For example,
                            if a label contains data about power consumption, the label definition
                            might explain that the data is measured in 'Watts'.

    Public methods overview.
      * set_label_defs() - set label definitions for a specific statistic.
      * get_label_defs() - get label definitions for a specific statistic.
      * set_timestamp_limits() - limit time-stamp range for statistics.
      * load_stat() - load and return a 'pandas.DataFrame' containing statistics data for this
                      result.
      * link_wldata() - create a symlink pointing to the workload data.
      * copy_logs() - copy 'stats-collect' tool logs.
      * copy() - copy the test result.
    """

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
        The statistics track metrics for a period of time. Typically raw statistics files include a
        timestamp, and metric values at that time, then ext time-stamp and metric values, and so on.
        In other words, the raw statistics file provide metrics values from time-stamp A to
        time-stamp B. The time-stamp format is local time since the epoch.

        Sometimes it is desirable to limit the time-stamps. For example, if a workload is known to
        have some long and uninteresting preparation phases, it may be desirable to exclude them.
        Provide the new time-stamps A ('begin_ts') and B ('end_ts') to use instead of the full
        time-stamps range from the raw statistics file. The arguments are as follows.
          * begin_ts - the measurements start time-stamps. All data collected before 'begin_ts'
                       will be discarded.
          * end_ts - - the measurements end time-stamp. All data collected after 'end_ts' will be
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

        self._tslimits["begin"] = begin_ts
        self._tslimits["end"] = end_ts
        self._tslimits["absolute"] = absolute

        _LOG.debug("set time-stamp limits for report ID '%s': begin %s, end %s, absolute %s",
                   self.reportid, begin_ts, end_ts, absolute)

    def _get_stats_path(self, stname):
        """
        Return path to the raw statistics file for statistic 'stname'. The arguments are as follows.
          * stname - the name of the statistic for which paths should be found.
        """

        try:
            subpath = self.info["stinfo"][stname]["paths"]["stats"]
        except KeyError:
            raise ErrorNotFound(f"raw '{stname}' statistics file path not found in "
                                f"'{self.info_path}'") from None

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

        path = self._get_stats_path(stname)
        labels_path = self._get_labels_path(stname)
        return dfbldr.load_df(path, labels_path=labels_path)

    def _is_specjbb2015(self):
        """Return 'True' if the workload is SPECjbb2015."""

        # Really basic SPECjbb2015 detection. Obviously needs to be improved.
        path = self.wldata_path / "controller.out"
        if not path.exists():
            return False

        parser = SPECjbb2015Parser.SPECjbb2015Parser(path=path)

        try:
            next(parser.next())
            return True
        except StopIteration:
            raise Error(f"failed to parse SPECjbb2015 controller output file at '{path}'") from None

        return False

    def _detect_wltype(self):
        """
        Detect the workload that was running while the statistics in this raw result were collected.
        """

        try:
            if not self.wldata_path:
                self.wltype = "generic"
            elif self._is_specjbb2015():
                self.wltype = "specjbb2015"
        except (Error, OSError) as err:
            _LOG.warning("workload type detection failed:\n%s", err.indent(2))
            self.wltype = "generic"

        _LOG.debug("%s: workload type is '%s (%s)'",
                   self.reportid, self.wltype, SUPPORTED_WORKLOADS[self.wltype])

    @staticmethod
    def _check_info_yml(dirpath):
        """Raise an exception if an 'info.yml' file exists in 'dirpath'."""

        path = dirpath / "info.yml"

        try:
            exists = path.exists()
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to check if '{path}' exists:\n{msg}") from None

        if not exists:
            return

        raise Error(f"the destination directory '{dirpath}' already contains 'info.yml', refusing "
                    f"to overwrite an existing test result")

    def link_wldata(self, dstpath):
        """
        If the raw results include the workload data sub-directory, create symbolic links pointing
        to the workload data directory.
          * dstpath - path to the directory to create the symbolic link in.
        """

        dstpath = Path(dstpath)

        if self.wldata_path:
            FSHelpers.symlink(dstpath / self.wldata_path.name, self.wldata_path, relative=True)

    def copy_logs(self, dstpath):
        """
        Copy (own) raw test result logs to path 'dirpath'. The arguments are as follows.
          * dstpath - path to the directory to copy the logs to.
        """

        dstpath = Path(dstpath)

        srcpaths = []
        if self.logs_path:
            srcpaths.append(self.logs_path)

        for path in srcpaths:
            FSHelpers.copy(path, dstpath / path.name, is_dir=True)

    def copy(self, dstpath):
        """
        Copy the raw test result (self) to path 'dirpath'. The arguments are as follows.
          * dstpath - path to the directory to copy the result to.
        """

        dstpath = Path(dstpath)
        self._check_info_yml(dstpath)

        srcpaths = [self.info_path]
        if self.logs_path:
            srcpaths.append(self.logs_path)
        if self.wldata_path:
            srcpaths.append(self.wldata_path)

        for path in srcpaths:
            FSHelpers.copy(path, dstpath / path.name)

    def _load_info_yml(self):
        """Load and validate the 'info.yml' file contents."""

        # Check that the 'info.yml' file exists, readable, and not empty.
        for name in ("info_path",):
            path = getattr(self, name)
            try:
                if not path.is_file():
                    raise ErrorNotFound(f"'{path}' does not exist or it is not a regular file")
                if not path.stat().st_size:
                    raise Error(f"file '{path}' is empty")
            except OSError as err:
                msg = Error(err).indent(2)
                raise Error(f"failed to access '{path}':\n{msg}") from err

        self.info = YAML.load(self.info_path)
        if "reportid" not in self.info:
            raise ErrorNotSupported(f"no 'reportid' key found in {self.info_path}")

        toolname = self.info.get("toolname")
        if not toolname:
            raise Error(f"bad '{self.info_path}' format - the 'toolname' key is missing")

        self.reportid = self.info["reportid"]
        if toolname == ToolInfo.TOOLNAME:
            # Validate report ID only if the tool is 'stats-collect'. Make no assumptions about
            # reportID format in case of other tools.
            try:
                ReportID.validate_reportid(self.reportid)
            except Error as err:
                raise Error(f"bad report ID in '{self.info_path}':\n{err.indent(2)}") from err

        toolver = self.info.get("toolver")
        if not toolver:
            raise Error(f"bad '{self.info_path}' format - the 'toolver' key is missing")

        wlinfo = self.info.get("workload")
        if wlinfo:
            path = Path(wlinfo.get("wldata_path"))
            if path:
                if not path.is_absolute():
                    # Assume that the path is relative to the raw results directory path.
                    path = self.dirpath / path
                if not path.is_dir():
                    raise ErrorNotFound(f"bad workload data path in '{self.info_path}':\n"
                                        f" '{path}' does not exist or it is not a directory")
                self.wldata_path = path

            wltype = wlinfo.get("wltype")
            if wltype:
                if wltype not in SUPPORTED_WORKLOADS:
                    _LOG.warning("unsupported workload type '%s' in '%s', assuming generic "
                                 "workload", wltype, self.info_path)
                else:
                    self.wltype = wltype

        if not self.wldata_path:
            # Check the default workload data path.
            path = self.dirpath.joinpath("wldata")
            if path.is_dir():
                self.wldata_path = path

        if self.wltype and not self.wldata_path:
            _LOG.warning("workload type is '%s', but workload data was not found, assuming generic "
                         "workload", SUPPORTED_WORKLOADS[self.wltype])

    def __init__(self, dirpath, reportid=None):
        """
        The class constructor. The arguments are as follows.
          * dirpath - path to the directory containing the raw test result to open.
          * reportid - override the report ID of the raw test result: the 'reportid' string will be
                       used instead of the report ID stored in 'dirpath/info.yml'. Note, the
                       provided report ID is not verified, so the caller has to make sure is a sane
                       string.

        Note, the constructor does not load the potentially huge test result data into the memory.
        It only loads the 'info.yml' file and figures out which metrics have been measured. The data
        are loaded "on-demand" by 'load_stat()' and other methods.
        """

        super().__init__(dirpath)

        if self.info_path.exists() and not self.info_path.is_file():
            raise Error(f"path '{self.info_path}' exists, but it is not a regular file")

        for name in ("logs_path", "stats_path"):
            path = getattr(self, name)
            if path.exists():
                if not path.is_dir():
                    raise Error(f"path '{path}' exists, but it is not a directory")
            else:
                setattr(self, f"{name}", None)

        # Path to the workload data.
        self.wldata_path = None
        # Type of the workload that was running while statistics were collected.
        self.wltype = None

        # Label definitions.
        self._labels_defs = {}

        # The time-stamp limits dictionary.
        self._tslimits = {}

        self._load_info_yml()
        if reportid:
            # Note, we do not validate it here, the caller is supposed to do that.
            self.info["reportid"] = reportid
            self.reportid = reportid

        self._detect_wltype()
