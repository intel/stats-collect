# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the read-only 'stats-collect' raw result class."""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from pepclibs.helperlibs import Logging, YAML
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorBadFormat
from statscollectlibs.parsers import SPECjbb2015CtrlOutParser, SPECjbb2015CtrlLogParser
from statscollectlibs.helperlibs import FSHelpers
from statscollectlibs.result import _RawResultBase
from statscollectlibs.result._RawResultBase import RawResultSTInfoTypedDict
from statscollectlibs.result._RawResultBase import RawResultWLInfoTypedDict
from statscollectlibs.mdc import MDCBase
from statscollectlibs.mdc.MDCBase import MDTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

KNOWN_WORKLOADS = {
    "specjbb2015": "SPECjbb2015 benchmark"
}

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
        self.wlname = ""

        self._load_info_yml()

        if reportid:
            self.info["reportid"] = reportid

        self.reportid = self.info["reportid"]

        if not self.wlname:
            self._detect_workload()

    def get_stats_path(self, stname: str) -> Path:
        """
        Return the path to the raw statistics file for a given statistic.

        Args:
            stname: The name of the statistic for which the path should be returned.

        Returns:
            Path: The path to the raw statistics file.

        Raises:
            ErrorNotFound: If the statistic raw result does not include the statistics of the raw
                           statistics file.
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

    def get_labels_path(self, stname: str) -> Path | None:
        """
        Return the path to the labels file for the specified statistic. Note, label files are
        actually not per-statistic, but per statistic collector. So multiple statistics may share
        the same labels file.

        Args:
            stname: The name of the statistic for which to return the labels file path.

        Returns:
            Path: The path to the labels file or None if there are no labels for 'stname'.

        Raises:
            ErrorNotFound: If the labels file is expected to exist, but it does not.
        """

        try:
            subpath = self.info["stinfo"][stname]["paths"]["labels"]
        except KeyError:
            return None

        path = self.dirpath / subpath
        if path.exists():
            return path

        raise ErrorNotFound(f"no labels file found for statistic '{stname}' at path: {path} '")

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

    def _detect_workload(self):
        """
        Detect what workload that was running during the collection of statistics in this raw
        result.
        """

        self.wlname = "generic"

        # Check the default workload data path.
        path = self.dirpath.joinpath("wldata")
        if not path.exists():
            return

        if not path.is_dir():
            raise ErrorBadFormat(f"Bad workload data path in '{path}' - not a directory")

        self.wldata_path = path

        try:
            if self._is_specjbb2015():
                self.wlname = "specjbb2015"
        except (Error, OSError) as err:
            _LOG.warning("workload detection failed:\n%s", Error(str(err)).indent(2))

        _LOG.debug("%s: workload is '%s (%s)'",
                   self.reportid, self.wlname, KNOWN_WORKLOADS[self.wlname])

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

    def _validate_stinfo(self, stinfo: dict[str, RawResultSTInfoTypedDict]) -> \
                                                        dict[str, RawResultSTInfoTypedDict]:
        """
        Validate the statistics information dictionary from the 'info.yml' file.

        Args:
            stinfo: A dictionary containing statistics information from 'info.yml'.

        Returns:
            dict[str, RawResultSTInfoTypedDict]: The validated statistics information dictionary.
        """

        new_stinfo: dict[str, RawResultSTInfoTypedDict] = {}

        for stname, info in stinfo.items():
            new_info = new_stinfo[stname] = {}

            if "paths" not in info:
                raise ErrorBadFormat(f"Bad '{self.info_path}' format - the "
                                     f"'statistics.{stname}.paths' key is missing")

            new_info["paths"] = {}

            if "stats" not in info["paths"]:
                raise ErrorBadFormat(f"Bad '{self.info_path}' format - the "
                                     f"'statistics.{stname}.paths.stats' key is missing")

            if not info["paths"]["stats"]:
                raise ErrorBadFormat(f"Bad statistics path in '{self.info_path}' - "
                                     f"'statistics.{stname}.paths.stats' is empty")

            new_info["paths"]["stats"] = Path(info["paths"]["stats"])

            if "labels" in info["paths"]:
                if not info["paths"]["labels"]:
                    raise ErrorBadFormat(f"Bad labels path in '{self.info_path}' - "
                                         f"'statistics.{stname}.paths.labels' is empty")

                new_info["paths"]["labels"] = Path(info["paths"]["labels"])

        return new_stinfo

    def _validate_wlinfo(self, wlinfo: RawResultWLInfoTypedDict) -> RawResultWLInfoTypedDict:
        """
        Validate the workload information dictionary from the 'info.yml' file.

        Args:
            wlinfo: A dictionary containing workload information from 'info.yml'.

        Returns:
            RawResultWLInfoTypedDict: The validated workload information dictionary.
        """

        new_wlinfo: RawResultWLInfoTypedDict = {}

        if "wlname" not in wlinfo:
            raise ErrorBadFormat(f"Bad '{self.info_path}' format - the 'workload.wlname' key is "
                                 f"missing")

        self.wlname = wlinfo["wlname"]
        if not self.wlname:
            raise ErrorBadFormat(f"Bad workload info in '{self.info_path}':\n"
                                 f"  'workload.wlname' is empty")

        if self.wlname not in KNOWN_WORKLOADS:
            _LOG.debug("Unknown workload '%s' in '%s'", self.wlname, self.info_path)

        new_wlinfo["wlname"] = self.wlname

        if "wldata_path" in wlinfo:
            if not wlinfo["wldata_path"]:
                raise ErrorBadFormat(f"Bad workload data path in '{self.info_path}' - "
                                    f"'workload.wldata_path' is empty")
            self.wldata_path = Path(wlinfo["wldata_path"])

            if not self.wldata_path.is_absolute():
                # Assume that the path is relative to the raw results directory path.
                self.wldata_path = self.dirpath / self.wldata_path

            if not self.wldata_path.is_dir():
                raise ErrorBadFormat(f"Bad workload data path in '{self.info_path}':\n"
                                    f"  '{self.wldata_path}' does not exist or it is not a "
                                    f"directory")

            new_wlinfo["wldata_path"] =  self.wldata_path

        if "MDD" in wlinfo:
            MDCBase.validate_mdd(wlinfo["MDD"], mdd_src=str(self.info_path))
            new_wlinfo["MDD"] = wlinfo["MDD"]

        return new_wlinfo

    def _load_info_yml(self):
        """Load and validate the contents of the 'info.yml' file."""

        info = YAML.load(self.info_path)

        for key in ("toolname", "toolver", "reportid"):
            if key not in info:
                raise ErrorBadFormat(f"Bad '{self.info_path}' format - the '{key}' key is missing")
            if not info[key]:
                raise ErrorBadFormat(f"Bad '{self.info_path}' format - the '{key}' key is empty")

            self.info[key] = info[key]

        if "stdout" in info:
            info["stdout"] = Path(info["stdout"])
        if "stderr" in info:
            info["stderr"] = Path(info["stderr"])

        if "stinfo" in info:
            self.info["stinfo"] = self._validate_stinfo(info["stinfo"])
        else:
            self.info["stinfo"] = {}

        if "wlinfo" in info:
            self.info["wlinfo"] = self._validate_wlinfo(info["wlinfo"])
        else:
            self.info["wlinfo"] = {}
