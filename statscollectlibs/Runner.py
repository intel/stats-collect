# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability to execute a given command on a SUT and control the simultaneous
collection of statistics.
"""

import logging
import time
from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs import ClassHelpers, Human
from statscollectlibs.helperlibs import ProcHelpers
from statscollecttools import ToolInfo

_LOG = logging.getLogger()

class Runner(ClassHelpers.SimpleCloseContext):
    """
    This class provides the capability to execute a given command on a SUT and control the
    simultaneous collection of statistics.
    """

    def _run_command(self, tlimit):
        """Run the command."""

        _LOG.info("Running the following command%s: %s", self._pman.hostmsg, self._cmd)

        if not tlimit:
            run_forever = True
            tlimit = 4 * 60 * 60
        else:
            run_forever = False

        self._proc = self._pman.run_async(self._cmd)
        while True:
            stdout, stderr, exitcode = self._proc.wait(timeout=tlimit)
            if exitcode is not None:
                break

            if run_forever:
                continue

            _LOG.notice("statistics collection stopped because the time limit was reached "
                        "before the command finished executing.")
            ProcHelpers.kill_pids(self._proc.pid, kill_children=True, must_die=True,
                                  pman=self._pman)
            break

        if exitcode:
            raise Error(f"there was an error running command '{self._cmd}':\n{stderr}")

        return stdout, stderr

    def run(self, cmd, tlimit=None):
        """
        Run command 'cmd' and collect statistics about the SUT during command execution. Arguments
        are as follows:
         * cmd - the command to run on the SUT during statistics collection.
         * tlimit - the time limit to execute 'cmd' in seconds.
        """

        self._cmd = cmd

        if self._stcoll:
            self._stcoll.start()

        start_time = time.time()
        stdout, stderr = self._run_command(tlimit)
        duration = time.time() - start_time

        if self._stcoll:
            min_duration = 2 * self._stcoll.get_max_interval()
            if duration < min_duration:
                raise Error(f"command '{self._cmd}' finished before '{ToolInfo.TOOLNAME}' "
                            f"collected the mininum amount of statistics. Command should run for "
                            f"at least {Human.duration(min_duration)}")

            self._stcoll.stop()
            self._stcoll.finalize()

        for ftype, txt in [("stdout", stdout,), ("stderr", stderr,)]:
            if not txt:
                continue
            fpath = self.res.logs_path / f"cmd-{ftype}.log.txt"
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(txt)
            self.res.info[ftype] = fpath.relative_to(self.res.dirpath)

        self.res.info["duration"] = Human.duration(duration)
        self.res.write_info()

    def __init__(self, res, pman, stcoll=None):
        """
        Class constructor. Arguments are as follows:
         * res - 'WORawResult' instance to store the results in.
         * pman - the process manager object that defines the host to run the measurements on.
         * stcoll - the 'StatsCollect' object to use for collecting statistics. No statistics
                    are collected by default.
        """

        self.res = res
        self._pman = pman
        self._stcoll = stcoll

        # Class attributes representing the command and process run by 'run()'.
        self._cmd = None
        self._proc = None

    def close(self):
        """Close the runner."""

        if self._proc.poll() is None:
            _LOG.info("'%s' is still running %s: attempting to kill it", self._cmd,
                      self._pman.hostmsg)
            ProcHelpers.kill_pids(self._proc.pid, kill_children=True, must_die=True,
                                  pman=self._pman)

        ClassHelpers.close(self, close_attrs=("_proc",), unref_attrs=("_pman",))
