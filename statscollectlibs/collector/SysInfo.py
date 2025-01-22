# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Collect the system information statistics.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.
import logging
from pathlib import Path
from typing import TypedDict
from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs.ProcessManager import ProcessManagerType

_LOG = logging.getLogger()

class _CmdInfoTypedDict(TypedDict, total=False):
    """
    A dictionary that describes the commands that have to be run on the SUT to collect system
    information.

    Attributes:
        cmd: the command to run.
        outfile: path to the output file to save redirect the output of the command to.
    """

    cmd: str
    outfile: Path

def _run_commands(cmdinfos: list[_CmdInfoTypedDict], pman: ProcessManagerType):
    """
    Execute commands specified in the 'cmdinfos' dictionary.

    Args:
        cmdinfos: describes the commands to execute.
        pman: The process manager object that defines the host to execute the commands on.
    """

    if pman.is_remote:
        # In case of a remote host, it is much more efficient to run all commands in one go, because
        # in this case only one SSH session needs to be established.
        cmd = ""
        for cmdinfo in cmdinfos:
            cmd += cmdinfo["cmd"] + " &"

        cmd += " wait"
        try:
            pman.run_verify(cmd, shell=True)
        except Error as err:
            _LOG.warning("Some system statistics were not collected")
            _LOG.debug(str(err))
    else:
        procs = []
        errors = []
        for cmdinfo in cmdinfos:
            try:
                procs.append(pman.run_async(cmdinfo["cmd"], shell=True))
            except Error as err:
                errors.append(str(err))

        for cmd_proc in procs:
            try:
                cmd_proc.wait(capture_output=False, timeout=5 * 60)
            except Error as err:
                errors.append(str(err))
            finally:
                cmd_proc.close()

        if errors:
            _LOG.warning("not all the system statistics were collected, here are the failures\n%s",
                         "\nNext error:\n".join(errors))

def _format_find_cmd(include: str, outfile: Path, exclude: str | None = None) -> str:
    """
    Format and return a 'find' tool command which finds and dump the contents of files found using
    regular expression 'include' into 'outfile'. If specified, exclude files matching the 'exclude'
    regular expression.

    Args:
        include: The regular expression for file names the 'find' tool should find.
        outfile: Path to the file the 'find' tool output should be redirected to.
        exclude: The regular expression for file names to exclude from the found files list.

    Returns:
        The 'find' tool command.
    """

    cmd = fr"""find /sys/devices/system/cpu/ -type f -regex '.*/{include}/.*' """
    if exclude:
        cmd += fr"""-not -regex '{exclude}' """
    cmd += fr"""-exec sh -c "echo '{{}}:'; cat '{{}}'; echo" \; > '{outfile}' 2>&1"""
    return cmd

def _collect_sysinfo(outdir: Path, when: str, pman: ProcessManagerType):
    """
    Collecting the system information statistics which may change after a workload has been run on
    the SUT. For example, 'dmesg' may have additional lines.

    Args:
        outdir: Path on the system defined by 'pman' to store the collected statistics in.
        when: "before" if collecting before the workload starts, "after" if collecting after the
              workload starts.
        pman: The process manager object that defines the host to collect the statistics on.
    """

    cmdinfos: list[_CmdInfoTypedDict] = []

    outfile = outdir / f"sys-cpuidle.{when}.raw.txt"
    cmd = _format_find_cmd("cpuidle", outfile)
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"sys-cpufreq.{when}.raw.txt"
    # Exclude 'scaling_cpu_freq' files -they are not very interesting.
    cmd = _format_find_cmd("cpufreq", outfile, exclude=".*/scaling_cur_freq")
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"sys-thermal_throttle.{when}.raw.txt"
    cmd = _format_find_cmd("thermal_throttle", outfile)
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"turbostat-d.{when}.raw.txt"
    cmd = f"turbostat -- sleep 1 > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"turbostat-d-c0.{when}.raw.txt"
    cmd = f"turbostat -c 0 -S -- sleep 0.01 > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"dmesg.{when}.raw.txt"
    cmd = f"dmesg --notime > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"x86_energy_perf_policy.{when}.raw.txt"
    cmd = f"x86_energy_perf_policy > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"interrupts.{when}.raw.txt"
    cmd = f"cat /proc/interrupts > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"sysctl-all.{when}.raw.txt"
    cmd = f"sysctl --all > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"pepc_cstates.{when}.raw.txt"
    cmd = f"pepc cstates info > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"pepc_pstates.{when}.raw.txt"
    cmd = f"pepc pstates info > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"pepc_pmqos.{when}.raw.txt"
    cmd = f"pepc pmqos info > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"pepc_aspm.{when}.raw.txt"
    cmd = f"pepc aspm info > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"pepc_topology.{when}.raw.txt"
    cmd = f"pepc topology info > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"pepc_power.{when}.raw.txt"
    cmd = f"pepc power info > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"lspci.{when}.raw.txt"
    cmd = f"lspci > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"lspci-vvv.{when}.raw.txt"
    cmd = f"lspci -vvv > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"lsusb.{when}.raw.txt"
    cmd = f"lsusb > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"lsusb-v.{when}.raw.txt"
    cmd = f"lsusb -v > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    _run_commands(cmdinfos, pman)

def collect_before(outdir: Path, pman: ProcessManagerType):
    """
    Collect system information statistics before running the workload.

    Args:
        outdir: Path on the system defined by 'pman' to store the collected statistics in.
        pman: The process manager object that defines the host to collect the statistics on.
    """

    pman.mkdir(outdir, parents=True, exist_ok=True)

    _collect_sysinfo(outdir, "before", pman)

def collect_after(outdir: Path, pman: ProcessManagerType):
    """
    Collect system information statistics after running the workload.

    Args:
        outdir: Path on the system defined by 'pman' to store the collected statistics in.
        pman: The process manager object that defines the host to collect the statistics on.
    """

    cmdinfos: list[_CmdInfoTypedDict] = []
    when = "after"

    outfile = outdir / f"proc_cmdline.{when}.raw.txt"
    cmd = f"cat /proc/cmdline > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"proc_cmdline.{when}.raw.txt"
    cmd = f"cat /proc/cmdline > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"uname-a.{when}.raw.txt"
    cmd = f"uname -a > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"dmidecode.{when}.raw.txt"
    cmd = f"dmidecode > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"proc_cpuinfo.{when}.raw.txt"
    cmd = f"cat /proc/cpuinfo > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"lsmod.{when}.raw.txt"
    cmd = f"lsmod > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    outfile = outdir / f"lsblk.{when}.raw.txt"
    cmd = f"lsblk > '{outfile}' 2>&1"
    cmdinfos.append(_CmdInfoTypedDict(cmd=cmd, outfile=outfile))

    _run_commands(cmdinfos, pman)

    _collect_sysinfo(outdir, when, pman)
