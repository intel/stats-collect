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

import sys
import time
from pepclibs.helperlibs import Logging, ClassHelpers, Human
from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs.ProcessManager import ProcessManagerType, ProcessType
from statscollectlibs.helperlibs import ProcHelpers
from statscollectlibs.rawresultlibs.WORawResult import WORawResult
from statscollectlibs.collector.StatsCollect import StatsCollect

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

        # The run command.
        self._cmd = ""
        # The process object of the running command.
        self._cmd_proc: ProcessType | None = None

        # For how long the command has been running (seconds).
        self._duration = 0.0

    def close(self):
        """Close the runner."""

        if self._cmd_proc and self._cmd_proc.poll() is None:
            _LOG.info("The command is still running%s: attempting to kill it",
                      self._cmd_pman.hostmsg)
            ProcHelpers.kill_pids(self._cmd_proc.pid, kill_children=True, must_die=True,
                                  pman=self._cmd_pman)

        ClassHelpers.close(self, close_attrs=("_cmd_proc",), unref_attrs=("_cmd_pman",))

    def _run_command(self, tlimit: float | None):
        """
        Run the specified command with an optional time limit.

        Args:
            tlimit: The time limit in seconds for the command to run. If None, the command
                    will run indefinitely with a default time limit of 4 hours.

        Returns:
            tuple: A tuple containing the standard output, standard error, and exit code of the
            command. If the command is still running, but the time limit has been reached, the
            exit code will be None.
        """

        _LOG.info("Running the following command%s:\n  %s", self._cmd_pman.hostmsg, self._cmd)

        if not tlimit:
            no_tlimit = True
            tlimit = 4 * 60 * 60
        else:
            no_tlimit = False

        # For how long to wait for the command to finish per iteration.
        cmd_proc_wait_time = float(tlimit)

        start_time = time.time()
        self._cmd_proc = self._cmd_pman.run_async(self._cmd)
        while True:
            stdout, stderr, exitcode = self._cmd_proc.wait(timeout=cmd_proc_wait_time,
                                                       output_fobjs=(sys.stdout, sys.stderr))
            self._duration = time.time() - start_time

            if exitcode is None:
                # The command is still running.
                if no_tlimit:
                    # There is no time limit, wait for the command to finish.
                    continue
                if self._duration < tlimit:
                    # There is a time limit, but it has not been reached yet.
                    if cmd_proc_wait_time > tlimit - self._duration:
                        cmd_proc_wait_time = tlimit - self._duration
                    continue
            break

        return stdout, stderr, exitcode

    def run(self, cmd: str, tlimit: float | None = None):
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

        stdout, stderr, exitcode = self._run_command(tlimit)

        # The measurements are finished, stop the statistics collection.
        if self._stcoll:
            self._stcoll.stop()

        assert self._cmd_proc is not None

        if exitcode is None:
            _LOG.notice("Statistics collection stopped because the time limit was reached "
                        "before the command finished executing.")
            ProcHelpers.kill_pids(self._cmd_proc.pid, kill_children=True, must_die=True,
                                    pman=self._cmd_pman)
        elif exitcode:
            # The command existed with a non-zero exit code. This may mean it failed, but may also
            # mean something else. So do not error out.
            errmsg = self._cmd_pman.get_cmd_failure_msg(self._cmd, stdout, stderr, exitcode,
                                                        failed=False)
            _LOG.warning(errmsg)

        if self._stcoll:
            min_duration = 2 * self._stcoll.get_max_interval()
            if self._duration < min_duration:
                ran = Human.duration(self._duration)
                expected = Human.duration(min_duration)
                raise Error(f"The command has finished before the minimum amount of statistics "
                            f"were collected.\nThe command ran for {ran}, but should run for at "
                            f"least {expected}.")
            self._stcoll.finalize()

        for ftype, txt in [("stdout", stdout,), ("stderr", stderr,)]:
            if not txt:
                continue
            fpath = self.res.logs_path / f"cmd-{ftype}.log.txt"
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(txt)
            self.res.add_info(ftype, fpath.relative_to(self.res.dirpath))

        self.res.add_info("duration", Human.duration(self._duration))
        self.res.write_info()
