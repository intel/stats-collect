# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
Provide capability to execute a given command on a System Under Test (SUT) and control the
simultaneous collection of statistics.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import time
from pepclibs.helperlibs import Logging, ClassHelpers, Human
from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs.ProcessManager import ProcessManagerType, ProcessType
from statscollectlibs.helperlibs import ProcHelpers
from statscollectlibs.rawresultlibs.WORawResult import WORawResult
from statscollectlibs.collector.StatsCollect import StatsCollect
from statscollecttools import ToolInfo

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class Runner(ClassHelpers.SimpleCloseContext):
    """
    Provide capability to execute a given command on a System Under Test (SUT) and control the
    simultaneous collection of statistics.
    """

    def __init__(self, res: WORawResult, cmd_pman: ProcessManagerType, stcoll: StatsCollect | None):
        """
        The class constructor.

        Args:
            res: Instance to store the results in.
            cmd_pman: The process manager object that defines the host where the command run by the
                      'run()' method will be executed.
            stcoll: The 'StatsCollect' object to use for collecting statistics. No statistics are
                    collected by default.
        """

        self.res = res
        self._cmd_pman = cmd_pman
        self._stcoll = stcoll

        # Class attributes representing the command and process run by 'run()'.
        self._cmd = ""
        self._proc: ProcessType | None = None

    def close(self):
        """Close the runner."""

        if self._proc and self._proc.poll() is None:
            _LOG.info("The command is still running%s: attempting to kill it",
                      self._cmd_pman.hostmsg)
            ProcHelpers.kill_pids(self._proc.pid, kill_children=True, must_die=True,
                                  pman=self._cmd_pman)

        ClassHelpers.close(self, close_attrs=("_proc",), unref_attrs=("_cmd_pman",))

    def _run_command(self, tlimit: int | None):
        """
        Run the specified command with an optional time limit.

        Args:
            tlimit: The time limit in seconds for the command to run. If None, the command
                    will run indefinitely with a default time limit of 4 hours.

        Returns:
            tuple: A tuple containing the standard output and standard error of the command.
        """

        _LOG.info("Running the following command%s: %s", self._cmd_pman.hostmsg, self._cmd)

        if not tlimit:
            run_forever = True
            tlimit = 4 * 60 * 60
        else:
            run_forever = False

        self._proc = self._cmd_pman.run_async(self._cmd)
        while True:
            stdout, stderr, exitcode = self._proc.wait(timeout=tlimit)
            if exitcode is not None:
                break

            if run_forever:
                continue

            _LOG.notice("Statistics collection stopped because the time limit was reached "
                        "before the command finished executing.")
            ProcHelpers.kill_pids(self._proc.pid, kill_children=True, must_die=True,
                                  pman=self._cmd_pman)
            break

        if exitcode:
            raise Error(f"There was an error running command '{self._cmd}':\n{stderr}")

        return stdout, stderr

    def run(self, cmd: str, tlimit: int | None = None):
        """
        Run command 'cmd' and collect statistics about the SUT during command execution.

        Args:
            cmd: The command to run on the SUT during statistics collection.
            tlimit: The time limit to execute 'cmd' in seconds. Defaults to None.
        """

        self._cmd = cmd
        # Do not remove the output directory in case of an error, in order to preserve log files.
        self.res.remove_outdir_on_close = False

        if self._stcoll:
            self._stcoll.start()

        start_time = time.time()
        stdout, stderr = self._run_command(tlimit)
        duration = time.time() - start_time

        if self._stcoll:
            min_duration = 2 * self._stcoll.get_max_interval()
            if duration < min_duration:
                raise Error(f"Command '{self._cmd}' finished before '{ToolInfo.TOOLNAME}' "
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
            self.res.add_info(ftype, fpath.relative_to(self.res.dirpath))

        self.res.add_info("duration", Human.duration(duration))
        self.res.write_info()
