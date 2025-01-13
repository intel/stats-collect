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

import logging
from pepclibs.helperlibs.Exceptions import Error

_LOG = logging.getLogger()

def _run_commands(cmdinfos, pman):
    """Execute commands specified in the 'cmdinfos' dictionary."""

    if pman.is_remote:
        # In case of a remote host, it is much more efficient to run all commands in one go, because
        # in this case only one SSH session needs to be established.
        cmd = ""
        for cmdinfo in cmdinfos.values():
            cmd += cmdinfo["cmd"] + " &"

        cmd += " wait"
        try:
            pman.run_verify(cmd, shell=True)
        except Error as err:
            _LOG.warning("some system statistics were not collected")
            _LOG.debug(str(err))
    else:
        procs = []
        errors = []
        for cmdinfo in cmdinfos.values():
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

def _format_find_cmd(include, outfile, exclude=None):
    """
    Format and return a command which finds and dump the contents of files found using regular
    expression 'include' into 'outfile'. If specified, exclude files matching the 'exclude' regular
    expression.
    """

    cmd = fr"""find /sys/devices/system/cpu/ -type f -regex '.*/{include}/.*' """
    if exclude:
        cmd += fr"""-not -regex '{exclude}' """
    cmd += fr"""-exec sh -c "echo '{{}}:'; cat '{{}}'; echo" \; > '{outfile}' 2>&1"""
    return cmd

def _collect_sysinfo(outdir, when, pman):
    """
    Collecting the system information statistics which may change after a workload has been run on
    the SUT. For example, 'dmesg' may have additional lines. The 'when' argument is supposed to be
    either 'before' or 'after'.
    """

    cmdinfos = {}

    cmdinfos["cpuidle"] = cmdinfo = {}
    outfile = outdir / f"sys-cpuidle.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = _format_find_cmd("cpuidle", outfile)

    cmdinfos["cpufreq"] = cmdinfo = {}
    outfile = outdir / f"sys-cpufreq.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    # Exclude 'scaling_cpu_freq' files -they are not very interesting.
    cmdinfo["cmd"] = _format_find_cmd("cpufreq", outfile, exclude=".*/scaling_cur_freq")

    cmdinfos["thermal_throttle"] = cmdinfo = {}
    outfile = outdir / f"sys-thermal_throttle.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = _format_find_cmd("thermal_throttle", outfile)

    cmdinfos["turbostat"] = cmdinfo = {}
    outfile = outdir / f"turbostat-d.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"turbostat -- sleep 1 > '{outfile}' 2>&1"

    cmdinfos["turbostat_c0"] = cmdinfo = {}
    outfile = outdir / f"turbostat-d-c0.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"turbostat -c 0 -S -- sleep 0.01 > '{outfile}' 2>&1"

    cmdinfos["dmesg"] = cmdinfo = {}
    outfile = outdir / f"dmesg.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"dmesg --notime > '{outfile}' 2>&1"

    cmdinfos["x86_energy_perf_policy"] = cmdinfo = {}
    outfile = outdir / f"x86_energy_perf_policy.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"x86_energy_perf_policy > '{outfile}' 2>&1"

    cmdinfos["proc_interrupts"] = cmdinfo = {}
    outfile = outdir / f"interrupts.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"cat /proc/interrupts > '{outfile}' 2>&1"

    cmdinfos["sysctl_all"] = cmdinfo = {}
    outfile = outdir / f"sysctl-all.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"sysctl --all > '{outfile}' 2>&1"

    cmdinfos["pepc_cstates"] = cmdinfo = {}
    outfile = outdir / f"pepc_cstates.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"pepc cstates info > '{outfile}' 2>&1"

    cmdinfos["pepc_pstates"] = cmdinfo = {}
    outfile = outdir / f"pepc_pstates.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"pepc pstates info > '{outfile}' 2>&1"

    cmdinfos["pepc_pmqos"] = cmdinfo = {}
    outfile = outdir / f"pepc_pmqos.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"pepc pmqos info > '{outfile}' 2>&1"

    cmdinfos["pepc_aspm"] = cmdinfo = {}
    outfile = outdir / f"pepc_aspm.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"pepc aspm info > '{outfile}' 2>&1"

    cmdinfos["pepc_topology"] = cmdinfo = {}
    outfile = outdir / f"pepc_topology.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"pepc topology info > '{outfile}' 2>&1"

    cmdinfos["pepc_power"] = cmdinfo = {}
    outfile = outdir / f"pepc_power.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"pepc power info > '{outfile}' 2>&1"

    cmdinfos["lspci"] = cmdinfo = {}
    outfile = outdir / f"lspci.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lspci > '{outfile}' 2>&1"

    cmdinfos["lspci_vvv"] = cmdinfo = {}
    outfile = outdir / f"lspci-vvv.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lspci -vvv > '{outfile}' 2>&1"

    cmdinfos["lsusb"] = cmdinfo = {}
    outfile = outdir / f"lsusb.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lsusb > '{outfile}' 2>&1"

    cmdinfos["lsusb_v"] = cmdinfo = {}
    outfile = outdir / f"lsusb-v.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lsusb -v > '{outfile}' 2>&1"

    return _run_commands(cmdinfos, pman)

def collect_before(outdir, pman):
    """
    Collect system information statistics before running the workload. The arguments are as follows.
      * outdir - path on the system defined by 'pman' to store the collected statistics in.
      * pman - the process manager object that defines the host to collect the statistics on.
    """

    pman.mkdir(outdir, parents=True, exist_ok=True)

    _collect_sysinfo(outdir, "before", pman)

def collect_after(outdir, pman):
    """
    Collect system information statistics after running the workload. The arguments are as follows.
      * outdir - path on the system defined by 'pman' to store the collected statistics in.
      * pman - the process manager object that defines the host to collect the statistics on.
    """

    cmdinfos = {}
    when = "after"

    cmdinfos["proc_cmdline"] = cmdinfo = {}
    outfile = outdir / f"proc_cmdline.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"cat /proc/cmdline > '{outfile}' 2>&1"

    cmdinfos["uname_a"] = cmdinfo = {}
    outfile = outdir / f"uname-a.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"uname -a > '{outfile}' 2>&1"

    cmdinfos["dmidecode"] = cmdinfo = {}
    outfile = outdir / f"dmidecode.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"dmidecode > '{outfile}' 2>&1"

    cmdinfos["proc_cpuinfo"] = cmdinfo = {}
    outfile = outdir / f"proc_cpuinfo.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"cat /proc/cpuinfo > '{outfile}' 2>&1"

    cmdinfos["lsmod"] = cmdinfo = {}
    outfile = outdir / f"lsmod.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lsmod > '{outfile}' 2>&1"

    cmdinfos["lsblk"] = cmdinfo = {}
    outfile = outdir / f"lsblk.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lsblk > '{outfile}' 2>&1"

    _run_commands(cmdinfos, pman)

    _collect_sysinfo(outdir, when, pman)
