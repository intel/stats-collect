#!/usr/bin/python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
stc-wl-cpu-wake-walk - a stats-collect workload for measuring an idle CPU which wakes up with
certain wake period (launch distance). Walk through user-specified wake periods.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import sys
import json
import time
import typing
import argparse
from pathlib import Path
from pepclibs.helperlibs import Logging, ArgParse, Human, Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import _HelpersCommon
from statscollectlibs.helperlibs import ProcHelpers

if typing.TYPE_CHECKING:
    from typing import IO, Iterator, TypedDict
    from statscollectlibs.mdc.MDCBase import MDTypedDict

    class _ArgsTypedDict(TypedDict, total=False):
        """
        A typed dictionary representing command line arguments.

        Attributes:
            pipe_path: Path to the named pipe on the SUT where the labels should be written to.
            ldist: A tuple with the launch distance range in nanoseconds.
            ldist_step_pct: The launch distance step in percent (0.0 if absolute step is used).
            ldist_step_ns: The launch distance step in nanoseconds (0 if percent step is used).
            span: For how long (in seconds) a single launch distance value should be measured.
            cpu: CPU number to bind the workload to.
        """

        pipe_path: Path
        ldist: tuple[int, int]
        ldist_step_pct: int | float
        ldist_step_ns: int
        span: int
        cpu: int

TOOLNAME = "stc-wl-cpu-wake-walk"
VERSION = "0.1"

_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=TOOLNAME)

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    text = sys.modules[__name__].__doc__
    parser = ArgParse.ArgsParser(description=text, prog=TOOLNAME, ver=VERSION)

    duration_descr = "d - days, h - hours, m - minutes, s - seconds"
    duration_ns_descr = "ms - milliseconds, us - microseconds, ns - nanoseconds"

    text = f"""This workload sleeps for launch distance milliseconds, wakes up, sleeps again, and
               repeats so for SPAN amount of seconds. Then it increases the launch distance by
               the LDIST_STEP amount of milliseconds, and repeats the process until it walks
               through the entire launch distance range. Specify the launch distance range to go
               through. The default range is [100us,50ms], but it can be overridden with this option
               by specifying a comma-separated range. The default unit is microseconds, but the
               following unit specifiers can be used: {duration_ns_descr}. For example, '--ldist
               500us,100ms' would be a [0.5, 100] milliseconds range."""
    parser.add_argument("-l", "--ldist", help=text, default="100us,50ms")

    text = f"""The launch distance step. By default it is 1%%. A percent value or an absolute time
               value can be specified. In the latter case, one of the following specifiers can be
               used: {duration_ns_descr}. For example, '--ldist-step=1ms' means that launch distance
               will be incremented by 1 millisecond on every iteration. If no unit was specified,
               microseconds are assumed."""
    parser.add_argument("-S", "--ldist-step", help=text, default="1%%")

    text = f"""For how long a single launch distance value should be measured. By default, it is 1
               minute. Specify time value in minutes, or use one of the following specifiers:
               {duration_descr}. For example, '--span=40s' or '--span=1m' would mean mean 40 seconds
                or 1 minute, respectively."""
    parser.add_argument("--span", help=text, default="1m")

    text = """CPU number to bind the workload to (CPU 0 by default). """
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

    ldist = Human.parse_human_range(args.ldist, unit="s", target_unit="ns",
                                    what="launch distance")
    if ldist[0] < 0 or ldist[1] < 0:
        raise Error(f"Bad launch distance range '{args.ldist}', values cannot be negative")
    if ldist[0] >= ldist[1]:
        raise Error(f"Bad launch distance range '{args.ldist}', the min. value must be less than "
                    "the max. value")

    ldist_step_pct, ldist_step_ns = 0.0, 0
    if args.ldist_step.endswith("%"):
        ldist_step_pct = Trivial.str_to_num(args.ldist_step.rstrip("%"))
    else:
        ldist_step_ns = Human.parse_human_int(args.ldist_step, unit="s", target_unit="ns",
                                              what="launch distance step")

    span = Human.parse_human_int(args.span, unit="s", target_unit="s", what="span")
    if span <= 0:
        raise Error(f"Bad span value '{args.span}', it must be positive")
    if span < 10:
        raise Error(f"The span value '{args.span}' is too small, min. span value is 10 "
                    f"seconds")

    cpu: int = args.cpu
    if not Trivial.is_int(cpu):
        raise Error(f"Bad CPU number '{cpu}', it must be an integer")
    if cpu < 0:
        raise Error(f"Bad CPU number '{cpu}', it must be non-negative")

    cmdl: _ArgsTypedDict = {}
    cmdl["pipe_path"] = pipe_path
    cmdl["ldist"] = round(ldist[0]), round(ldist[1])
    cmdl["ldist_step_pct"] = ldist_step_pct
    cmdl["ldist_step_ns"] = ldist_step_ns
    cmdl["span"] = span
    cmdl["cpu"] = cpu
    return cmdl

def _parse_arguments() -> _ArgsTypedDict:
    """Parse input arguments."""

    parser = _build_arguments_parser()
    args = parser.parse_args()

    if args.print_module_paths:
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

        self._pipe_path = cmdl["pipe_path"]
        self._ldist = cmdl["ldist"]
        self._ldist_step_pct = cmdl["ldist_step_pct"]
        self._ldist_step_ns = cmdl["ldist_step_ns"]
        self._span = cmdl["span"]

        self._span_human = Human.duration(self._span)
        self._pipe: IO[str]

        ProcHelpers.bind_pid(Trivial.get_pid(), cmdl["cpu"])

        try:
            # pylint: disable-next=consider-using-with
            self._pipe = open(cmdl["pipe_path"], "w", encoding="utf-8")
            _LOG.debug(f"Opened the named pipe '{cmdl['pipe_path']}' for writing")
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to open the named pipe '{cmdl['pipe_path']}' for writing:\n"
                        f"{errmsg}") from None

    def close(self):
        """Uninitialize the object."""

        if getattr(self, "_pipe", False):
            self._pipe.close()

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
            "name": "LDist",
            "title": "Launch Distance",
            "descr": f"For how the '{TOOLNAME}' workload sleeps before the next wake up.",
            "type": "int",
            "unit": "nanosecond",
            "short_unit": "ns",
            "scope": "CPU",
        }

        label = {"name": "wlinfo", "wlname": TOOLNAME, "MDD": {"LDist": mdd}}

        try:
            mdd_json = json.dumps(label)
        except ValueError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Failed to serialize MDD as JSON:\n{msg}") from err

        self._write_json(mdd_json)

    def _write_label(self, name: str, ldist: int | None = None):
        """
        Write a label to the named pipe in JSON format.

        Args:
            name: The label name.
            ldist: The launch distance value to include in the label.
        """

        label: dict[str, str | int] = {"name": name}
        if ldist is not None:
            label["LDist"] = ldist

        try:
            label_json = json.dumps(label)
        except ValueError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Failed to serialize a label as JSON:\n{msg}") from err

        self._write_json(label_json)

    def _get_ldist(self) -> Iterator[int]:
        """
        Yield all launch distance values starting from the initial value in 'self._ldist[0]'.

        Yields:
            The next launch distance value.
        """

        ldist = self._ldist[0]
        yield ldist

        while True:
            if self._ldist_step_pct:
                ldist += int((ldist * self._ldist_step_pct) / 100.0)
            else:
                ldist += self._ldist_step_ns

            if ldist > self._ldist[1]:
                break

            yield ldist

    def _run_iteration(self, ldist: int):
        """
        Run a single iteration of the workload: wake up every 'ldist' nanoseconds for 'span' amount
        of seconds.

        Args:
            ldist: The interval in nanoseconds between wake-ups.
        """

        human_ldist = Human.num2si(ldist, unit="ns")
        _LOG.info(f"Launch distance {human_ldist}, span {self._span_human}")

        delta = 0
        start_time = time.time()
        self._write_label("start", ldist=ldist)
        while delta <= self._span:
            # Convert nanoseconds to seconds for 'sleep()'.
            time.sleep(ldist / 1_000_000_000)
            delta = round(time.time() - start_time)
        self._write_label("skip")

    def run(self):
        """Run the workload."""

        self._write_wlinfo()

        for ldist in self._get_ldist():
            self._run_iteration(ldist)

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
