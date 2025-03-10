# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for creating raw stats-collect test results."""

import contextlib
import os
import shutil
import time
from pepclibs.helperlibs import Logging, Human, YAML, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from statscollectlibs.rawresultlibs import _RawResultBase
from statscollecttools import ToolInfo

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class WORawResult(_RawResultBase.RawResultBase, ClassHelpers.SimpleCloseContext):
    """This class represents a write-only raw test result."""

    def write_info(self):
        """Write the 'self.info' dictionary to the 'info.yml' file."""

        YAML.dump(self.info, self.info_path)
        self._data_collected = True

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
                raise Error(f"failed to create directory '{self.dirpath}':\n{err}") from None

        # Create an empty info file in advance.
        try:
            self.info_path.open("tw+", encoding="utf-8").close()
        except OSError as err:
            raise Error(f"failed to create file '{self.info_path}':\n{err}") from None

    def __init__(self, reportid, outdir, cmd=None, cpus=None):
        """
        The class constructor. The arguments are as follows.
          * reportid - reportid of the raw test result.
          * outdir - the output directory to store the raw results at.
          * toolver - version of the tool creating the report.
          * cmd - the command executed during statistics collection.
          * cpus - lsit of CPU number associated with this test resuls.
        """

        super().__init__(outdir)

        self.reportid = reportid
        self.cpus = cpus

        self._created_paths = []
        self._data_collected = False

        self._init_outdir()

        self.info["format_version"] = _RawResultBase.FORMAT_VERSION
        self.info["reportid"] = reportid
        self.info["toolname"] = ToolInfo.TOOLNAME
        self.info["toolver"] = ToolInfo.VERSION
        if cpus is not None:
            self.info["cpus"] = Human.rangify(self.cpus)
        if cmd is not None:
            self.info["cmd"] = cmd
        self.info["date"] = time.strftime("%d %b %Y")
        self.info["stinfo"] = {}

    def close(self):
        """Stop the experiment."""

        # Only remove result directory if no data were collected.
        if self._data_collected:
            return

        paths = getattr(self, "_created_paths", [])
        if paths:
            _LOG.debug("no statistics were collected, so the following paths which were created "
                       "will be deleted:\n  - %s",
                       "\n  -".join(str(p) for p in self._created_paths))

        for path in paths:
            if not path.exists():
                continue
            with contextlib.suppress(Exception):
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.is_file():
                    os.remove(path)
