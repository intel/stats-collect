#!/usr/bin/python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
stc-agent - the statistics collection agent, a service for collecting statistics. This is an
internal sub-tool of the 'stats-collect' tool, not intended to be used directly by end users.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import os
import sys
import json
import time
import typing
import socket
import signal
import tempfile
import argparse
import contextlib
from pathlib import Path
from pepclibs.helperlibs import Logging, ArgParse, LocalProcessManager, Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import ProcHelpers
from statscollecttools import ToolInfo, _Common

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Final, IO, Iterable, Sequence, TypedDict, cast, NoReturn

    class _CmdlineArgsTypedDict(TypedDict, total=False):
        """
        Typed dictionary representing the command-line arguments.

        Attributes:
            unix: Path to the Unix socket to listen on. 'None' means a socket file with a random
                  name is created in the temporary directory.
            port: TCP port number to listen on. '-1' means use a Unix socket instead.
            sutname: The SUT name, used in socket file name and log messages.
        """

        unix: Path | None
        port: int
        sutname: str

    class _BasePropsTypedDict(TypedDict, total=False):
        """
        Base properties shared by the statistics collection agent and all statistics collectors.

        Attributes:
            outdir: The output directory.
        """

        outdir: Path

    class _BaseCollectorPropsTypedDict(_BasePropsTypedDict, total=False):
        """
        Base properties shared by all statistics collectors.

        Attributes:
            fallible: Whether the collector is allowed to fail without causing an error.
            logdir: The directory for collector standard error output.
            interval: The statistics collection interval.
        """

        fallible: bool
        logdir: Path
        interval: str

    class _TurbostatPropsTypedDict(_BaseCollectorPropsTypedDict, total=False):
        """
        Properties for the turbostat statistics collector.

        Attributes:
            toolpath: Path to the turbostat binary.
            opts: Extra command-line options to pass to turbostat.
        """

        toolpath: Path
        opts: str

    class _InterruptsPropsTypedDict(_BaseCollectorPropsTypedDict, total=False):
        """
        Properties for the interrupts statistics collector.

        Attributes:
            toolpath: Path to the interrupts helper binary.
        """

        toolpath: Path

    class _IPMIPropsTypedDict(_BaseCollectorPropsTypedDict, total=False):
        """
        Base properties for IPMI statistics collectors.

        Attributes:
            toolpath: Path to the IPMI helper binary.
            retries: Number of retries for IPMI commands.
            count: Number of IPMI readings per interval.
        """

        toolpath: Path
        retries: int
        count: int

    class _IPMIOOBPropsTypedDict(_IPMIPropsTypedDict, total=False):
        """
        Properties for the out-of-band IPMI statistics collector.

        Attributes:
            host: The remote host to collect IPMI data from.
            user: The IPMI user name.
            pwdfile: Path to the file containing the IPMI password.
            interface: The IPMI interface to use.
        """

        host: str
        user: str
        pwdfile: Path
        interface: str

    class _ACPowerPropsTypedDict(_BaseCollectorPropsTypedDict, total=False):
        """
        Properties for the AC power statistics collector.

        Attributes:
            toolpath: Path to the yokotool binary.
            devnode: The power meter device node.
            pmtype: The power meter type.
        """

        toolpath: Path
        devnode: str
        pmtype: str

    class _UninitializedTypedDict(TypedDict):
        """
        Sentinel values indicating uninitialized statistics collector properties.

        Attributes:
            str: Sentinel for an optional string property.
            int: Sentinel for an optional integer property.
            path: Sentinel for an optional path property.
            required_str: Sentinel for a required string property.
            required_int: Sentinel for a required integer property.
            required_path: Sentinel for a required path property.
        """

        str: str
        int: int
        path: Path
        required_str: str
        required_int: int
        required_path: Path

_VERSION: Final[str] = ToolInfo.VERSION
_TOOLNAME: Final[str] = "stc-agent"

# Sentinel values for uninitialized statistics collector properties.
_UNINITIALIZED: Final[_UninitializedTypedDict] = {
    "str": "<not configured>",
    "int": -1000000000000,
    "path": Path("<not configured>"),
    "required_str": "<must be configured>",
    "required_int": -9999999999999,
    "required_path": Path("<must be configured>"),
}

# The messages delimiter prefix. Every time it appears following a newline, it marks the end of
# the message.
_DELIMITER: Final[str] = "--"

# Names of the supported statistics.
_SUPPORTED_STATS: Final[tuple[str, ...]] = ("turbostat", "interrupts", "ipmi-oob", "ipmi-inband",
                                            "acpower")

# Configure the root 'main' logger, not a child logger, so that debug messages from pepclibs
# ('main.pepc.*') are also captured.
_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=_TOOLNAME)

class _ClientDisconnected(Exception):
    """Raise when a client disconnects."""

class _ExitCommand(Exception):
    """Raise to signal that the agent should exit."""

class _BaseCollector:
    """
    The base class for statistics collectors.

    Public methods overview:

    - 'configure()': configure the collector; must be called after every property change.
    - 'kill_stale()': kill stale collector processes that might still be running.
    - 'start()': start collecting the statistics.
    - 'end()': signal the collector process to stop.
    - 'save()': wait for the collector to exit and synchronize the output file.
    - 'validate()': validate the collected data to make sure it is sane.

    The expected usage sequence after initialization is: 'configure()', 'kill_stale()', 'start()',
    'end()', 'save()', 'validate()'. The sequence can be repeated many times.
    """

    def __init__(self, name: str):
        """
        Initialize a class instance.

        Args:
            name: The name of the statistics to collect.
        """

        self.name = name

        # The collector properties that can be changed directly, but any change requires the
        # 'configure()' method to be executed for the changes to take the effect.
        self.props: _BaseCollectorPropsTypedDict = {}
        # Whether this collector is allowed to fail without causing an error.
        self.props["fallible"] = False
        # The output directory where the statistics will be stored.
        self.props["outdir"] = _UNINITIALIZED["required_path"]
        # The log directory where collectors may put their standard error output.
        self.props["logdir"] = _UNINITIALIZED["required_path"]
        # The statistics collection interval.
        self.props["interval"] = _UNINITIALIZED["required_str"]

        # The local process manager object.
        self._pman: LocalProcessManager.LocalProcessManager | None
        self._pman = LocalProcessManager.LocalProcessManager()

        #
        # These attributes are internal to this base class.
        #

        # The output file where subprocess redirects its stdout and stderr streams. The file is
        # opened with no buffering ('buffering=0') as a paranoid measure to minimize the
        # probability of data loss. And to disable buffering, the file must be opened in binary
        # mode.
        self._fobj: IO[bytes] | None = None
        # The statistics collector process.
        self._proc: LocalProcessManager.LocalProcess | None = None
        # The full path to the output file.
        self._outpath: Path | None = None
        # Whether 'configure()' has been called and the collector is ready to use.
        self._configured: bool = False

        #
        # These attributes can/should be set by child classes.
        #
        self._outfile: str = f"{name}.raw.txt"
        self._command: str = ""
        # Optional byte patterns the base class 'validate()' checks against the start and end of
        # the output file. Set by subclasses, empty bytes means no validation should be performed.
        self._valid_start: bytes = b""
        self._valid_end: bytes = b""
        self._signal: signal.Signals = signal.SIGTERM
        self._stale_search: str = ""

    def __del__(self):
        """Class destructor."""

        if getattr(self, "_pman", None):
            if typing.TYPE_CHECKING:
                assert self._pman is not None
            self._pman.close()
            self._pman = None
        if getattr(self, "_fobj", None):
            if typing.TYPE_CHECKING:
                assert self._fobj is not None
            self._fobj.close()
            self._fobj = None

    def _error(self, msgformat, *args) -> NoReturn:
        """The collector error handler."""

        if args:
            msg = msgformat % args
        else:
            msg = str(msgformat)

        raise Error(f"The '{self.name}' statistics collector failed:\n{msg}")

    def _sync(self):
        """Synchronize all the collector files."""

        if self._fobj is None:
            self._error("BUG: The output file object is not initialized")

        try:
            self._fobj.flush()
            os.fsync(self._fobj.fileno())
        except OSError as err:
            self._error("Cannot synchronize '%s':\n%s", self._fobj.name, err)

    def _handle_dirs(self):
        """Make sure the output and log directories exist."""

        for key in ("outdir", "logdir"):
            path = self.props[key]
            if not path.is_absolute():
                self._error("Path '%s' (%s) is not absolute", path, key)
            if path.exists():
                if not path.is_dir():
                    self._error("Path '%s' (%s) already exists and it is not a directory",
                                path, key)
            else:
                _LOG.debug("'%s': Creating directory '%s' (%s)", self.name, path, key)
                try:
                    path.mkdir()
                except OSError as err:
                    self._error("Cannot create directory '%s' (%s):\n%s", path, key, err)

    def configure(self):
        """Configure the statistics collector."""

        # Validate that all of the mandatory properties have been set.
        for prop, val in self.props.items():
            if any(val is s for s in (_UNINITIALIZED["required_str"],
                                      _UNINITIALIZED["required_int"],
                                      _UNINITIALIZED["required_path"])):
                self._error("Please configure '%s' first", prop)

        self._handle_dirs()

        self._outpath = self.props["outdir"] / self._outfile

        if self._fobj is not None:
            self._fobj.close()
            self._fobj = None

        try:
            # pylint: disable=consider-using-with
            self._fobj = open(self._outpath, "wb+", buffering=0)
        except OSError as err:
            self._error("Failed to open '%s':\n%s", self._outpath, err)

        # Ensure the newly created output file is flushed to disk.
        self._sync()
        self._configured = True

    def kill_stale(self):
        """Kill stale collector process that might still be running."""

        if not self._stale_search:
            return

        ProcHelpers.kill_processes(self._stale_search, kill_children=True, log=False)

    def start(self):
        """Start collecting the statistics."""

        if not self._configured:
            self._error("The collector was not configured")

        if self._proc is not None:
            self._error("BUG: The collector is already running")

        if self._pman is None:
            self._error("BUG: The process manager is not initialized")

        self._proc = self._pman.run_async(self._command, stderr=self._fobj, stdout=self._fobj,
                                          newgrp=True)

    def end(self):
        """Signal the collector process to stop."""

        if self._proc is None:
            self._error("BUG: The collector is not running")

        exitcode = self._proc.poll()
        if exitcode is not None:
            self._error("The following command exited prematurely with exit code %d:\n%s",
                        exitcode, self._command)

        try:
            pgid = Trivial.get_pgid(self._proc.pid)
        except Error as err:
            self._error(err)

        # Signal the entire statistics collector process group.
        _LOG.debug("'%s': Sending signal %s to PGID %d (group of PID %d)",
                   self.name, self._signal, pgid, self._proc.pid)
        try:
            os.killpg(pgid, self._signal)
        except OSError as err:
            self._error("Failed to kill the process group of PID %d, PGID %d:\n%s",
                        self._proc.pid, pgid, err)

    def save(self):
        """Wait for the collector process to exit and save the collected statistics."""

        if self._proc is None:
            self._error("BUG: The collector is not running")

        # Make sure the process has exited. The reason it is done in 'save()' is a hacky
        # optimization: all processes are signaled first without waiting (in 'end()'), and only once
        # all are signaled does checking begin. This approach helps having the collectors stop
        # "more simultaneously".
        try:
            _, _, exitcode = self._proc.wait(timeout=10, capture_output=False)
            if exitcode is None:
                self._error("PID %d refused to exit", self._proc.pid)
        finally:
            self._proc.close()
            self._proc = None

        self._sync()

    def validate(self):
        """Check that the collected statistics are valid."""

        if self._fobj is None:
            self._error("BUG: The output file object is not initialized")

        if self._valid_start:
            self._fobj.seek(0)
            buf = self._fobj.read(len(self._valid_start))
            if buf != self._valid_start:
                self._error("Failed to validate the collected statistics:\nThe output file '%s' "
                            "does not start with the required pattern\nExpected '%s', got '%s'",
                            self._outpath, self._valid_start.decode("utf-8"), buf.decode("utf-8"))

        if self._valid_end:
            length = len(self._valid_end)
            self._fobj.seek(-length, 2)
            buf = self._fobj.read(len(self._valid_end))
            if buf != self._valid_end:
                self._error("Failed to validate the collected statistics:\nThe output file '%s' "
                            "does not end with the required pattern\nExpected '%s', got '%s'",
                            self._outpath, self._valid_end.decode("utf-8"), buf.decode("utf-8"))

class _TurbostatCollector(_BaseCollector):
    """The turbostat statistics collector."""

    def __init__(self):
        """Initialize a class instance."""

        super().__init__("turbostat")

        if typing.TYPE_CHECKING:
            self.props = cast(_TurbostatPropsTypedDict, self.props)

        self.props["toolpath"] = Path("turbostat")
        self.props["opts"] = _UNINITIALIZED["str"]

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        if typing.TYPE_CHECKING:
            self.props = cast(_TurbostatPropsTypedDict, self.props)

        self._command = f"{self.props['toolpath']} --enable Time_Of_Day_Seconds " \
                        f"--interval '{self.props['interval']}'"

        if self.props["opts"] is not _UNINITIALIZED["str"]:
            self._command += " " + self.props["opts"]

        toolname = os.path.basename(self.props["toolpath"])
        self._stale_search = f"{toolname} --enable Time_Of_Day_Seconds --interval "

        if self._pman is None:
            self._error("BUG: The process manager is not initialized")

        try:
            self._pman.run_verify("modprobe intel_uncore_frequency")
        except Error as err:
            _LOG.debug("Unable to load 'intel_uncore_frequency' module which is required "
                       "to collect turbostat uncore frequency measurements: %s", str(err))

class _InterruptsCollector(_BaseCollector):
    """The interrupts statistics collector - periodically snapshot '/proc/interrupts'."""

    def __init__(self):
        """Initialize a class instance."""

        super().__init__("interrupts")

        if typing.TYPE_CHECKING:
            self.props = cast(_InterruptsPropsTypedDict, self.props)

        self.props["toolpath"] = Path("stc-agent-proc-interrupts-helper")
        self._signal = signal.SIGINT

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        if typing.TYPE_CHECKING:
            self.props = cast(_InterruptsPropsTypedDict, self.props)

        self._command = f"{self.props['toolpath']} --interval {self.props['interval']}"

class _IPMICollector(_BaseCollector):
    """Base class for IPMI statistics collectors."""

    def __init__(self, name):
        """Initialize a class instance."""

        super().__init__(name)

        if typing.TYPE_CHECKING:
            self.props = cast(_IPMIPropsTypedDict, self.props)

        self.props["toolpath"] = Path("stc-agent-ipmi-helper")
        self.props["retries"] = _UNINITIALIZED["int"]
        self.props["count"] = _UNINITIALIZED["int"]
        self._valid_start = b"timestamp | "

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        if typing.TYPE_CHECKING:
            self.props = cast(_IPMIPropsTypedDict, self.props)

        self._command = f"{self.props['toolpath']} --interval '{self.props['interval']}'"
        if self.props["retries"] is not _UNINITIALIZED["int"]:
            self._command += f" --retries '{self.props['retries']}'"
        if self.props["count"] is not _UNINITIALIZED["int"]:
            self._command += f" --count '{self.props['count']}'"

        self._stale_search = f"{os.path.basename(self.props['toolpath'])} --interval "

class _IPMIInBandCollector(_IPMICollector):
    """The in-band IPMI statistics collector."""

    def __init__(self):
        """Initialize a class instance."""

        super().__init__("ipmi-inband")

class _IPMIOOBCollector(_IPMICollector):
    """The out-of-band IPMI statistics collector."""

    def __init__(self):
        """Initialize a class instance."""

        super().__init__("ipmi-oob")

        if typing.TYPE_CHECKING:
            self.props = cast(_IPMIOOBPropsTypedDict, self.props)

        self.props["host"] = _UNINITIALIZED["required_str"]
        self.props["user"] = _UNINITIALIZED["str"]
        self.props["pwdfile"] = _UNINITIALIZED["path"]
        self.props["interface"] = _UNINITIALIZED["str"]

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        if typing.TYPE_CHECKING:
            self.props = cast(_IPMIOOBPropsTypedDict, self.props)

        hostopt = f" --host '{self.props['host']}'"
        self._command += hostopt
        if self.props["user"] is not _UNINITIALIZED["str"]:
            self._command += f" --user '{self.props['user']}'"
        if self.props["pwdfile"] is not _UNINITIALIZED["path"]:
            self._command += f" --password-file '{self.props['pwdfile']}'"
        if self.props["interface"] is not _UNINITIALIZED["str"]:
            self._command += f" -I '{self.props['interface']}'"

        self._stale_search += f".*{hostopt}"

class _ACPowerCollector(_BaseCollector):
    """The ACPower statistics collector."""

    def __init__(self):
        """Initialize a class instance."""

        super().__init__("acpower")

        if typing.TYPE_CHECKING:
            self.props = cast(_ACPowerPropsTypedDict, self.props)

        self.props["toolpath"] = Path("yokotool")
        self.props["devnode"] = _UNINITIALIZED["required_str"]
        self.props["pmtype"] = _UNINITIALIZED["str"]
        self._signal: signal.Signals = signal.SIGINT

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        if typing.TYPE_CHECKING:
            self.props = cast(_ACPowerPropsTypedDict, self.props)

        devnode = self.props['devnode']
        cmd = f"{self.props['toolpath']} {devnode}"
        if self.props["pmtype"] is not _UNINITIALIZED["str"]:
            cmd += f" --pmtype {self.props['pmtype']}"

        self._stale_search = f"{os.path.basename(self.props['toolpath'])} {devnode}"

        if self._pman is None:
            self._error("BUG: The process manager is not initialized")

        # The power meter is assumed to be initialized and configured outside of 'stc-agent'.
        # Only the interval is set here.
        self._pman.run_verify(f"{cmd} set interval {self.props['interval']}")

        items = "T,P,I,V,S,Q,Phi,Fv,Vrange,Irange"
        self._command = f"{cmd} read {items}"

class _STCAgent:
    """
    The statistics collection agent class implementing all statistics collection functionality.

    Public methods overview:

    - 'create()': create the statistics collector objects.
    - 'set_property()': set a property of the statistics collection agent.
    - 'set_collector_property()': set a property of one or multiple statistic collectors.
    - 'configure()': configure the collectors.
    - 'add_label()': add a label.
    - 'start()': start collecting the statistics.
    - 'stop()': stop collecting the statistics.
    """

    def __init__(self):
        """Initialize a class instance."""

        self._started: bool = False
        self._collectors: dict[str, _BaseCollector] = {}
        self.failed_collectors: set[str] = set()
        self.name: str = "STCAgent"

        # The labels file object.
        self._lfobj: IO[str] | None = None

        # Statistics collection agent properties.
        self.props: _BasePropsTypedDict = {}
        # The output directory where data like labels will be stored.
        self.props["outdir"] = _UNINITIALIZED["path"]

    def _execute_collectors_methods(self, methods: Iterable[str]):
        """
        Execute a sequence of methods on all statistics collectors.

        Args:
            methods: Names of the collector methods to call, in order.

        Notes:
            - Collectors that have previously failed are skipped.
            - If a method raises an 'Error' and the collector is fallible, the error is logged and
              execution continues. Otherwise it is re-raised.
        """

        for method in methods:
            for collector in self._collectors.values():
                if collector.name in self.failed_collectors:
                    _LOG.debug("Skip running the '%s' method of failed '%s' collector",
                               method, collector.name)
                    continue

                _LOG.debug("Running the '%s' method of the %s collector", method, collector.name)

                try:
                    getattr(collector, method)()
                except Error as err:
                    self.failed_collectors.add(collector.name)
                    errmsg = f"The '{method}' method of the {collector.name} collector failed:\n" \
                             f"{err.indent(2)}"
                    if collector.props["fallible"]:
                        _LOG.debug(errmsg)
                    else:
                        raise type(err)(errmsg) from err
                else:
                    _LOG.debug("'%s' method of the %s collector succeeded", method, collector.name)

    def create(self, stnames: Sequence[str]):
        """
        Create statistics collector objects for the given statistics names.

        Args:
            stnames: Names of the statistics to collect. Must be a non-empty list of names from
                     '_SUPPORTED_STATS'.
        """

        if not stnames:
            raise Error("Please, specify at least one statistic name")
        if self._started:
            raise Error("Statistics collection has been started, cannot create collectors")

        _LOG.debug("Creating the following collectors: %s", ",".join(stnames))

        # Delete collectors one by one to explicitly trigger their '__del__()' methods, which close
        # open file objects and process managers.
        for name in list(self._collectors):
            del self._collectors[name]
        self.failed_collectors = set()

        _collector_map: dict[str, Callable[[], _BaseCollector]] = {
            "turbostat":   _TurbostatCollector,
            "interrupts":  _InterruptsCollector,
            "ipmi-oob":    _IPMIOOBCollector,
            "ipmi-inband": _IPMIInBandCollector,
            "acpower":     _ACPowerCollector,
        }

        for name in stnames:
            if name not in _collector_map:
                supported = ", ".join(_SUPPORTED_STATS)
                raise Error(f"Unknown statistics name '{name}', use one of:\n{supported}")
            try:
                _LOG.debug("Creating the %s collector", name)
                self._collectors[name] = _collector_map[name]()
            except Error as err:
                raise type(err)(f"Failed to create the {name} collector:\n"
                                f"{err.indent(2)}") from err

        _LOG.debug("Created the collectors")

    @staticmethod
    def _set_obj_property(obj: _BaseCollector | _STCAgent, name: str, value: str):
        """
        Set property 'name' of object 'obj' to 'value'.

        Args:
            obj: The object whose property to set.
            name: The property name.
            value: The new property value as a string.

        Notes:
            - Property values arrive as raw strings from external clients over the network socket,
              but properties are typed ('bool', 'int', 'str', 'Path'). 'value' is converted to the
              correct type by inspecting the existing property value.
        """

        if not hasattr(obj, "props"):
            raise Error(f"Object '{obj}' has no 'props' attribute")

        if typing.TYPE_CHECKING:
            props = cast(dict[str, Any], obj.props)
        else:
            props = obj.props

        if name not in props:
            raise Error(f"Object '{obj}' has no property '{name}'")

        # Since 'bool("False")' is 'True', boolean props require a special case.
        if isinstance(props[name], bool):
            if value not in ("True", "False"):
                raise Error(f"Type conversion error for property '{name}' of '{obj.name}':\n"
                            f"String '{value}' cannot be converted to 'bool'")
            props[name] = value == "True"
        else:
            try:
                props[name] = type(props[name])(value)
            except (TypeError, ValueError) as err:
                raise Error(f"Type conversion error for property '{name}' of '{obj.name}':\n"
                            f"String '{value}' cannot be converted to "
                            f"'{type(props[name]).__name__}'") from err

    def set_collector_property(self, args: str):
        """
        Set a property of a statistics collector.

        Args:
            args: A space-separated string in the format '<stat_name> <property_name>
                  <property_value>'.

        Notes:
            - 'args' arrives as a raw string from an external client over the network socket and is
              validated before use.
        """

        if not self._collectors:
            raise Error("No statistics collectors selected")

        if self._started:
            raise Error("Statistics collection has been started, cannot change properties")

        # Split into at most 3 parts. Fewer means the argument is malformed.
        arg_list = args.split(maxsplit=2)
        if len(arg_list) < 3:
            raise Error(f"Incorrect argument '{args}'\nThe argument must be in the following "
                        f"format:\n<stat_name> <property_name> <property_value>")

        if arg_list[0] not in self._collectors:
            active = ", ".join(self._collectors)
            raise Error(f"Collector '{arg_list[0]}' is not active, active collectors are:\n"
                        f"{active}")

        collector = self._collectors[arg_list[0]]

        if collector.name in self.failed_collectors:
            # Ignore failed collectors.
            return

        if arg_list[1] not in collector.props:
            raise Error(f"The '{collector.name}' collector does not support the '{arg_list[1]}' "
                        f"property")

        self._set_obj_property(collector, arg_list[1], arg_list[2])

        _LOG.debug("Set collector '%s' property '%s' to value '%s'",
                   collector.name, arg_list[1], arg_list[2])

    @staticmethod
    def _set_outdir(path: Path):
        """
        Validate and create the 'stc-agent' output directory.

        Args:
            path: Absolute path to the output directory to create.
        """

        if not path.is_absolute():
            raise Error(f"The 'stc-agent' output directory path '{path}' is not absolute")

        if path.exists():
            if not path.is_dir():
                raise Error(f"The 'stc-agent' output directory path '{path}' already exists "
                            f"and is not a directory")
        else:
            _LOG.debug("Creating 'stc-agent' output directory '%s'", path)
            try:
                path.mkdir()
            except OSError as err:
                raise Error(f"Cannot create 'stc-agent' output directory '{path}':\n{err}") from err

    def set_property(self, args: str):
        """
        Set a property of the statistics collection agent.

        Args:
            args: A space-separated string in the format '<property_name> <property_value>'.

        Notes:
            - 'args' arrives as a raw string from an external client over the network socket and is
              validated before use.
        """

        if self._started:
            raise Error("Statistics collection has been started, cannot change properties")

        arg_list = args.split(maxsplit=1)
        if len(arg_list) < 2:
            raise Error(f"Incorrect 'stc-agent' property argument '{args}'\nIt must be in the "
                        f"following format:\n<property_name> <property_value>")

        pname, pval = arg_list
        if pname not in self.props:
            supported = ", ".join(self.props)
            raise Error(f"Unsupported 'stc-agent' property '{pname}', supported properties are: "
                        f"{supported}")

        self._set_obj_property(self, pname, pval)
        if pname == "outdir":
            self._set_outdir(Path(pval))

        _LOG.debug("Set 'stc-agent' property '%s' to value '%s'", pname, pval)

    def configure(self):
        """Configure the statistics collectors."""

        if not self._collectors:
            raise Error("No statistics collectors selected")

        if self._started:
            raise Error("Statistics collection has been started, cannot configure")

        self._execute_collectors_methods(("configure", "kill_stale"))
        _LOG.debug("Configured the collectors")

    def add_label(self, args: str):
        """
        Add a label to the labels file.

        Args:
            args: A JSON-serialized dictionary. Must include the 'name' key for the label name,
                  and may include any number of additional keys.

        Notes:
            - Labels are a mechanism for synchronizing workload stages with collected statistics.
              Each label is a JSON object written as a single line to 'labels.txt', with at minimum
              a 'name' and a 'ts' (Unix timestamp) key. Report tools match labels to statistics
              data points by timestamp, so a label can mark workload stages such as warmup or the
              main measurement phase.
            - 'args' arrives as a raw string from an external client over the network socket and is
              validated before use.
            - The 'ts' key is reserved and must not be present in 'args'; it is added automatically
              with the current timestamp.
        """

        if not self._collectors:
            raise Error("No statistics collectors selected")

        if self.props["outdir"] is _UNINITIALIZED["path"]:
            raise Error("Cannot add 'stc-agent' label: The output directory was not set")

        _LOG.debug("Adding label '%s'", args)

        try:
            label = json.loads(args)
        except ValueError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to parse label JSON:\n{errmsg}") from err

        # Validate that the 'name' key is present and contains only alphanumeric characters.
        name: str = label.get("name")
        if not name:
            raise Error(f"No label name provided in '{args}'")
        if not name.isalnum():
            raise Error(f"Bad label name '{name}': Must be alphanumeric")

        # The 'ts' key is reserved for the timestamp added below.
        if "ts" in label:
            raise Error(f"Found reserved key 'ts' in label '{args}'")

        if not self._lfobj:
            path = self.props["outdir"] / "labels.txt"
            try:
                # pylint: disable=consider-using-with
                self._lfobj = open(path, "w", encoding="utf-8")
            except OSError as err:
                errmsg = Error(str(err)).indent(2)
                raise Error(f"Failed to create file '{path}':\n{errmsg}") from err

            # The first line provides the list of collectors the labels file covers.
            self._lfobj.write(f"# {','.join(self._collectors)}\n")

        label["ts"] = time.time()

        try:
            label_str = json.dumps(label)
        except ValueError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to serialize label JSON:\n{errmsg}") from err

        self._lfobj.write(f"{label_str}\n")

    def start(self):
        """Start collecting the statistics."""

        if not self._collectors:
            raise Error("No statistics collectors selected")

        if self._started:
            raise Error("Statistics collection has already been started")

        self._execute_collectors_methods(("start",))
        self._started = True

        _LOG.debug("Started the collectors")

    def stop(self):
        """Stop collecting the statistics."""

        if not self._started:
            raise Error("Statistics collection has not been started")

        try:
            self._execute_collectors_methods(("end", "save", "validate"))
        finally:
            self._started = False

            if self._lfobj:
                try:
                    self._lfobj.flush()
                    os.fsync(self._lfobj.fileno())
                except OSError as err:
                    errmsg = Error(str(err)).indent(2)
                    raise Error(f"Failed to synchronize 'stc-agent' labels file:\n"
                                f"{errmsg}") from err
                finally:
                    self._lfobj.close()
                    self._lfobj = None

        _LOG.debug("Stopped the collectors")

class _Client(ClassHelpers.SimpleCloseContext):
    """The statistics collection agent network client."""

    def __init__(self, sock: socket.socket, clientid: str):
        """
        Initialize the client.

        Args:
            sock: The client connection socket.
            clientid: A printable client ID string used in log messages.
        """

        self._sock: socket.socket = sock
        self.clientid: str = clientid

    def close(self):
        """Close the client connection."""

        if getattr(self, "_sock", None):
            with contextlib.suppress(socket.error):
                self._sock.shutdown(socket.SHUT_RDWR)
                self._sock.close()

    def respond(self, msg: str):
        """
        Respond to the client by sending it a message.

        Args:
            msg: The message to send.
        """

        _LOG.debug("Sending the following response to client '%s': %s", self.clientid, msg)

        buf: bytes = (msg + _DELIMITER + "\n").encode("utf-8")
        total: int = 0

        while total < len(buf):
            sent = self._sock.send(buf[total:])
            if sent == 0:
                raise _ClientDisconnected(f"Client '{self.clientid}' disconnected, cannot send it "
                                          f"the following message: {msg}")
            total += sent

    def get_command(self) -> str:
        """
        Receive and return the next client command.

        Returns:
            The command string received from the client.
        """

        _LOG.debug("Waiting for a command from client '%s'", self.clientid)

        bufs: list[bytes] = []
        cmd: bytes = bytes()
        msg: bytes = bytes()

        while not cmd:
            buf = self._sock.recv(1)
            if not buf:
                raise _ClientDisconnected(f"Client '{self.clientid}' disconnected, failed to "
                                          f"receive a command from it")
            bufs.append(buf)
            if buf != "\n".encode("utf-8"):
                continue

            msg += b"".join(bufs)
            bufs = []
            # Handle both Linux and Windows newlines.
            for delim in (_DELIMITER + "\n", _DELIMITER + "\r\n"):
                delim_bytes = delim.encode("utf-8")
                if msg.endswith(delim_bytes):
                    cmd = msg[:-len(delim_bytes)]
                    break

        try:
            cmd_str = cmd.decode("utf-8").strip()
        except UnicodeError as err:
            self.respond("Failed to decode the command from UTF-8")
            errmsg = Error(str(err)).indent(2)
            raise _ClientDisconnected(f"Failed to decode the command from UTF-8 from client "
                                      f"'{self.clientid}':\n{errmsg}") from err

        _LOG.debug("Received command from client '%s':\n%s", self.clientid, cmd_str)
        return cmd_str

class _Server(ClassHelpers.SimpleCloseContext):
    """
    Statistics collection agent network server.

    Manage a server-side socket (Unix or TCP) that listens for and accepts one client connection at
    a time. Create the server with either a Unix socket path or a TCP port number. If neither is
    provided, use a Unix socket with a random name created in the temporary directory.
    """

    def __init__(self, unix: Path | None = None, port: int = -1, sutname: str = ""):
        """
        Initialize the server.

        Args:
            unix: Path to the Unix socket file to listen on. 'None' means a socket file with a
                  random name is created in the temporary directory.
            port: TCP port number to listen on. '-1' means use a Unix socket instead. '0' lets the
                  OS pick an available port.
            sutname: Optional SUT name, used only as a prefix in the Unix socket file name
                     created in the temporary directory.
        """

        self._port: int = port
        self._unix: Path | None = unix
        self._sutname: str = sutname
        self._is_unix: bool = port == -1
        self._sock: socket.socket | None = None
        # Whether to remove the Unix socket file on 'close()'. 'True' means the path was
        # created internally. User-provided paths are left alone.
        self._remove_unix: bool = False

        if self._port != -1 and self._unix is not None:
            raise Error("Specify either TCP port or Unix socket path, not both of them")

        if self._is_unix:
            self._unix_socket_prepare()

    def close(self):
        """Close the server."""

        if getattr(self, "_sock", None):
            if typing.TYPE_CHECKING:
                assert self._sock is not None
            with contextlib.suppress(socket.error):
                self._sock.shutdown(socket.SHUT_RDWR)
                self._sock.close()

        if getattr(self, "_remove_unix", False) and getattr(self, "_unix", None):
            if typing.TYPE_CHECKING:
                assert self._unix is not None
            with contextlib.suppress(OSError):
                self._unix.unlink()

    def _unix_socket_prepare(self):
        """Prepare the Unix socket path before binding."""

        if self._unix is None:
            # Select a random name for the Unix socket file.
            try:
                pfx = f"{_TOOLNAME}-"
                if self._sutname:
                    pfx = f"{pfx}{self._sutname}-"
                with tempfile.NamedTemporaryFile("wb+", prefix=pfx, delete=True) as fobj:
                    self._unix = Path(fobj.name)
            except OSError as err:
                errmsg = Error(str(err)).indent(2)
                raise Error(f"Failed to create a temporary file:\n{errmsg}") from err
            self._remove_unix = True
        elif self._unix.exists():
            try:
                with contextlib.suppress(FileNotFoundError):
                    self._unix.unlink()
            except OSError as err:
                errmsg = Error(str(err)).indent(2)
                raise Error(f"Failed to remove '{self._unix}':\n{errmsg}") from err

    def start_listening(self):
        """Bind the socket and start listening for incoming client connections."""

        if self._is_unix:
            try:
                self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self._sock.bind(str(self._unix))
                self._sock.listen(1)
            except socket.error as err:
                errmsg = Error(str(err)).indent(2)
                raise Error(f"Failed to start listening on Unix socket '{self._unix}': "
                            f"{errmsg}") from err

            msg = f"Listening on Unix socket {self._unix}"
        else:
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._sock.bind(("", self._port))
                _, self._port = self._sock.getsockname()
                self._sock.listen(1)
            except socket.error as err:
                errmsg = Error(str(err)).indent(2)
                raise Error(f"Failed to start listening on TCP port {self._port}:\n"
                            f"{errmsg}") from err

            msg = f"Listening on TCP port {self._port}"

        _LOG.debug(msg)
        _LOG.info(msg)

    def wait_for_client(self):
        """
        Accept the next incoming client connection.

        Returns:
            A '_Client' instance wrapping the accepted socket connection.
        """

        if typing.TYPE_CHECKING:
            assert self._sock is not None

        try:
            client_sock, _ = self._sock.accept()
        except (OSError, socket.error) as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Error while accepting a client connection:\n{errmsg}") from err

        if self._is_unix:
            clientid = "local_client"
        else:
            client_host, client_port = client_sock.getpeername()
            clientid = f"{client_host}:{client_port}"
        _LOG.debug("Client connected: %s", clientid)

        return _Client(client_sock, clientid)

def _handle_command(cmd: str, stc_agent: _STCAgent) -> str:
    """
    Dispatch a single client command to the appropriate '_STCAgent' method.

    Args:
        cmd: The raw command string received from the client. May include a space-separated
             argument after the command name.
        stc_agent: The statistics collection agent to dispatch the command to.

    Returns:
        The response string to send back to the client. 'OK' on success, 'OK <data>' when the
        command returns data, or an error description otherwise.
    """

    cmd, args = cmd.partition(" ")[::2]
    cmd = cmd.strip()
    args = args.strip()

    response = "OK"

    try:
        if cmd == "set-stats":
            # Create the statistics collectors without initializing them.
            stc_agent.create([stname.strip() for stname in args.split(",")])
        elif cmd == "set-agent-property":
            # Set a property of 'stc-agent'.
            stc_agent.set_property(args)
        elif cmd == "set-collector-property":
            # Set a property of a statistics collector.
            stc_agent.set_collector_property(args)
        elif cmd == "configure":
            # Once all the properties had been set, configure the collectors.
            stc_agent.configure()
        elif cmd == "start":
            # Start collecting the statistics.
            stc_agent.start()
        elif cmd == "stop":
            # Stop collecting the statistics.
            stc_agent.stop()
        elif cmd == "add_label":
            stc_agent.add_label(args)
        elif cmd == "get-failed-collectors":
            # Get the list of failed collectors.
            response += f" {','.join(stc_agent.failed_collectors)}"
        elif cmd == "exit":
            pass
        else:
            response = f"Bad command: {cmd}"
    except Error as err:
        response = f"Error: {err}"
    except Exception as err: # pylint: disable=broad-except
        response = f"Unknown exception of type '{type(err).__name__}':\n{err}"

    return response

def _handle_client(client: _Client, stc_agent: _STCAgent):
    """
    Process all commands from a connected client until it sends 'exit'.

    Args:
        client: The connected client to read commands from and write responses to.
        stc_agent: The statistics collection agent to dispatch commands to.

    Raises:
        _ExitCommand: The client sent the 'exit' command.
    """

    cmd = None
    while cmd != "exit":
        cmd = client.get_command()
        response = _handle_command(cmd, stc_agent)
        client.respond(response)

    raise _ExitCommand()

def _build_arguments_parser() -> ArgParse.ArgsParser:
    """Build and return the arguments parser object."""

    text = sys.modules[__name__].__doc__
    parser = ArgParse.ArgsParser(description=text, prog=_TOOLNAME, ver=_VERSION)

    text = f"""The local unix socket path to wait for incoming clients connections on. By default,
               '{_TOOLNAME}' creates a socket node with a random name in the temporary directory and
               prints its path to the standard output. The socket file name, however, will include
               SUT name, if it was specified with '--sut-name'. E.g., '--sut-name=myhost' would
               result in socket file name like 'stc-agent-myhost-abracadabra', where 'abracadabra'
               is the random part of the name."""
    parser.add_argument("-u", "--unix", default="", help=text)

    text = f"""TCP port number to listen for incoming client connections on. If port value is 0,
               '{_TOOLNAME}' allocates an available port and prints its value to the standard
               output. WARNING! Using a TCP port may be dangerous because there is no
               authentication. It is more secure to use a unix socket and let the remote client
               authenticate and connect via a secure protocol like SSH."""
    parser.add_argument("-p", "--port", type=int, default=-1, help=text)

    text = """System Under Test (SUT) name. This option affects only the messages and the
              automatically created Unix socket file name."""
    parser.add_argument("--sut-name", dest="sutname", default="", help=text)

    # Hidden option: print paths to 'stc-agent' module dependencies and exit.
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
    cmdl["unix"] = Path(args.unix) if args.unix else None
    cmdl["port"] = args.port
    cmdl["sutname"] = args.sutname

    if cmdl["port"] != -1 and cmdl["unix"] is not None:
        raise Error("'--port' and '--unix' options are mutually exclusive")

    return cmdl

def _sighandler(sig, _):
    """
    In case 'stc-agent' is started in a PID namespace and it is PID 1, the default signal handlers
    are not set up, and this handler is installed to exit on 'SIGTERM' and 'SIGINT' signals.
    """

    _LOG.debug("Received signal '%d', exiting", sig)
    raise SystemExit(sig)

def _main() -> int:
    """Implement main logic."""

    if Trivial.get_pid() == 1:
        # When 'stc-agent' runs as PID 1 inside a new PID namespace (e.g., launched via
        # 'unshare --pid'), the kernel does not set up default signal handlers for it. Install
        # explicit handlers so that 'SIGINT' and 'SIGTERM' cause a clean exit.
        signal.signal(signal.SIGINT, _sighandler)
        signal.signal(signal.SIGTERM, _sighandler)

    args = _parse_arguments()

    if args.print_module_paths:
        _Common.print_module_paths()
        raise SystemExit(0)

    cmdl = _get_cmdline_args(args)

    stc_agent = _STCAgent()

    with _Server(unix=cmdl["unix"], port=cmdl["port"], sutname=cmdl["sutname"]) as server:
        server.start_listening()
        _LOG.debug("Commands delimiter is '\\n%s'", _DELIMITER)

        while True:
            with server.wait_for_client() as client:
                try:
                    _handle_client(client, stc_agent)
                except _ClientDisconnected as err:
                    _LOG.debug(err)
                except _ExitCommand:
                    break

    _LOG.debug("Exiting")
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
