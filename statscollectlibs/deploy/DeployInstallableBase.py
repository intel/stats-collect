# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide base class for deploying installables. Refer to the 'DeployBase' module docstring for
terminology reference.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from pepclibs.helperlibs import Logging, ClassHelpers, ToolChecker
from pepclibs.helperlibs.ProcessManager import ProcessManagerType

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class DeployInstallableBase(ClassHelpers.SimpleCloseContext):
    """
    Base class for deploying installables.
    """

    def __init__(self,
                 prjname: str,
                 toolname: str,
                 spman: ProcessManagerType,
                 bpman: ProcessManagerType,
                 stmpdir: Path,
                 btmpdir: Path,
                 cpman: ProcessManagerType | None = None,
                 ctmpdir: Path | None = None,
                 btchk: ToolChecker.ToolChecker | None = None,
                 debug: bool = False):
        """
        Initialize a class instance.

        Args:
            prjname: Name of the project the installables and 'toolname' belong to.
            toolname: Name of the tool the installables belong to.
            spman: A process manager object associated with the SUT (System Under Test).
            bpman: A process manager object associated with the build host (the host where the
                   installable should be built).
            stmpdir: A temporary directory on the SUT.
            btmpdir: Path to a temporary directory on the build host.
            cpman: A process manager object associated with the controller (local host). Defaults to
                   'spman'.
            ctmpdir: Path to a temporary directory on the controller. Defaults to 'stmpdir'.
            btchk: An instance of 'ToolChecker' that can be used for checking the availability of
                   various tools on the build host. Will be created if not provided.
            debug: A boolean variable for enabling additional debugging messages.
        """

        if not cpman:
            cpman = spman
        if not ctmpdir:
            ctmpdir = stmpdir

        self._prjname = prjname
        self._toolname = toolname
        self._spman = spman
        self._bpman = bpman
        self._stmpdir = stmpdir
        self._btmpdir = btmpdir
        self._cpman = cpman
        self._ctmpdir = ctmpdir
        self._btchk = btchk
        self._debug = debug

        self._close_btchk = btchk is None

    def close(self):
        """Uninitialize the object."""

        close_attrs=("_btchk", )
        unref_attrs=("_spman", "_bpman", "_cpman")
        ClassHelpers.close(self, close_attrs=close_attrs, unref_attrs=unref_attrs)

    def _log_cmd_output(self, stdout: str, stderr: str):
        """
        Print the output of a command if debugging is enabled.

        Args:
            stdout: Standard output from the command.
            stderr: Standard error output from the command.
        """

        if self._debug:
            if stdout:
                _LOG.log(Logging.ERRINFO, stdout)
            if stderr:
                _LOG.log(Logging.ERRINFO, stderr)

    def _get_btchk(self):
        """Return a 'ToolChecker' instance."""

        if self._btchk:
            return self._btchk

        self._btchk = ToolChecker.ToolChecker(self._bpman)
        return self._btchk
