# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for creating raw stats-collect test results."""

# TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

import contextlib
import os
import shutil
import time
from typing import Any
from pepclibs.helperlibs import Logging, Trivial, YAML, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from statscollectlibs.rawresultlibs import _RawResultBase
from statscollecttools import ToolInfo

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class WORawResult(_RawResultBase.RawResultBase, ClassHelpers.SimpleCloseContext):
    """This class represents a write-only raw test result."""

    def add_info(self, key: str, value: Any, override: bool = False):
        """
        Add a key-value pair to the 'info' dictionary, so that it gets saved in the 'info.yml' file.

        Args:
            key: The key to add to the dictionary.
            value: The value associated with the key.
            override: If True, override the existing value if the key already exists.
        """

        if not override and key in self.info:
            raise Error(f"BUG: Key '{key}' already exists in the 'info' dictionary")
        self.info[key] = value

    def write_info(self):
        """Write the 'self.info' dictionary to the 'info.yml' file."""

        YAML.dump(self.info, self.info_path)
        self.remove_outdir_on_close = False

    def _init_outdir(self):
        """Initialize the output directory for writing or appending test results."""

        if self.dirpath.exists():
            # Only accept "clean" output directory (either empty or including empty
            # sub-directories).
            paths = (self.info_path, self.logs_path, self.stats_path)
            for path in paths:
                # If path exists fail, except for the case when it is an empty directory.
                if path.exists():
                    if not path.is_dir() or any(path.iterdir()):
                        raise ErrorExists(f"cannot use path '{self.dirpath}' as the output "
                                          f"directory, it already contains '{path.name}'")
        else:
            try:
                self.dirpath.mkdir(parents=True, exist_ok=True)
                self._created_paths.append(self.dirpath)
                _LOG.info("Created statistics result directory '%s'", self.dirpath)
            except OSError as err:
                msg = Error(str(err)).indent(2)
                raise Error(f"failed to create directory '{self.dirpath}':\n{msg}") from None

        # Create empty log and statistics directories in advance.
        paths = (self.logs_path, self.stats_path)
        for path in paths:
            try:
                path.mkdir()
                self._created_paths.append(path)
            except OSError as err:
                msg = Error(str(err)).indent(2)
                raise Error(f"failed to create directory '{path}':\n{msg}") from None

        # Create an empty info file in advance.
        try:
            self.info_path.open("tw+", encoding="utf-8").close()
            self._created_paths.append(self.info_path)
        except OSError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"failed to create file '{self.info_path}':\n{msg}") from None

    def __init__(self, reportid, outdir, cpus=None):
        """
        The class constructor. The arguments are as follows.
          * reportid - reportid of the raw test result.
          * outdir - the output directory to store the raw results at.
          * toolver - version of the tool creating the report.
          * cpus - lsit of CPU number associated with this test resuls.
        """

        super().__init__(outdir)

        self.reportid = reportid
        self.cpus = cpus

        self.remove_outdir_on_close = True

        self._created_paths = []

        self._init_outdir()

        self.info["format_version"] = _RawResultBase.FORMAT_VERSION
        self.info["reportid"] = reportid
        self.info["toolname"] = ToolInfo.TOOLNAME
        self.info["toolver"] = ToolInfo.VERSION
        if cpus is not None:
            self.info["cpus"] = Trivial.rangify(self.cpus)
        self.info["date"] = time.strftime("%d %b %Y")
        self.info["stinfo"] = {}

    def close(self):
        """Stop the experiment."""

        # Only remove result directory if no data were collected.
        if not self.remove_outdir_on_close:
            return

        paths = getattr(self, "_created_paths", [])
        if paths:
            _LOG.debug("no statistics were collected, so the following paths which were created "
                       "will be deleted:\n  - %s",
                       "\n  - ".join(str(p) for p in self._created_paths))

        for path in paths:
            if not path.exists():
                continue
            with contextlib.suppress(Exception):
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.is_file():
                    os.remove(path)
