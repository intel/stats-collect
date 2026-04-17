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

def _filter_pids(pids: Iterable[str],
                 pman: ProcessManagerType,
                 include_children: bool) -> list[str]:
    """
    Filter PIDs to only those that are alive and not zombies.

    Args:
        pids: String PID numbers to filter.
        pman: The process manager to use for running 'pgrep' and 'ps'.
        include_children: If 'True', also include child processes of each PID.

    Returns:
        The filtered list of string PID numbers that are alive and not zombies.
    """

    strpids: list[str] = list(pids)

    if include_children:
        # Find all children of each process.
        for pid in strpids:
            for child in _get_children(int(pid), pman):
                strpids.append(str(child))

    # Drop zombie processes.
    strpids = Trivial.list_dedup(strpids)
    result = []
    for pid in strpids:
        state, _ = _get_ps_state(int(pid), pman)
        if not state or state == "Z":
            continue
        result.append(pid)

    return result

def kill_pids(pids: Iterable[int],
              sig: signal.Signals = signal.SIGTERM,
              kill_children: bool = False,
              must_die: bool = False,
              pman: ProcessManagerType | None = None):
    """
    Send signal 'sig' to processes in 'pids'.

    Args:
        pids: Integer PID numbers to signal.
        sig: The signal to send to the processes, default is 'signal.SIGTERM'.
        kill_children: Whether to also try killing child processes. Should only be used with
                       'SIGTERM' and 'SIGKILL'.
        must_die: Whether to verify that the processes actually died, and raise an exception if
                  they did not. Should only be used with 'SIGTERM' and 'SIGKILL'.
        pman: The process manager object that defines the system to signal the processes on
              (local host by default).
    """

    def _wait_for_pids_to_die(pids: list[str], pman: ProcessManagerType, timeout: int = 4) -> bool:
        """
        Wait for PIDs in 'pids' list to die. Return 'True' if all processes have died, and 'False'
        otherwise.
        """

        start_time = time.time()
        while time.time() - start_time <= timeout:
            # Reap any zombie children to prevent them from accumulating.
            if not pman.is_remote:
                with contextlib.suppress(OSError):
                    os.waitpid(0, os.WNOHANG)

            # Refresh the PIDs list to exclude already exited processes and zombies.
            pids = _filter_pids(pids, pman, include_children=kill_children)
            if not pids:
                return True

            # Check if processes have exited (special signal "0").
            pids_spc = " ".join(pids)
            _, _, exitcode = pman.run(f"kill -0 -- {pids_spc}")
            if exitcode == 1:
                # All processes have exited.
                return True

            time.sleep(0.2)

        return False

    strpids: list[str] = [str(pid) for pid in pids]
    killing: bool = sig in (signal.SIGTERM, signal.SIGKILL)

    if (kill_children or must_die) and not killing:
        raise Error(f"BUG: 'children' and 'must_die' arguments cannot be used with '{sig.name}' "
                    f"signal")

    with ProcessManager.pman_or_local(pman) as wpman:
        strpids = _filter_pids(strpids, wpman, include_children=kill_children)
        if not strpids:
            return

        pids_spc = " ".join(strpids)
        pids_comma = ", ".join(strpids)
        _LOG.debug("Sending '%s' signal to the following process%s: %s",
                   sig.name, wpman.hostmsg, pids_comma)

        try:
            wpman.run_verify(f"kill -{sig.value} -- {pids_spc}")
        except Error as err:
            if not killing:
                raise Error(f"Failed to send signal '{sig.name}' to the following PIDs{wpman.hostmsg}:\n"
                            f"  {pids_comma}:\n{err.indent(2)}") from err
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

        # Give the processes up to 4 seconds to die.
        if _wait_for_pids_to_die(strpids, wpman):
            return

        if sig is signal.SIGTERM:
            # Something refused to die, try SIGKILL.
            strpids = _filter_pids(strpids, wpman, include_children=kill_children)
            if not strpids:
                return

            try:
                pids_spc = " ".join(strpids)
                wpman.run_verify(f"kill -9 -- {pids_spc}")
            except Error as err:
                # It is fine if one of the processes exited meanwhile.
                if "No such process" not in str(err):
                    raise

            # Give the processes another 4 seconds to die.
            if _wait_for_pids_to_die(strpids, wpman):
                return

        if not must_die:
            return

        # Something refused to die, find out what.
        strpids = _filter_pids(strpids, wpman, include_children=kill_children)
        if not strpids:
            return

        pids_spc = " ".join(strpids)
        msg, _, = wpman.run_verify(f"ps -f {pids_spc} --no-headers")
        if not msg:
            msg = "PIDs " + ", ".join(strpids)

        msg = Error(msg).indent(2)
        raise Error(f"One of the following processes{wpman.hostmsg} did not die after 'SIGKILL':\n"
                    f"{msg}")

def find_processes(regex, pman=None):
    """
    Find all processes matching the 'regex' regular expression.

    Args:
        regex: The regular expression matched against the process executable name and command-line
               arguments.
        pman: The process manager object that defines the system to search for processes on
              (local host by default).

    Returns:
        A list of tuples containing the PID and the command line.
    """

    cmd = "ps axo pid,args"

    with ProcessManager.pman_or_local(pman) as wpman:
        stdout, stderr = wpman.run_verify(cmd, join=False)

        if len(stdout) < 2:
            raise Error(f"No processes found at all{wpman.hostmsg}\nExecuted this command:\n{cmd}\n"
                        f"stdout:\n{stdout}\nstderr:{stderr}\n")

        procs = []
        for line in stdout[1:]:
            pid_str, comm = line.strip().split(" ", 1)
            pid = int(pid_str)
            if wpman.hostname == "localhost" and pid == Trivial.get_pid():
                continue
            if re.search(regex, comm):
                procs.append((pid, comm))

    return procs

def kill_processes(regex,
                   sig: signal.Signals = signal.SIGTERM,
                   kill_children: bool = False,
                   log: bool = False,
                   name=None,
                   pman=None):
    """
    Kill or signal all processes matching the 'regex' regular expression.

    Args:
        regex: The regular expression matched against the process executable name and command-line
               arguments.
        sig: The signal to send to matching processes, default is 'signal.SIGTERM'.
        kill_children: Whether to also try killing child processes. Should only be used with
                       'SIGTERM' and 'SIGKILL'.
        log: If 'True', print a message including the PIDs of the processes being signalled.
        name: A human-readable name of the processes being signalled, included in the printed
              message when 'log' is 'True'.
        pman: The process manager object that defines the system to search for processes on
              (local host by default).

    Returns:
        The list of signalled processes.
    """

    with ProcessManager.pman_or_local(pman) as wpman:
        procs = find_processes(regex, pman=wpman)
        if not procs:
            return []

        if not name:
            name = "the following process(es)"

        pids = [pid for pid, _ in procs]
        if log:
            pids_str = ", ".join([str(pid) for pid in pids])
            _LOG.info("Sending '%s' signal to %s%s, PID(s): %s",
                      sig.name, name, wpman.hostmsg, pids_str)

        kill_pids(pids, sig=sig, kill_children=kill_children, pman=wpman)

        return procs
