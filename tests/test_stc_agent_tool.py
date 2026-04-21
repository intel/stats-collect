# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Tests for the 'stc-agent' tool."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import time
import signal
import socket
import typing
import contextlib

import pytest
from pepclibs.helperlibs import Trivial, Exceptions
from pepclibs.helperlibs.Exceptions import Error, ErrorPermissionDenied
from statscollectlibs.collector import _Collectors
from statscollectlibs.deploy import DeployHelpersBase
from statscollectlibs.helperlibs import ProcHelpers
from statscollectlibs.parsers import InterruptsParser, TurbostatParser
from tests import _Common

if typing.TYPE_CHECKING:
    from pathlib import Path
    from typing import cast, Generator
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType, ProcessType
    from tests._Common import CommonTestParamsTypedDict

    class _TestParamsTypedDict(CommonTestParamsTypedDict, total=False):
        """
        Test parameters dictionary for 'stc-agent' tests.

        Attributes:
            stc_agent_path: Path to the 'stc-agent' binary on the target host.
            interrupts_helper_path: Path to 'stc-agent-proc-interrupts-helper' on the target host.
        """

        stc_agent_path: Path
        interrupts_helper_path: Path | None

# Paths to tools in the local project source tree.
_LOCAL_STC_AGENT = _Common.get_prj_src_path() / "stc-agent"
_LOCAL_INTERRUPTS_HELPER = _Common.get_prj_src_path() / "stc-agent-proc-interrupts-helper"

@pytest.fixture(name="params", scope="module")
def get_params(hostspec: str, username: str) -> Generator[_TestParamsTypedDict, None, None]:
    """
    Create and yield test parameters for the given host.

    Args:
        hostspec: The host specification to create a process manager for.
        username: The username to use when connecting to a remote host.

    Yields:
        A dictionary containing the process manager and 'stc-agent' path.
    """

    with _Common.get_pman(hostspec, username=username) as pman:
        if typing.TYPE_CHECKING:
            params = cast(_TestParamsTypedDict, _Common.build_params(pman))
        else:
            params = _Common.build_params(pman)

        # On the local host, prefer the in-tree 'stc-agent'. On a remote host, use
        # 'get_deploy_path()' to find the deployment directory, matching the same logic used by
        # the collector.
        if pman.is_remote:
            deploy_path = DeployHelpersBase.get_deploy_path("stats-collect", pman)
            stc_agent_path = deploy_path / "stc-agent"
            interrupts_helper_path = deploy_path / "stc-agent-proc-interrupts-helper"
        else:
            stc_agent_path = _LOCAL_STC_AGENT
            interrupts_helper_path = _LOCAL_INTERRUPTS_HELPER

        if not pman.exists(stc_agent_path):
            raise FileNotFoundError(f"'stc-agent' binary not found at '{stc_agent_path}'"
                                    f"{pman.hostmsg}.")

        params["stc_agent_path"] = stc_agent_path
        if pman.exists(interrupts_helper_path):
            params["interrupts_helper_path"] = interrupts_helper_path
        else:
            params["interrupts_helper_path"] = None

        yield params

def test_cmdl_help(params: _TestParamsTypedDict):
    """
    Test that 'stc-agent -h' prints usage information and exits successfully.

    Args:
        params: Test parameters including the process manager and 'stc-agent' path.
    """

    pman = params["pman"]
    stc_agent_path = params["stc_agent_path"]

    stdout, _, exitcode = pman.run_join(f"{stc_agent_path} -h")

    assert exitcode == 0, f"'stc-agent -h' exited with code {exitcode}"
    assert stdout, "'stc-agent -h' printed nothing to stdout"

def test_cmdl_mutual_exclusion(params: _TestParamsTypedDict):
    """
    Test that '--unix' and '--port' are mutually exclusive options.

    Args:
        params: Test parameters including the process manager and 'stc-agent' path.
    """

    pman = params["pman"]
    stc_agent_path = params["stc_agent_path"]

    _, stderr, exitcode = pman.run_join(f"{stc_agent_path} --unix /tmp/test.sock --port 0")

    assert exitcode != 0, "'stc-agent --unix <path> --port N' should have exited with an error"
    assert stderr, "'stc-agent --unix <path> --port N' printed nothing to stderr"

def test_cmdl_print_module_paths(params: _TestParamsTypedDict):
    """
    Test that '--print-module-paths' prints Python module paths and exits successfully.

    Args:
        params: Test parameters including the process manager and 'stc-agent' path.
    """

    pman = params["pman"]
    stc_agent_path = params["stc_agent_path"]

    stdout, _, exitcode = pman.run_nojoin(f"{stc_agent_path} --print-module-paths")

    assert exitcode == 0, f"'stc-agent --print-module-paths' exited with code {exitcode}"
    assert stdout, "'stc-agent --print-module-paths' printed nothing to stdout"
    for line in stdout:
        line = line.rstrip()
        assert line.endswith(".py"), \
               f"'stc-agent --print-module-paths' printed a non-.py line: {line}"

def _recv_msg(sock: socket.socket) -> str:
    """
    Receive one delimited message from the 'stc-agent' socket.

    Args:
        sock: The connected socket to receive from.

    Returns:
        The decoded message string with the delimiter stripped.
    """

    raw = b""
    while not raw.endswith(_Collectors.DELIMITER):
        chunk = sock.recv(4096)
        assert chunk, "Connection closed before a complete message was received"
        raw += chunk

    try:
        return raw[:-len(_Collectors.DELIMITER)].decode("utf-8")
    except UnicodeDecodeError as err:
        raise Error(f"Failed to decode 'stc-agent' response as UTF-8: {err}\n"
                    f"Raw response: {raw!r}") from err

def _send_cmd(sock: socket.socket, cmd: str):
    """
    Send one command to 'stc-agent' and raise the matching Exception on failure.

    Args:
        sock: The connected socket to send to and receive from.
        cmd: The command string to send.

    Raises:
        ErrorPermissionDenied: If the command failed due to insufficient permissions.
    """

    sock.sendall(cmd.encode() + _Collectors.DELIMITER)
    msg = _recv_msg(sock)
    if msg == "OK":
        return

    # Parse 'Error: <ClassName>: <message>' and raise the matching exception subclass.
    err_class = Error
    if msg.startswith("Error: "):
        remainder = msg[len("Error: "):]
        class_name, _, err_msg = remainder.partition(": ")
        candidate = getattr(Exceptions, class_name.strip(), None)
        if isinstance(candidate, type) and issubclass(candidate, Error):
            err_class = candidate
    else:
        err_msg = msg

    raise err_class(f"Command {cmd!r} failed: {err_msg}")

def _get_failed_collectors(sock: socket.socket) -> list[str]:
    """
    Send 'get-failed-collectors' and return the list of failed collector names.

    Args:
        sock: The connected socket to send the command through.

    Returns:
        The list of collector names reported as failed, or an empty list if none have failed.
    """

    sock.sendall(b"get-failed-collectors" + _Collectors.DELIMITER)
    msg = _recv_msg(sock)
    assert msg.startswith("OK"), f"'get-failed-collectors' command failed: {msg}"
    data = msg[len("OK"):].strip()
    return Trivial.split_csv_line(data)

@contextlib.contextmanager
def _start_stc_agent(pman: ProcessManagerType,
                     stc_agent_path: Path) -> Generator[tuple[ProcessType, int], None, None]:
    """
    Start 'stc-agent' and yield the process and the TCP port it is listening on.

    Args:
        pman: The process manager to use for running the command.
        stc_agent_path: Path to the 'stc-agent' binary on the target host.

    Yields:
        A tuple of the async process object and the TCP port number.
    """

    proc = pman.run_async(f"{stc_agent_path} --port 0")
    try:
        # 'stc-agent' prints a "Listening on TCP port N" message when ready.
        stdout, _, _ = proc.wait_nojoin(timeout=10, lines=(1, 0))
        assert stdout, "'stc-agent' did not print anything to stdout within the startup timeout"

        pfx = "Listening on TCP port "
        assert stdout[0].startswith(pfx), f"Unexpected 'stc-agent' startup output: {stdout[0]!r}"
        port = Trivial.str_to_int(stdout[0].split(pfx, maxsplit=1)[1].strip())

        yield proc, port
    finally:
        with contextlib.suppress(Exception):
            proc.close()

def test_exit_command(params: _TestParamsTypedDict):
    """
    Test that sending 'exit' to 'stc-agent' causes it to exit cleanly.

    Args:
        params: Test parameters including the process manager and 'stc-agent' path.
    """

    pman = params["pman"]
    stc_agent_path = params["stc_agent_path"]

    with _start_stc_agent(pman, stc_agent_path=stc_agent_path) as (proc, port):
        with socket.create_connection((pman.hostname, port), timeout=10) as sock:
            _send_cmd(sock, "exit")

        _, _, exitcode = proc.wait(timeout=10)
        assert exitcode == 0, f"'stc-agent' exited with code {exitcode}"

def _subtest_start_stop_interrupts(pman: ProcessManagerType,
                                   sock: socket.socket,
                                   outdir: Path,
                                   interrupts_helper_path: Path):
    """
    Run a configure -> start -> stop cycle for the interrupts collector.

    Args:
        pman: The process manager for verification after collection.
        sock: The connected socket to send commands through.
        outdir: The directory for collector output files.
        interrupts_helper_path: Path to the 'stc-agent-proc-interrupts-helper' binary.
    """

    _send_cmd(sock, "set-stats interrupts")
    _send_cmd(sock, f"set-collector-property interrupts outdir {outdir}")
    _send_cmd(sock, f"set-collector-property interrupts logdir {outdir / 'log'}")
    _send_cmd(sock, "set-collector-property interrupts interval 1")
    _send_cmd(sock, f"set-collector-property interrupts toolpath {interrupts_helper_path}")
    _send_cmd(sock, "configure")
    _send_cmd(sock, "start")

    # Wait for at least one collection interval so the output file has data.
    time.sleep(2)

    _send_cmd(sock, "stop")

    outfile = outdir / "interrupts.raw.txt"
    assert pman.exists(outfile), f"Output file '{outfile}' was not created"

    raw = pman.read_file(outfile)
    parser = InterruptsParser.InterruptsParser(lines=iter(raw.splitlines()))
    for _ in parser.next():
        break
    else:
        assert False, f"The interrupts output file '{outfile}' contains no snapshots"

def _subtest_start_stop_turbostat(pman: ProcessManagerType, sock: socket.socket, outdir: Path):
    """
    Run a configure -> start -> stop cycle for the turbostat collector.

    Args:
        pman: The process manager for verification after collection.
        sock: The connected socket to send commands through.
        outdir: The directory for collector output files.

    Notes:
        - Skip the subtest if the collector reports 'ErrorPermissionDenied', which happens when the
          test runs as an unprivileged user.
    """

    try:
        _send_cmd(sock, "set-stats turbostat")
    except ErrorPermissionDenied:
        return

    _send_cmd(sock, f"set-collector-property turbostat outdir {outdir}")
    _send_cmd(sock, f"set-collector-property turbostat logdir {outdir / 'log'}")
    _send_cmd(sock, "set-collector-property turbostat interval 1")
    _send_cmd(sock, "configure")
    _send_cmd(sock, "start")

    # Wait for at least one collection interval so the output file has data.
    time.sleep(2)

    _send_cmd(sock, "stop")

    outfile = outdir / "turbostat.raw.txt"
    assert pman.exists(outfile), f"Output file '{outfile}' was not created"

    raw = pman.read_file(outfile)
    parser = TurbostatParser.TurbostatParser(lines=iter(raw.splitlines()))
    for _ in parser.next():
        break
    else:
        assert False, f"The turbostat output file '{outfile}' contains no snapshots"

def test_start_stop(params: _TestParamsTypedDict):
    """
    Test a full configure -> start -> stop cycle for each supported collector.

    Start 'stc-agent' once and run each collector subtest sequentially using the same agent
    process. Verify that all commands succeed and the output files contain valid data.

    Args:
        params: Test parameters including the process manager and 'stc-agent' path.
    """

    pman = params["pman"]
    stc_agent_path = params["stc_agent_path"]
    interrupts_helper_path = params["interrupts_helper_path"]

    turbostat_path = pman.which_or_none("turbostat")

    if interrupts_helper_path is None and turbostat_path is None:
        pytest.skip("No supported collectors available")

    with contextlib.ExitStack() as stack:
        proc, port = stack.enter_context(_start_stc_agent(pman, stc_agent_path=stc_agent_path))
        outdir = stack.enter_context(pman.mkdtemp_ctx(prefix="stc_start_stop_"))
        sock = stack.enter_context(socket.create_connection((pman.hostname, port), timeout=10))

        if interrupts_helper_path is not None:
            subdir = outdir / "interrupts"
            pman.mkdir(subdir)
            _subtest_start_stop_interrupts(pman, sock=sock, outdir=subdir,
                                           interrupts_helper_path=interrupts_helper_path)

        if turbostat_path is not None:
            subdir = outdir / "turbostat"
            pman.mkdir(subdir)
            _subtest_start_stop_turbostat(pman, sock=sock, outdir=subdir)

        _send_cmd(sock, "exit")
        _, _, exitcode = proc.wait(timeout=10)
        assert exitcode == 0, f"'stc-agent' exited with code {exitcode}"

def _configure_collectors(sock: socket.socket,
                          outdir: Path,
                          interrupts_helper_path: Path | None,
                          turbostat_path: Path | None) -> list[Path]:
    """
    Configure all available collectors on 'sock', writing output to 'outdir'.

    Args:
        sock: The connected socket to send commands through.
        outdir: The directory for collector output files.
        interrupts_helper_path: Path to the interrupts helper, or 'None' if unavailable.
        turbostat_path: Path to turbostat, or 'None' if unavailable.

    Returns:
        The list of binary paths for collectors that were successfully configured.
    """

    collector_paths: list[Path] = []

    if interrupts_helper_path is not None:
        try:
            _send_cmd(sock, "set-stats interrupts")
            collector_paths.append(interrupts_helper_path)
        except ErrorPermissionDenied:
            pass

    if turbostat_path is not None:
        try:
            _send_cmd(sock, "set-stats turbostat")
            collector_paths.append(turbostat_path)
        except ErrorPermissionDenied:
            pass

    if interrupts_helper_path in collector_paths:
        _send_cmd(sock, f"set-collector-property interrupts outdir {outdir}")
        _send_cmd(sock, f"set-collector-property interrupts logdir {outdir / 'log'}")
        _send_cmd(sock, "set-collector-property interrupts interval 1")
        _send_cmd(sock, f"set-collector-property interrupts toolpath {interrupts_helper_path}")

    if turbostat_path in collector_paths:
        _send_cmd(sock, f"set-collector-property turbostat outdir {outdir}")
        _send_cmd(sock, f"set-collector-property turbostat logdir {outdir / 'log'}")
        _send_cmd(sock, "set-collector-property turbostat interval 1")

    _send_cmd(sock, "configure")

    return collector_paths

def test_stale_process_cleanup(params: _TestParamsTypedDict):
    """
    Test that stc-agent kills stale collector processes left over from a previous run.

    Scenario:
     1. Start stc-agent, configure and start all available collectors (interrupts, turbostat).
     2. Kill stc-agent with SIGKILL so it has no chance to clean up.
     3. Verify that all collector processes are still running (stale).
     4. Start a fresh stc-agent and run 'configure' for the same collectors.
     5. Verify that all stale collector processes have been killed.
     6. Start the collectors, stop them, then exit stc-agent cleanly.
     7. Verify that all collector processes have been stopped.

    Args:
        params: Test parameters including the process manager and 'stc-agent' path.
    """

    pman = params["pman"]
    stc_agent_path = params["stc_agent_path"]

    interrupts_helper_path = params["interrupts_helper_path"]
    turbostat_path = pman.which_or_none("turbostat")

    if interrupts_helper_path is None and turbostat_path is None:
        pytest.skip("No supported collectors available")

    with contextlib.ExitStack() as stack:
        proc, port = stack.enter_context(_start_stc_agent(pman, stc_agent_path=stc_agent_path))
        outdir = stack.enter_context(pman.mkdtemp_ctx(prefix="stc_stale_cleanup_"))
        sock = socket.create_connection((pman.hostname, port), timeout=10)

        configured = _configure_collectors(sock, outdir=outdir,
                                           interrupts_helper_path=interrupts_helper_path,
                                           turbostat_path=turbostat_path)
        if not configured:
            pytest.skip("No collectors could be configured (insufficient privileges)")

        _send_cmd(sock, "start")

        # Give the collectors a moment to start.
        time.sleep(1)

        try:
            # Kill stc-agent with SIGKILL, no cleanup will run.
            ProcHelpers.signal_pids([proc.pid], pman=pman, sig=signal.SIGKILL, must_die=True,
                                    interval=0)
            proc.wait(timeout=5)
        finally:
            # Close the socket after killing, the connection is broken so suppress the error.
            with contextlib.suppress(OSError):
                sock.close()

        # All collectors must still be running after stc-agent was killed.
        for path in configured:
            procs = ProcHelpers.grep_processes(path.name, pman=pman)
            assert procs, f"Expected '{path.name}' to be running after SIGKILL to stc-agent"

    # Start a fresh stc-agent and configure the same collectors, this should trigger cleanup of the
    # stale processes.
    with contextlib.ExitStack() as stack:
        proc, port = stack.enter_context(_start_stc_agent(pman, stc_agent_path=stc_agent_path))
        outdir = stack.enter_context(pman.mkdtemp_ctx(prefix="stc_stale_cleanup2_"))
        sock = stack.enter_context(socket.create_connection((pman.hostname, port), timeout=10))

        _configure_collectors(sock, outdir=outdir,
                              interrupts_helper_path=interrupts_helper_path,
                              turbostat_path=turbostat_path)

        # All stale collectors must be gone after the fresh stc-agent configured its collectors.
        still_running = []
        for path in configured:
            still_running.extend(ProcHelpers.grep_processes(path.name, pman=pman))

        assert not still_running, \
               f"Stale collector processes still running: {still_running}"

        _send_cmd(sock, "start")

        # Give the collectors a moment to start.
        time.sleep(1)

        _send_cmd(sock, "stop")
        _send_cmd(sock, "exit")
        _, _, exitcode = proc.wait(timeout=10)
        assert exitcode == 0, f"Second 'stc-agent' exited with code {exitcode}"

    # After a clean exit, all collector processes must have been stopped.
    still_running = []
    for path in configured:
        still_running.extend(ProcHelpers.grep_processes(path.name, pman=pman))

    assert not still_running, \
           f"Collector processes still running after clean 'stc-agent' exit: {still_running}"

def test_failed_collectors(params: _TestParamsTypedDict):
    """
    Test that 'get-failed-collectors' reports collectors that died during a run.

    Scenario:
     1. Start stc-agent and configure collectors (prefer turbostat, fall back to interrupts).
     2. Start collection.
     3. Verify the victim collector is running, then kill it externally.
     4. Send 'stop' - it must succeed, but the victim must appear in 'get-failed-collectors'.
     5. Verify that 'get-failed-collectors' reports the victim collector name.
     6. Send 'exit' and verify stc-agent exits cleanly.

    Args:
        params: Test parameters including the process manager and 'stc-agent' path.
    """

    pman = params["pman"]
    stc_agent_path = params["stc_agent_path"]
    interrupts_helper_path = params["interrupts_helper_path"]
    turbostat_path = pman.which_or_none("turbostat")

    if interrupts_helper_path is None and turbostat_path is None:
        pytest.skip("No supported collectors available")

    with contextlib.ExitStack() as stack:
        proc, port = stack.enter_context(_start_stc_agent(pman, stc_agent_path=stc_agent_path))
        outdir = stack.enter_context(pman.mkdtemp_ctx(prefix="stc_failed_collectors_"))
        sock = stack.enter_context(socket.create_connection((pman.hostname, port), timeout=10))

        configured = _configure_collectors(sock, outdir=outdir,
                                           interrupts_helper_path=interrupts_helper_path,
                                           turbostat_path=turbostat_path)
        if not configured:
            pytest.skip("No collectors could be configured (insufficient privileges)")

        # Prefer turbostat as the victim; fall back to the interrupts helper.
        if turbostat_path in configured:
            victim_name = "turbostat"
            victim_regex = "turbostat"
            victim_su = True
        else:
            victim_name = "interrupts"
            victim_regex = interrupts_helper_path.name
            victim_su = False

        _send_cmd(sock, "start")

        # Give the collectors a moment to start.
        time.sleep(1)

        # Verify the victim is running, then kill it externally so stc-agent is unaware.
        procs = ProcHelpers.grep_processes(victim_regex, pman=pman)
        assert procs, f"Expected '{victim_regex}' to be running after 'start'"
        victim_pids = [pid for pid, _ in procs]
        ProcHelpers.signal_pids(victim_pids, pman=pman, sig=signal.SIGKILL, must_die=True,
                                interval=0, su=victim_su)

        # 'stop' must succeed even though the victim exited prematurely.
        _send_cmd(sock, "stop")

        # The victim must be reported as a failed collector.
        failed = _get_failed_collectors(sock)
        assert victim_name in failed, \
               f"Expected '{victim_name}' in 'get-failed-collectors' response, got: {failed}"

        _send_cmd(sock, "exit")
        _, _, exitcode = proc.wait(timeout=10)
        assert exitcode == 0, f"'stc-agent' exited with code {exitcode}"
