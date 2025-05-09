# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains misc. helper functions related to processes (tasks).
"""

# Finish annotating this module
from __future__ import annotations # Remove when switching to Python 3.10+.

import os
import re
import time
import contextlib
from pepclibs.helperlibs import Logging, ProcessManager, Trivial
from pepclibs.helperlibs.Exceptions import Error

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

def _is_sigterm(sig: str):
    """Return 'True' if sig' is the 'SIGTERM' signal."""
    return sig == "15" or sig.endswith("TERM")

def _is_sigkill(sig: str):
    """Return 'True' if sig' is the 'SIGKILL' signal."""
    return sig == "15" or sig.endswith("KILL")

def is_root(pman=None):
    """
    If 'pman' is 'None' or a local process manager object, return 'True' if current process' user
    name is 'root' and 'False' if current process' user name is not 'root'.

    If 'pman' is a remote process manager object, returns 'True' if user has 'root' permissions on
    the remote host, otherwise returns 'False'.
    """

    if not pman or not pman.is_remote:
        return Trivial.is_root()

    stdout, _ = pman.run_verify("id -u")
    stdout = stdout.strip()
    if not Trivial.is_int(stdout):
        raise Error("unexpected output from 'id -u' command, expected an integer, got:\n{stdout}")

    return int(stdout) == 0

def bind_pid(pid: int,
             cpus: int | list[int] | str,
             pman: ProcessManager.ProcessManagerType | None = None):
    """
    Bind a process with PID 'pid' to CPUs in 'cpus'

    Args:
        pid: The PID of the process to bind to CPUs.
        cpus: The integer CPU number to bind the process to, or a list list of integer CPU numbers to
              bind the process to. Can also be a string containing a comma-separated list of CPU
              numbers and CPU number ranges. For example, "0,2-4,6".
        pman - the process manager object that defines the system to the 'pid' process runs on
               (local host by default).
    """

    if isinstance(cpus, int):
        cpus_str = cpus = str(cpus)
    if not isinstance(cpus, str):
        cpus_str = ",".join([str(cpu) for cpu in cpus])
    else:
        cpus_str = cpus

    cmd = f"taskset -pc {cpus_str} {pid}"

    with ProcessManager.pman_or_local(pman) as wpman:
        try:
            wpman.run_verify(cmd)
        except Error as err:
            errmsg = err.indent(2)
            raise Error(f"failed to bind PID {pid} to CPUs {cpus_str}:\n{errmsg}") from err

def kill_pids(pids, sig="SIGTERM", kill_children=False, must_die=False, pman=None):
    """
    Send signal 'sig' to processes in 'pids'. The arguments are as follows.
      * pids - an iterable collection of PIDs to signal. May contain integers or strings. May also
              a signel PID number.
      * sig - the signal to send the the processes. The signal can be specified either by name or by
               number, default is 'SIGTERM' (terminate the process).
      * kill_children - whether this function should also try killing the child processes. Should
                        only be used with 'SIGTERM' and 'SIGKILL'.
      * must_die - whether this function should also verify that the processes did actually die, and
                   if they did not, raise an exception. Should only be used with 'SIGTERM' and
                   'SIGKILL'.
      * pman - the process manager object that defines the system to signal for the processes on
               (local host by default).
    """

    def collect_zombies(pman):
        """In case of a local process we need to 'waitpid()' the children."""

        if not pman.is_remote:
            with contextlib.suppress(OSError):
                os.waitpid(0, os.WNOHANG)

    def get_pids(pids, pman):
        """Return the list of integer PID numbers to send the signal to."""

        if kill_children:
            # Find all the children of the process.
            for pid in pids:
                children, _, exitcode = wpman.run(f"pgrep -P {pid}", join=False)
                if exitcode != 0:
                    _LOG.debug("PID %d was not found, skipping")
                    continue
                pids += [child.strip() for child in children]

        # Drop zombie processes.
        orig_pids = Trivial.list_dedup(pids)
        pids = []
        for pid in orig_pids:
            state, _, exitcode = pman.run(f"ps -p {pid} -o stat --no-headers")
            if exitcode != 0:
                continue
            if state.strip() == "Z":
                # Drop the zombie process.
                continue
            pids.append(pid)

        return pids

    def wait_for_pids_to_die(pids, pman, timeout=4):
        """
        Wait for PIDs in 'pids' list to die. Return 'True' if all processes have died, and 'False'
        otherwise.
        """

        start_time = time.time()
        while time.time() - start_time <= timeout:
            collect_zombies(pman)

            # Refresh the PIDs list to exclude already exited processes and zombies.
            pids = get_pids(pids, pman)
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

    if not pids:
        return

    if not Trivial.is_iterable(pids):
        pids = (pids, )

    pids = [str(int(pid)) for pid in pids]

    if sig is None:
        sig = "SIGTERM"
    else:
        sig = str(sig)

    killing = _is_sigterm(sig) or _is_sigkill(sig)
    if (kill_children or must_die) and not killing:
        raise Error(f"'children' and 'must_die' arguments cannot be used with '{sig}' signal")

    with ProcessManager.pman_or_local(pman) as wpman:
        pids = get_pids(pids, wpman)
        if not pids:
            return

        pids_spc = " ".join(pids)
        pids_comma = ", ".join(pids)
        _LOG.debug("sending '%s' signal to the following process%s: %s",
                   sig, wpman.hostmsg, pids_comma)

        try:
            wpman.run_verify(f"kill -{sig} -- {pids_spc}")
        except Error as err:
            if not killing:
                raise Error(f"failed to send signal '{sig}' the following PIDs{wpman.hostmsg}:\n"
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
        if wait_for_pids_to_die(pids, wpman):
            return

        if _is_sigterm(sig):
            # Something refused to die, try SIGKILL.
            pids = get_pids(pids, wpman)
            if not pids:
                return

            try:
                pids_spc = " ".join(pids)
                wpman.run_verify(f"kill -9 -- {pids_spc}")
            except Error as err:
                # It is fine if one of the processes exited meanwhile.
                if "No such process" not in str(err):
                    raise

            # Give the processes another 4 seconds to die.
            if wait_for_pids_to_die(pids, wpman):
                return

        if not must_die:
            return

        # Something refused to die, find out what.
        pids = get_pids(pids, wpman)
        if not pids:
            return

        pids_spc = " ".join(pids)
        msg, _, = wpman.run_verify(f"ps -f {pids_spc} --no-headers")
        if not msg:
            msg = "PIDs " + ", ".join(pids)

        msg = Error(msg).indent(2)
        raise Error(f"one of the following processes{wpman.hostmsg} did not die after 'SIGKILL':\n"
                    f"{msg}")

def find_processes(regex, pman=None):
    """
    Find all processes which match the 'regex' regular expression. The arguments are as follows.
      * regex - the regular expression which is matched process executable name + command-line
                arguments.
      * pman - the process manager object that defines the system to search for the processes on
               (local host by default).

    Returns a list of tuples containing the PID and the command line.
    """

    cmd = "ps axo pid,args"

    with ProcessManager.pman_or_local(pman) as wpman:
        stdout, stderr = wpman.run_verify(cmd, join=False)

        if len(stdout) < 2:
            raise Error(f"no processes found at all{wpman.hostmsg}\nExecuted this command:\n{cmd}\n"
                        f"stdout:\n{stdout}\nstderr:{stderr}\n")

        procs = []
        for line in stdout[1:]:
            pid, comm = line.strip().split(" ", 1)
            pid = int(pid)
            if wpman.hostname == "localhost" and pid == Trivial.get_pid():
                continue
            if re.search(regex, comm):
                procs.append((int(pid), comm))

    return procs

def kill_processes(regex, sig="SIGTERM", kill_children=False, log=False, name=None, pman=None):
    """
    Kill or signal all processes matching the 'regex' regular expression. The arguments are as
    follows.
      * regex - the regular expression which is matched process executable name + command-line
                arguments.
      * sig - the signal to send the the processes matching 'regex'. The signal can be specified
              either by name or by number, default is 'SIGTERM' (terminate the process).
      * kill_children - whether this function should also try killing the child processes. Should
                        only be used with 'SIGTERM' and 'SIGKILL'.
      * log - If 'True', then this function also prints a message which includes the PIDs of the
              processes which are going to be signalled.
      * name - a human-readable name of the processes which are being signalled - this name will be
               part of the printed message (if 'log' is provided).
      * pman - the process manager object that defines the system to search for the processes on
               (local host by default).

    Returns the list of signalled processes.
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
                      sig, name, wpman.hostmsg, pids_str)

        kill_pids(pids, sig=sig, kill_children=kill_children, pman=wpman)

        return procs
