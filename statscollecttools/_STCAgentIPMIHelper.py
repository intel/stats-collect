#!/usr/bin/python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
stc-agent-ipmi-helper - a wrapper over the 'ipmitool' utility for collecting the IPMI statistics.
This is an internal sub-tool of the 'stats-collect' tool, not intended to be used directly by end
users.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import sys
import time
import typing
import argparse
from pathlib import Path
from pepclibs.helperlibs import Logging, ArgParse, KernelModule, LocalProcessManager
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import ToolInfo, _Common

if typing.TYPE_CHECKING:
    from typing import Final, TypedDict

    class _CmdlineArgsTypedDict(TypedDict, total=False):
        """
        Typed dictionary representing the command-line arguments.

        Attributes:
            host: The IP address or host name of the BMC. Empty string means local IPMI.
            retries: How many times to retry the 'ipmitool' command on failure.
            count: How many IPMI data samples to collect. 0 means unlimited.
            interval: The interval between IPMI data samples in seconds.
            user: The IPMI user name.
            password_file: Path to the IPMI password file.
            interface: The IPMI interface to use.
        """

        host: str
        retries: int
        count: int
        interval: float
        user: str
        password_file: Path | None
        interface: str

_VERSION: Final[str] = ToolInfo.VERSION
_TOOLNAME: Final[str] = "stc-agent-ipmi-helper"

_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=_TOOLNAME)

# The Linux kernel modules required for local (in-band) IPMI access.
_IPMI_MODULES: Final[tuple[str, ...]] = ("ipmi_devintf", "ipmi_si")

def _build_arguments_parser() -> ArgParse.ArgsParser:
    """Build and return the arguments parser object."""

    text = sys.modules[__name__].__doc__
    parser = ArgParse.ArgsParser(description=text, prog=_TOOLNAME, ver=_VERSION)

    text = "The IP address or host name of the BMC (required for out-of-band IPMI collection)."
    parser.add_argument("--host", metavar="HOST", help=text)

    text = "How many times to retry the 'ipmitool' command on failure. Default is 2."
    parser.add_argument("--retries", help=text, type=int, default=2)

    text = "How many IPMI data samples to collect. Default is 0 (unlimited)."
    parser.add_argument("--count", help=text, type=int, default=0)

    text = "The interval between IPMI data samples in seconds. Default is 5."
    parser.add_argument("--interval", help=text, type=float, default=5)

    text = "IPMI user name for BMC authentication (passed to 'ipmitool -U'). Defaults to 'root'."
    parser.add_argument("-U", "--user", help=text)

    text = """Path to a file containing the IPMI password for BMC authentication (passed to
             'ipmitool -f')."""
    parser.add_argument("-f", "--password-file", help=text, type=Path)

    text = "The IPMI interface to use (passed to 'ipmitool -I'). Default is 'lanplus'."
    parser.add_argument("-I", "--interface", help=text, default="lanplus")

    # Hidden option: print paths to 'stc-agent-ipmi-helper' module dependencies and exit.
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
    cmdl["host"] = args.host or ""
    cmdl["retries"] = args.retries
    cmdl["count"] = args.count
    cmdl["interval"] = args.interval
    cmdl["user"] = args.user or ""
    cmdl["password_file"] = args.password_file
    cmdl["interface"] = args.interface

    if (cmdl["user"] or cmdl["password_file"]) and not cmdl["host"]:
        raise Error("Please, specify the host: '--user' and '--password-file' require '--host'")
    if cmdl["retries"] < 0:
        raise Error(f"Bad '--retries' value '{cmdl['retries']}': Must be non-negative")
    if cmdl["count"] < 0:
        raise Error(f"Bad '--count' value '{cmdl['count']}': Must be non-negative")
    if cmdl["interval"] <= 0:
        raise Error(f"Bad '--interval' value '{cmdl['interval']}': Must be positive")
    if cmdl["password_file"] and not cmdl["password_file"].is_file():
        raise Error(f"Password file does not exist: {cmdl['password_file']}")

    if not cmdl["user"] and cmdl["host"]:
        cmdl["user"] = "root"

    return cmdl

def _main() -> int:
    """Implement main logic."""

    args = _parse_arguments()

    if args.print_module_paths:
        _Common.print_module_paths()
        sys.exit(0)

    cmdl = _get_cmdline_args(args)

    cmd = "ipmitool"
    if cmdl["host"]:
        cmd += f" -I '{cmdl['interface']}' -H '{cmdl['host']}'"
    if cmdl["user"]:
        cmd += f" -U '{cmdl['user']}'"
    if cmdl["password_file"]:
        cmd += f" -f '{cmdl['password_file']}'"
    cmd += " sdr list full"

    with LocalProcessManager.LocalProcessManager() as pman:
        if not cmdl["host"]:
            # Make sure the IPMI Linux kernel modules are loaded.
            for modname in _IPMI_MODULES:
                with KernelModule.KernelModule(modname, pman=pman) as kmod:
                    kmod.load()

        interval = cmdl["interval"]
        retries = count = 0

        while True:
            start = time.time()
            try:
                output, _ = pman.run_verify(cmd)
            except Error:
                if retries >= cmdl["retries"]:
                    # Too many failures.
                    raise
                retries += 1
                continue
            else:
                _LOG.info("Timestamp | %s", time.time())
                _LOG.info(output)
                retries = 0
            finally:
                elapsed = time.time() - start
                if elapsed < interval:
                    time.sleep(interval - elapsed)

            if cmdl["count"]:
                count += 1
                if count >= cmdl["count"]:
                    break

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
