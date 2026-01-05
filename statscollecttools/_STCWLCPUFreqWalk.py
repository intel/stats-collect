
#!/usr/bin/python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
stc-wl-cpu-freq-walk - a stats-collect workload for measuring the system while locking CPU frequency
at different levels. Run a simple busy loop workload on the target CPU while walking through the CPU
frequency range.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import sys
import time
import json
import typing
import argparse
from pathlib import Path
from pepclibs import PStates, CPUInfo
from pepclibs.helperlibs import Logging, ArgParse, ClassHelpers, Human, Trivial, LocalProcessManager
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import _HelpersCommon
from statscollectlibs.helperlibs import ProcHelpers

TOOLNAME = "stc-wl-cpu-freq-walk"
VERSION = "0.1"

_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=TOOLNAME)

if typing.TYPE_CHECKING:
    from typing import TypedDict, Iterator
    from statscollectlibs.mdc.MDCBase import MDTypedDict

    class _ArgsTypedDict(TypedDict, total=False):
        """
        A typed dictionary representing command line arguments.

        Attributes:
            freq_range: Tuple with minimum and maximum frequencies as strings.
            interval: Interval between frequency changes in seconds.
            step: Frequency increment step in Hz.
            pipe_path: Path to the named pipe on the SUT where the labels should be written to.
            cpu: CPU number to walk frequencies on.
        """

        freq_range: tuple[str, str]
        interval: int
        step: int
        pipe_path: Path
        cpu: int

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    text = sys.modules[__name__].__doc__
    parser = ArgParse.ArgsParser(description=text, prog=TOOLNAME, ver=VERSION)

    text = """The CPU frequency range to walk through. The format is MIN_FREQ,MAX_FREQ where the
              frequencies are in Hz by default. You can specify kHz, MHz, or GHz suffixes. For
              example, '--freq-range 800MHz,3.5GHz'. Use special value 'min' to indicate the minimum
              possible frequency and 'max' to indicate the maximum possible frequency. For example,
              '--freq-range min,max'. will walk through the entire frequency range supported by the
              CPU."""
    parser.add_argument("--freq-range", help=text, default="min,max")

    text = """Interval between frequency changes. The default is 20s. You can use suffixes like
              's' for seconds, 'm' for minutes, etc. For example, '--interval 30s'."""
    parser.add_argument("--interval", help=text, default="20s")

    text = """Frequency increment step in Hz. The default is 10MHz."""
    parser.add_argument("--step", help=text, default="10MHz")

    text = """CPU number to to walk frequencies on. Default is CPU 0."""
    parser.add_argument("--cpu", help=text, type=int, default=0)

    text = """Path to the named pipe on the SUT where the labels should be written to."""
    parser.add_argument("--pipe-path", help=text, type=Path)

    # This is a hidden option for printing paths to dependencies. Required for building a standalone
    # version of this script.
    parser.add_argument("--print-module-paths", action="store_true", help=argparse.SUPPRESS)

    return parser

def _format_args(args: argparse.Namespace) -> _ArgsTypedDict:
    """
    Validate and format the command line arguments, then build and return the arguments typed
    dictionary.

    Args:
        args: The input arguments parsed from the command line.

    Returns:
        _ArgsTypedDict: The formatted arguments.
    """

    if not args.pipe_path:
        raise Error("Please, specify the named pipe path using the '--pipe-path' option")

    pipe_path = Path(args.pipe_path)

    try:
        if not pipe_path:
            raise Error(f"The named pipe '{pipe_path}' does not exist")
    except OSError as err:
        errmsg = Error(str(err)).indent(2)
        raise Error(f"Failed to check if the named pipe '{pipe_path}' exists:\n{errmsg}") from None

    freq_range: list[str] = args.freq_range.split(",")
    if len(freq_range) != 2:
        raise Error(f"Bad frequency range '{args.freq_range}', it must be in the format "
                    "'MIN_FREQ,MAX_FREQ'")

    interval = Human.parse_human_int(args.interval, unit="s", target_unit="s",
                                     what="interval between frequency changes")
    if interval < 5:
        raise Error(f"Bad interval '{args.interval}', it must be at least 5 seconds")

    step = Human.parse_human_int(args.step, unit="Hz", target_unit="Hz",
                                 what="frequency increment step")
    if step <= 0:
        raise Error(f"Bad frequency increment step '{args.step}', it must be positive")

    cpu: int = args.cpu
    if not Trivial.is_int(cpu):
        raise Error(f"Bad CPU number '{cpu}', it must be an integer")
    if cpu < 0:
        raise Error(f"Bad CPU number '{cpu}', it must be non-negative")

    cmdl: _ArgsTypedDict = {}
    cmdl["freq_range"] = (freq_range[0].strip(), freq_range[1].strip())
    cmdl["interval"] = interval
    cmdl["step"] = step
    cmdl["pipe_path"] = pipe_path
    cmdl["cpu"] = cpu
    return cmdl

def _parse_arguments() -> _ArgsTypedDict:
    """Parse input arguments."""

    parser = _build_arguments_parser()
    args = parser.parse_args()

    if args.print_module_paths:
        try:
            # The reason for this block is to ensure that PStates module imports all the necessary
            # sub-modules so that their paths are printed as well.
            pobj = PStates.PStates()
            pobj.get_cpu_prop_int("min_freq", 0, mnames=("sysfs",))
        except Error:
            pass
        _HelpersCommon.print_module_paths()
        sys.exit(0)

    return _format_args(args)

class _Runner(ClassHelpers.SimpleCloseContext):
    """
    Manage and execute a workload that periodically wakes up at configurable intervals,
    writing progress and metadata to a named pipe.
    """

    def __init__(self, cmdl: _ArgsTypedDict):
        """
        Initialize a class instance.

        Args:
            cmdl: The command line arguments typed dictionary.
        """

        self._interval = cmdl["interval"]
        self._step = cmdl["step"]
        self._cpu = cmdl["cpu"]
        self._pipe_path = cmdl["pipe_path"]

        self._lpman = LocalProcessManager.LocalProcessManager()
        self._proc: LocalProcessManager.LocalProcess

        self._cpuinfo = CPUInfo.CPUInfo(pman=self._lpman)
        self._pobj = PStates.PStates(pman=self._lpman, cpuinfo=self._cpuinfo)

        self._saved_freqs: dict[int, tuple[int, int]] = {}

        try:
            # pylint: disable-next=consider-using-with
            self._pipe = open(cmdl["pipe_path"], "w", encoding="utf-8")
            _LOG.debug(f"Opened the named pipe '{cmdl['pipe_path']}' for writing")
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to open the named pipe '{cmdl['pipe_path']}' for writing:\n"
                        f"{errmsg}") from None

        min_freq_limit = self._pobj.get_cpu_prop_int("min_freq_limit", self._cpu, mnames=("sysfs",))
        max_freq_limit = self._pobj.get_cpu_prop_int("max_freq_limit", self._cpu, mnames=("sysfs",))

        if cmdl["freq_range"][0].lower() == "min":
            min_freq = min_freq_limit["val"]
        else:
            min_freq = Human.parse_human_int(cmdl["freq_range"][0], "Hz")

        if cmdl["freq_range"][1].lower() == "max":
            max_freq = max_freq_limit["val"]
        else:
            max_freq = Human.parse_human_int(cmdl["freq_range"][1], "Hz")

        if min_freq < min_freq_limit["val"]:
            human_min_freq_limit = Human.num2si(min_freq_limit["val"], unit="Hz")
            raise Error(f"The specified minimum frequency {min_freq} Hz is less than the minimum "
                        f"frequency limit {human_min_freq_limit} Hz for CPU {self._cpu}")
        if max_freq > max_freq_limit["val"]:
            human_max_freq_limit = Human.num2si(max_freq_limit["val"], unit="Hz")
            raise Error(f"The specified maximum frequency {max_freq} Hz is greater than the "
                        f"maximum frequency limit {human_max_freq_limit} Hz for CPU {self._cpu}")

        self._freq_range = (min_freq, max_freq)

    def close(self):
        """Uninitialize the object."""

        if getattr(self, "_proc", False):
            ProcHelpers.kill_pids(self._proc.pid, kill_children=False, must_die=True,
                                  pman=self._lpman)
            setattr(self, "_proc", None)

        ClassHelpers.close(self, close_attrs=("_pobj", "_cpuinfo", "_pipe", "_lpman"))

    def _start_workload(self):
        """
        Start a workload to keep the CPU busy.
        """

        # Kill any existing busy loop processes started by this tool.
        regex = ".* # stc-wl-cpu-freq-walk.*"
        ProcHelpers.kill_processes(regex, kill_children=False, log=True,
                                   name=f"{TOOLNAME} busy loop", pman=self._lpman)

        # Use a comment at the end of the busy loop command to make it easier to identify the
        # process.
        busy_loop_cmd = f"taskset -c {self._cpu} sh -c 'while :; do :; done # stc-wl-cpu-freq-walk'"

        self._proc = self._lpman.run_async(busy_loop_cmd)

    def _stop_workload(self):
        """
        Stop the busy loop workload.
        """

        ProcHelpers.kill_pids(self._proc.pid, kill_children=False, must_die=True,
                              pman=self._lpman)
        setattr(self, "_proc", None)

    def _configure(self):
        """
        Configure the CPU frequency settings before starting the frequency walk.
        """

        _LOG.info("Configuring CPU frequency settings")

        cpus = self._cpuinfo.get_cpus()

        # Save the current frequency limits to restore them later.
        min_freq_iter = self._pobj.get_prop_cpus_int("min_freq", cpus, mnames=("sysfs",))
        max_freq_iter = self._pobj.get_prop_cpus_int("max_freq", cpus, mnames=("sysfs",))
        for min_freq_pvinfo, max_freq_pvinfo in zip(min_freq_iter, max_freq_iter):
            cpu = min_freq_pvinfo["cpu"]
            self._saved_freqs[cpu] = (min_freq_pvinfo["val"], max_freq_pvinfo["val"])

        # CPU frequency limits are often shared across a frequency domain (multiple CPUs).
        # The effective frequency is the maximum of all limits in that domain.
        # To ensure the target CPU runs at the requested frequency, set all CPUs in the system
        # to the minimum frequency in our walk range.
        #
        # Reason for setting max_freq to "max" first: if the current min_freq is higher than current
        # max_freq, setting min_freq to the desired value will fail. Setting max_freq to "max" first
        # prevents the failure.
        self._pobj.set_prop_cpus("max_freq", "max", cpus, mnames=("sysfs",))
        self._pobj.set_prop_cpus("min_freq", self._freq_range[0], cpus, mnames=("sysfs",))
        self._pobj.set_prop_cpus("max_freq", self._freq_range[0], cpus, mnames=("sysfs",))

    def _restore_configuration(self):
        """
        Restore the CPU frequency settings saved before starting the frequency walk.
        """

        _LOG.info("Restoring CPU frequency settings")

        for cpu, (min_freq, max_freq) in self._saved_freqs.items():
            # If the current min_freq exceeds the saved max_freq, attempting to restore max_freq
            # will fail. Setting min_freq to the absolute minimum prevents this issue.
            self._pobj.set_cpu_prop("min_freq", "min", cpu, mnames=("sysfs",))

            self._pobj.set_cpu_prop("max_freq", max_freq, cpu, mnames=("sysfs",))
            self._pobj.set_cpu_prop("min_freq", min_freq, cpu, mnames=("sysfs",))

    def _write_json(self, json_str: str):
        """
        Write a JSON-formatted string to the named pipe.

        Args:
            json_str: the string to write.
        """

        try:
            _LOG.debug(f"Writing a the following JSON string to the named pipe "
                       f"'{self._pipe_path}':\n  {json_str}")
            self._pipe.write(json_str + "\n")
            self._pipe.flush()
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to write a JSON string to the named pipe '{self._pipe_path}':\n"
                        f"{errmsg}") from err

    def _write_wlinfo(self):
        """
        Write the workload information label to the named pipe.
        """

        mdd: MDTypedDict = {
            "name": "ReqFreq",
            "title": "Requested CPU Frequency",
            "descr": f"The CPU frequency requested by the {TOOLNAME} workload via sysfs.",
            "type": "int",
            "unit": "hertz",
            "short_unit": "Hz",
            "scope": "CPU",
        }

        label = {"name": "wlinfo", "wlname": TOOLNAME, "MDD": {"ReqFreq": mdd}}

        try:
            mdd_json = json.dumps(label)
        except ValueError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Failed to serialize MDD as JSON:\n{msg}") from err

        self._write_json(mdd_json)

    def _write_label(self, name: str, freq: int | None = None):
        """
        Write a label to the named pipe in JSON format.

        Args:
            name: The label name.
            freq: The CPU frequency value to include in the label.
        """

        label: dict[str, str | int] = {"name": name}
        if freq is not None:
            label["ReqFreq"] = freq

        try:
            label_json = json.dumps(label)
        except ValueError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Failed to serialize a label as JSON:\n{msg}") from err

        self._write_json(label_json)

    def _get_freq(self) -> Iterator[int]:
        """
        Yield CPU frequency values starting from the initial value in 'self._freq_range[0]'.

        Yields:
            The next CPU frequency value.
        """

        freq = self._freq_range[0]
        yield freq

        while True:
            freq += self._step

            if freq > self._freq_range[1]:
                break
            yield freq

    def _run_iteration(self, freq: int):
        """
        Run a single iteration: set the CPU frequency and wait for the specified interval.

        Args:
            freq: The CPU frequency to set in Hz.
        """

        human_freq = Human.num2si(freq, unit="Hz")
        _LOG.info(f"Setting CPU frequency to {human_freq}, interval {self._interval}s")

        self._pobj.set_cpu_prop("max_freq", freq, self._cpu, mnames=("sysfs",))
        self._pobj.set_cpu_prop("min_freq", freq, self._cpu, mnames=("sysfs",))

        self._write_label("start", freq)
        time.sleep(self._interval)
        self._write_label("skip")

    def run(self):
        """Run the workload."""

        self._configure()
        self._start_workload()

        self._write_wlinfo()

        _LOG.info("Walking through the CPU frequency range %s - %s",
                  Human.num2si(self._freq_range[0], unit="Hz"),
                  Human.num2si(self._freq_range[1], unit="Hz"))

        for freq in self._get_freq():
            res = self._proc.wait(timeout=0, capture_output=False)
            if res.exitcode is not None:
                raise Error(f"The busy loop workload process exited unexpectedly with exit code "
                            f"{res.exitcode}")
            self._run_iteration(freq)

        self._stop_workload()

def main():
    """Implement main logic."""

    try:
        cmdl = _parse_arguments()
        with _Runner(cmdl) as runner:
            runner.run()
    except KeyboardInterrupt:
        _LOG.info("\nInterrupted, exiting")
        return -1
    except Error as err:
        _LOG.error_out(err)

    return 0
