# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains misc. helper functions related to processes (tasks).
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import os
import re
import time
import typing
import signal
import contextlib
from pepclibs.helperlibs import Logging, ProcessManager, Trivial
from pepclibs.helperlibs.Exceptions import Error

if typing.TYPE_CHECKING:
    from typing import Generator, Iterable
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

def bind_pid(pid: int,
             cpus: Iterable[int],
             pman: ProcessManagerType | None = None):
    """
    Bind a process with PID 'pid' to CPUs in 'cpus'.

    Args:
        pid: The PID of the process to bind to CPUs.
        cpus: The CPU numbers to bind the process to.
        pman: The process manager object that defines the system the 'pid' process runs on
              (local host by default).
    """

    cpus_str = ",".join(str(cpu) for cpu in cpus)
    cmd = f"taskset -pc {cpus_str} {pid}"

    with ProcessManager.pman_or_local(pman) as wpman:
        try:
            wpman.run_verify(cmd)
        except Error as err:
            errmsg = err.indent(2)
            raise Error(f"Failed to bind PID {pid} to CPUs {cpus_str}:\n{errmsg}") from err

def _get_children(pid: int,
                  pman: ProcessManagerType) -> Generator[int, None, None]:
    """
    Yield all descendants of PID 'pid' (children, grandchildren, etc.).

    Args:
        pid: The PID of the process to get descendants of.
        pman: The process manager to use for running 'pgrep'.

    Yields:
        Descendant PIDs. Yields nothing if the process does not exist or has no children.
    """

    children, _, exitcode = pman.run_nojoin(f"pgrep -P {pid}")
    if exitcode != 0:
        return

    for child in children:
        child = child.strip()
        if not Trivial.is_int(child):
            raise Error(f"Unexpected non-integer 'pgrep' output: '{child}'")
        child_pid = int(child)
        yield child_pid
        yield from _get_children(child_pid, pman)

def _get_ps_state(pid: int, pman: ProcessManagerType) -> tuple[str, str]:
    """
    Get the process state of PID 'pid'.

    Args:
        pid: The PID of the process to get the state of.
        pman: The process manager to use for running 'ps'.

    Returns:
        A tuple of '(state, modifiers)' where 'state' is the single letter indicating the process
        state (e.g., 'R', 'S', 'Z'), and 'modifiers' is the string of additional modifier
        characters (possibly empty). Returns '("", "")' if the process does not exist.
    """

    stat, _, exitcode = pman.run_join(f"ps -p {pid} -o stat --no-headers")
    if exitcode != 0:
        return "", ""
    stat = stat.strip()
    if not stat or len(stat) > 5 or not stat[0].isalpha():
        raise Error(f"Unexpected 'ps' stat output for PID {pid}: '{stat}'")
    return stat[0], stat[1:]

def _filter_pids(pids: Iterable[int],
                 pman: ProcessManagerType,
                 include_children: bool) -> list[int]:
    """
    Filter PIDs to only those that are alive and not zombies.

    Args:
        pids: Integer PID numbers to filter.
        pman: The process manager to use for running 'pgrep' and 'ps'.
        include_children: If 'True', also include child processes of each PID.

    Returns:
        The filtered list of integer PID numbers that are alive and not zombies.
    """

    pids_list: list[int] = list(pids)

    if include_children:
        # Find all children of each process.
        for pid in pids_list:
            for child in _get_children(pid, pman):
                pids_list.append(child)

    # Drop zombie processes.
    pids_list = Trivial.list_dedup(pids_list)
    result = []
    for pid in pids_list:
        state, _ = _get_ps_state(pid, pman)
        if not state or state == "Z":
            continue
        result.append(pid)

    return result

def _wait_for_pids_to_die(pids: Iterable[int],
                          pman: ProcessManagerType,
                          include_children: bool = False,
                          timeout: int = 5,
                          interval: float = 0.1) -> bool:
    """
    Wait for processes to exit.

    Args:
        pids: Integer PID numbers to wait for.
        pman: The process manager to use for running 'ps' and sending signal 0.
        include_children: If 'True', also wait for child processes of each PID to exit.
        timeout: Maximum number of seconds to wait before giving up.
        interval: Number of seconds to sleep between polls.

    Returns:
        'True' if all processes exited within 'timeout' seconds, 'False' otherwise.
    """

    start_time = time.time()
    while time.time() - start_time <= timeout:
        # Reap any zombie children to prevent them from accumulating.
        if not pman.is_remote:
            with contextlib.suppress(OSError):
                os.waitpid(0, os.WNOHANG)

        # Refresh the PIDs list to exclude already exited processes and zombies.
        pids = _filter_pids(pids, pman, include_children=include_children)
        if not pids:
            return True

        # Check if processes have exited (special signal "0").
        pids_str = " ".join(str(pid) for pid in pids)
        _, _, exitcode = pman.run(f"kill -0 -- {pids_str}")
        if exitcode == 1:
            # All processes have exited.
            return True

        time.sleep(interval)

    return False

def signal_pids(pids: Iterable[int],
                pman: ProcessManagerType | None = None,
                sig: signal.Signals = signal.SIGTERM,
                include_children: bool = False,
                must_die: bool = False,
                interval: float = 0.1,
                su: bool = False):
    """
    Send signal 'sig' to processes in 'pids'.

    Args:
        pids: Integer PID numbers to signal.
        pman: The process manager object that defines the system to signal the processes on
              (local host by default).
        sig: The signal to send to the processes, default is 'signal.SIGTERM'.
        include_children: Also signal child processes of each PID. Only valid with 'SIGTERM' and
                          'SIGKILL'.
        must_die: Wait for processes to exit and raise 'Error' if any survive. When 'True' and
                  'sig' is 'SIGTERM', also escalates to 'SIGKILL' if processes do not exit within
                  the timeout. Only valid with 'SIGTERM' and 'SIGKILL'.
        interval: Number of seconds to sleep between polls when waiting for processes to exit.
        su: If 'True', run the kill command with superuser privileges.

    Notes:
        - When 'must_die' is 'False', the signal is sent and the function returns immediately
          without checking whether the processes actually exited.
        - When 'must_die' is 'True' and 'sig' is 'SIGTERM', waits up to 5 seconds for processes
          to exit, then escalates to 'SIGKILL'. Raises 'Error' if any process survives.
        - When 'must_die' is 'True' and 'sig' is 'SIGKILL', waits up to 5 seconds and raises
          'Error' if any process survives.
    """

    pids_list: list[int] = list(pids)
    killing: bool = sig in (signal.SIGTERM, signal.SIGKILL)

    if (include_children or must_die) and not killing:
        raise Error(f"BUG: The 'include_children' and 'must_die' arguments cannot be used with "
                    f"'{sig.name}' signal")

    with ProcessManager.pman_or_local(pman) as wpman:
        pids_list = _filter_pids(pids_list, wpman, include_children=include_children)
        if not pids_list:
            return

        pids_space = " ".join(str(p) for p in pids_list)
        pids_comma = ", ".join(str(p) for p in pids_list)
        _LOG.debug("Sending '%s' signal to the following process%s: %s",
                   sig.name, wpman.hostmsg, pids_comma)

        try:
            wpman.run_verify(f"kill -{sig.value} -- {pids_space}", su=su)
        except Error as err:
            if not killing:
                raise Error(f"Failed to send signal '{sig.name}' to the following PIDs"
                            f"{wpman.hostmsg}:\n{pids_comma}:\n{err.indent(2)}") from err

            # We are trying to terminate processes, but an error happened. Do not give up yet. Here
            # is an example to demonstrate why.
            #
            # One of the processes in the list is owned by a different user (e.g., root). Let's call
            # it process A. We have no permissions to kill process A, but we can kill other
            # processes in the 'pids' list. But often killing other processes in the 'pids' list
            # will make process A exit. This is why we do not error out just yet. So the strategy is
            # to do the second signal sending round and often times it happens without errors, and
            # all the processes that we want to kill just go away.

        if not killing:
            return

        if not must_die:
            return

        # Give the processes up to 5 seconds to die.
        if _wait_for_pids_to_die(pids_list, wpman, include_children=include_children, timeout=5,
                                 interval=interval):
            return

        if sig is signal.SIGTERM:
            # Something refused to die, try SIGKILL.
            pids_list = _filter_pids(pids_list, wpman, include_children=include_children)
            if not pids_list:
                return

            try:
                pids_space = " ".join(str(p) for p in pids_list)
                wpman.run_verify(f"kill -9 -- {pids_space}", su=su)
            except Error as err:
                # It is fine if one of the processes exited meanwhile.
                if "No such process" not in str(err):
                    raise

            # Give the processes another 5 seconds to die.
            if _wait_for_pids_to_die(pids_list, wpman, include_children=include_children, timeout=5,
                                     interval=interval):
                return

        # Something refused to die, find out what.
        pids_list = _filter_pids(pids_list, wpman, include_children=include_children)
        if not pids_list:
            return

        pids_comma = ",".join(str(p) for p in pids_list)
        msg, _, = wpman.run_verify_join(f"ps -ww -fp {pids_comma} --no-headers")
        if not msg:
            msg = "PIDs " + ", ".join(str(p) for p in pids_list)

        msg = Error(msg).indent(2)
        raise Error(f"One of the following processes{wpman.hostmsg} did not die after 'SIGKILL':\n"
                    f"{msg}")

def grep_processes(regex: str | re.Pattern[str],
                   pman: ProcessManagerType | None = None) -> list[tuple[int, str]]:
    """
    Find all processes matching 'regex'.

    Args:
        regex: A regular expression (string or compiled pattern) matched against the process
               executable name and command-line arguments.
        pman: The process manager object that defines the system to search for processes on
              (local host by default).

    Returns:
        A list of '(pid, command_line)' tuples for each matching process.
    """

    # Use '-ww' to disable 'ps' column-width truncation so long command lines are not cut off.
    cmd = "ps -ww axo pid,args"

    with ProcessManager.pman_or_local(pman) as wpman:
        stdout, stderr = wpman.run_verify_nojoin(cmd)

        if len(stdout) < 2:
            stdout_str = "".join(stdout)
            stderr_str = "".join(stderr)
            raise Error(f"No processes found at all{wpman.hostmsg}\nExecuted this command:\n{cmd}\n"
                        f"stdout:\n{stdout_str}\nstderr:\n{stderr_str}")

        procs = []
        for line in stdout[1:]:
            pid_str, comm = line.strip().split(" ", 1)
            pid = Trivial.str_to_int(pid_str)
            if wpman.hostname == "localhost" and pid == Trivial.get_pid():
                continue
            if re.search(regex, comm):
                procs.append((pid, comm))

    return procs

def signal_processes(regex: str | re.Pattern[str],
                     sig: signal.Signals = signal.SIGTERM,
                     include_children: bool = False,
                     must_die: bool = False,
                     interval: float = 0.1,
                     log: bool = False,
                     name: str = "",
                     pman: ProcessManagerType | None = None,
                     su: bool = False) -> list[tuple[int, str]]:
    """
    Send signal 'sig' to all processes matching 'regex'.

    Args:
        regex: A regular expression (string or compiled pattern) matched against the process
               executable name and command-line arguments.
        sig: The signal to send to matching processes, default is 'signal.SIGTERM'.
        include_children: Also signal child processes of each matching PID. Only valid with
                          'SIGTERM' and 'SIGKILL'.
        must_die: Wait for processes to exit and raise 'Error' if any survive. When 'True' and
                  'sig' is 'SIGTERM', also escalates to 'SIGKILL' if processes do not exit within
                  the timeout. Only valid with 'SIGTERM' and 'SIGKILL'.
        interval: Number of seconds to sleep between polls when waiting for processes to exit.
        log: If 'True', log a message including the PIDs of the processes being signalled.
        name: A human-readable description of the processes, used in the log message when 'log'
              is 'True'. Defaults to "the following process(es)" when empty.
        pman: The process manager object that defines the system to search for processes on
              (local host by default).
        su: If 'True', run the kill command with superuser privileges.

    Returns:
        A list of '(pid, command_line)' tuples for each signalled process, or an empty list if
        no matching processes were found.
    """

    with ProcessManager.pman_or_local(pman) as wpman:
        procs = grep_processes(regex, pman=wpman)
        if not procs:
            return []

        if not name:
            name = "the following process(es)"

        pids = [pid for pid, _ in procs]
        if log:
            pids_str = ", ".join(str(pid) for pid in pids)
            _LOG.info("Sending '%s' signal to %s%s, PID(s): %s",
                      sig.name, name, wpman.hostmsg, pids_str)

        signal_pids(pids, pman=wpman, sig=sig, include_children=include_children,
                    must_die=must_die, interval=interval, su=su)
        return procs
