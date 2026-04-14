#!/usr/bin/python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
stc-agent-proc-interrupts-helper - collect interrupts statistics by making a periodic snapshot of
the '/proc/interrupts' file. This is an internal sub-tool of the 'stats-collect' tool, not intended
to be used directly by end users.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import re
import sys
import time
import typing
import argparse
from pepclibs.helperlibs import Logging, ArgParse
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import ToolInfo, _Common

if typing.TYPE_CHECKING:
    from typing import Final, TypedDict

    class _CmdlineArgsTypedDict(TypedDict, total=False):
        """
        Typed dictionary representing the command-line arguments.

        Attributes:
            interval: The interval between '/proc/interrupts' snapshots in seconds.
        """

        interval: float

_VERSION: Final[str] = ToolInfo.VERSION
_TOOLNAME: Final[str] = "stc-agent-proc-interrupts-helper"

# Configure the root 'main' logger, not a child logger, so that debug messages from pepclibs
# ('main.pepc.*') are also captured.
_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=_TOOLNAME)

def _build_arguments_parser() -> ArgParse.ArgsParser:
    """Build and return the arguments parser object."""

    text = sys.modules[__name__].__doc__
    parser = ArgParse.ArgsParser(description=text, prog=_TOOLNAME, ver=_VERSION)

    text = "The interval between '/proc/interrupts' snapshots in seconds. Default is 5."
    parser.add_argument("--interval", help=text, type=float, default=5)

    # Hidden option: print paths to 'stc-agent-proc-interrupts-helper' module dependencies and exit.
    parser.add_argument("--print-module-paths", action="store_true", help=argparse.SUPPRESS)
    return parser

def _parse_arguments() -> argparse.Namespace:
    """
    Parse the command-line arguments.

    Returns:
        The parsed arguments namespace.
    """

    parser = _build_arguments_parser()
    return parser.parse_args()

def _get_cmdline_args(args: argparse.Namespace) -> _CmdlineArgsTypedDict:
    """
    Format command-line arguments into a typed dictionary.

    Args:
        args: Command-line arguments namespace.

    Returns:
        A typed dictionary containing the validated and formatted command-line arguments.
    """

    cmdl: _CmdlineArgsTypedDict = {}
    cmdl["interval"] = args.interval

    if cmdl["interval"] <= 0:
        raise Error(f"Bad '--interval' value '{cmdl['interval']}': Must be positive")

    return cmdl

def _main() -> int:
    """Implement main logic."""

    args = _parse_arguments()

    if args.print_module_paths:
        _Common.print_module_paths()
        raise SystemExit(0)

    cmdl = _get_cmdline_args(args)

    fname = "/proc/interrupts"
    regex = re.compile(r" +")

    try:
        fobj = open(fname, "r", encoding="utf-8")
    except OSError as err:
        raise Error(f"Failed to open '{fname}': {err}") from err

    with fobj:
        while True:
            start = time.time()

            try:
                fobj.seek(0)
            except OSError as err:
                raise Error(f"Failed to seek in '{fname}': {err}") from err

            try:
                # It is OK to read the entire file in one go, it should not be huge.
                contents = fobj.read()
            except OSError as err:
                raise Error(f"Failed to read '{fname}': {err}") from err

            # The file contents is very sparse and on large servers takes a lot of space.
            # Shrink it by removing the extra white-spaces.
            new_contents = re.sub(regex, " ", contents).rstrip()

            _LOG.info("Timestamp: %s", time.time())
            _LOG.info(new_contents)

            elapsed = time.time() - start
            if elapsed < cmdl["interval"]:
                time.sleep(cmdl["interval"] - elapsed)

    return 0

def main() -> int:
    """Script entry point."""

    try:
        return _main()
    except KeyboardInterrupt:
        _LOG.info("\nInterrupted, exiting")
    except Error as err:
        _LOG.error_out(str(err))

    return -1
