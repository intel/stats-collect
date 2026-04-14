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
    from typing import Final, TypedDict

    class _CmdlineArgsTypedDict(TypedDict, total=False):
        """
        Typed dictionary representing the command-line arguments.

        Attributes:
            unix: Path to the Unix socket to listen on. 'None' means a socket file with a random name is created in the temporary directory.
            port: TCP port number to listen on. '-1' means use a Unix socket instead.
            sutname: The SUT name, used in socket file name and log messages.
        """

        unix: Path | None
        port: int
        sutname: str

_VERSION: Final[str] = ToolInfo.VERSION
_TOOLNAME: Final[str] = "stc-agent"

# The values for statistics collector properties which mean that the property was not initialized.
# If the property is required to be initialize, the key name starts with "required-".
_UNINITIALIZED = {
    # Not required to be initialized.
    "str" : "<not configured>",
    "int" : -1000000000000,
    # Non-optional property, required to be initialized.
    "required-str" : "<must be configured>",
    "required-int" : -9999999999999,
}

# The messages delimiter prefix. Every time it appears following a newline, it marks the end of
# the message.
_DELIMITER = "--"

# Names of the supported statistics.
_SUPPORTED_STATS = ("turbostat", "interrupts", "ipmi-oob", "ipmi-inband", "acpower")

_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=_TOOLNAME)

# Our own process ID.
_PID = Trivial.get_pid()

class _ClientDisconnected(Exception):
    """Raise when a client disconnects."""

class _ExitCommand(Exception):
    """Raise to signal that the agent should exit."""

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
    In case 'satsd' is started in a PID namespace and it is PID1, the default signal handlers are
    not set up, and this handler is installed to exit on 'SIGTERM' and 'SIGINT' signals.
    """

    _LOG.debug("Received signal '%d', exiting", sig)
    raise SystemExit(sig)

class _BaseCollector:
    """
    The base class for statistics collectors. Here is the methods overview.

    1. '__init__()' - the object constructor, performs basic initialization. The collector is not
       usable yet, because it has not been configured yet (e.g., the output directory was not yet
       set).
    2. 'configure()' - must be called every time a collector property have been changed (e.g., the
       output directory).
    4. 'start()' - start collecting the statistics
    5. 'stop()' - stop collecting the statistics
    6. 'save()' - save the results to the output directory, synchronize all the stats and flush all
                  the buffers.
    7. 'validate()' - validate the collected data to make sure it is sane

    Once the collector is initialized, the usage sequence is as follows.
      * Set various collector properties like 'outdir'
      * 'configure()
      * start()
      * stop()
      * save()
      * validate()
    The sequence can be repeated many times.
    """

    def __init__(self, name):
        """
        Initialize a class instance. The 'name' parameter is the name of the statistics to collect.
        """

        self.name = name

        # The collector properties that can be changed directly, but any change requires the
        # 'configure()' method to be executed for the changes to take the effect.
        self.props = {}
        # Whether this collector is allowed to fail without causing an error.
        self.props["fallible"] = False
        # The output directory where the statistics will be stored.
        self.props["outdir"] = _UNINITIALIZED["required-str"]
        # The log directory where may put their standard error output.
        self.props["logdir"] = _UNINITIALIZED["required-str"]
        # The statistics collection interval.
        self.props["interval"] = _UNINITIALIZED["required-str"]

        # The local process manager object.
        self._pman = LocalProcessManager.LocalProcessManager()

        #
        # These attributes are internal to this base class.
        #

        self._fobj = None
        # The statistics collector process.
        self._proc = None
        self._outpath = None

        #
        # These attributes can/should be set by child classes.
        #
        self._outfile = f"{name}.raw.txt"
        self._command = None
        self._configured = False
        self._valid_start = None
        self._valid_end = None
        self._signal = signal.SIGTERM
        self._stale_search = None

    def __del__(self):
        """Class destructor."""

        if getattr(self, "_pman", None):
            self._pman.close()
            self._pman = None
        if getattr(self, "_fobj", None):
            self._fobj.close()
            self._fobj = None

    def _error(self, msgformat, *args):
        """The collector error handler."""

        if args:
            msg = msgformat % args
        else:
            msg = str(msgformat)

        raise Error(f"The '{self.name}' statistics collector failed:\n{msg}")

    def _debug(self, msgformat, *args):
        """The collector debug messages."""

        if args:
            msg = msgformat % args
        else:
            msg = str(msgformat)

        _LOG.debug("'%s': %s", self.name, msg)

    def _sync(self):
        """Synchronize all the collector files."""

        def _fsync(fobj):
            """Synchronize the 'fobj' file."""

            try:
                fobj.flush()
                os.fsync(fobj.fileno())
            except OSError as err:
                self._error("Cannot synchronize '%s':\n%s", fobj.name, err)

        _fsync(self._fobj)

    def _handle_dirs(self):
        """Make sure the output directory exists."""

        for key in ("outdir", "logdir"):
            path = self.props[key]
            if not os.path.isabs(path):
                self._error("Path '%s' (%s) is not absolute", path, key)
            if os.path.exists(path):
                if not os.path.isdir(path):
                    self._error("Path '%s' (%s) already exists and it is not a directory",
                                path, key)
            else:
                self._debug("Creating directory '%s' (%s)", path, key)
                try:
                    os.mkdir(path)
                except OSError as err:
                    self._error("Cannot create directory '%s' (%s):\n%s", path, key, err)

    def configure(self):
        """Configure the statistics collector."""

        # Validate that all of the mandatory properties have been set.
        for prop, val in self.props.items():
            if val in (_UNINITIALIZED["required-str"], _UNINITIALIZED["required-int"]):
                self._error("Please configure '%s' first", prop)

        self._handle_dirs()

        self._outpath = os.path.join(self.props["outdir"], self._outfile)

        if self._fobj:
            self._fobj.close()
            self._fobj = None

        try:
            # pylint: disable=consider-using-with
            self._fobj = open(self._outpath, "wb+", buffering=0)
        except OSError as err:
            self._error("Failed to open '%s':\n%s", self._outpath, err)

        self._sync() # Flush any newly created files.
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

        self._proc = self._pman.run_async(self._command, stderr=self._fobj, stdout=self._fobj,
                                          newgrp=True)

    def end(self):
        """Stop collecting and get the resulting statistics."""

        exitcode = self._proc.poll()
        if exitcode is not None:
            self._error("The following command exited prematurely with exit code %d:\n%s",
                        exitcode, self._command)
        else:
            try:
                pgid = Trivial.get_pgid(self._proc.pid)
            except Error as err:
                self._error(err)

            # Signal the entire statistics collector process group.
            self._debug("Sending signal %s to PGID %d (group of PID %d)",
                        self._signal, pgid, self._proc.pid)
            try:
                os.killpg(pgid, self._signal)
            except OSError as err:
                self._error("Failed to kill the process group of PID %d, PGID %d:\n%s",
                            self._proc.pid, pgid, err)

    def save(self):
        """Save the collected statistics."""

        # Make sure the process has exited. The reason it is done in 'save()' is a hacky
        # optimization: all processes are signaled first without waiting (in 'end()'), and
        # only once all are signaled does checking begin. This
        # approach helps having the collectors stop "more simultaneously".
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
        self.props["toolpath"] = "turbostat"
        self.props["opts"] = _UNINITIALIZED["str"]

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        self._command = f"{self.props['toolpath']} --enable Time_Of_Day_Seconds " \
                        f"--interval '{self.props['interval']}'"

        if self.props["opts"] != _UNINITIALIZED["str"]:
            self._command += " " + self.props["opts"]

        toolname = os.path.basename(self.props["toolpath"])
        self._stale_search = f"{toolname} --enable Time_Of_Day_Seconds --interval "

        try:
            self._pman.run_verify("modprobe intel_uncore_frequency")
        except Error as err:
            _LOG.debug("Unable to load 'intel_uncore_frequency' module which is required "
                       "to collect turbostat uncore frequency measurements: %s", {str(err)})

class _InterruptsCollector(_BaseCollector):
    """The interrupts statistics collector - periodically snapshot '/proc/interrupts'."""

    def __init__(self):
        """Initialize a class instance."""

        super().__init__("interrupts")

        self.props["toolpath"] = "stc-agent-proc-interrupts-helper"
        self._signal = signal.SIGINT

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        self._command = f"{self.props['toolpath']} --interval {self.props['interval']}"

class _IPMICollector(_BaseCollector):
    """Base class for IPMI statistics collectors."""

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        self._command = f"{self.props['toolpath']} --interval '{self.props['interval']}'"
        if self.props["retries"] != _UNINITIALIZED["int"]:
            self._command += f" --retries '{self.props['retries']}'"
        if self.props["count"] != _UNINITIALIZED["int"]:
            self._command += f" --count '{self.props['count']}'"

        self._stale_search = f"{os.path.basename(self.props['toolpath'])} --interval "

    def __init__(self, name):
        """Initialize a class instance."""

        super().__init__(name)
        self.props["toolpath"] = "stc-agent-ipmi-helper"
        self.props["retries"] = _UNINITIALIZED["int"]
        self.props["count"] = _UNINITIALIZED["int"]
        self._valid_start = b"timestamp | "

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
        self.props["host"] = _UNINITIALIZED["required-str"]
        self.props["user"] = _UNINITIALIZED["str"]
        self.props["pwdfile"] = _UNINITIALIZED["str"]
        self.props["interface"] = _UNINITIALIZED["str"]

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        hostopt = f" --host '{self.props['host']}'"
        self._command += hostopt
        if self.props["user"] != _UNINITIALIZED["str"]:
            self._command += f" --user '{self.props['user']}'"
        if self.props["pwdfile"] != _UNINITIALIZED["str"]:
            self._command += f" --password-file '{self.props['pwdfile']}'"
        if self.props["interface"] != _UNINITIALIZED["str"]:
            self._command += f" -I '{self.props['interface']}'"

        self._stale_search += f".*{hostopt}"

class _ACPowerCollector(_BaseCollector):
    """The ACPower statistics collector."""

    def __init__(self):
        """Initialize a class instance."""

        super().__init__("acpower")
        self.props["toolpath"] = "yokotool"
        self.props["devnode"] = _UNINITIALIZED["required-str"]
        self.props["pmtype"] = _UNINITIALIZED["str"]
        self._signal = signal.SIGINT

    def configure(self):
        """Configure the statistics collector."""

        super().configure()

        devnode = self.props['devnode']
        cmd = f"{self.props['toolpath']} {devnode}"
        if self.props["pmtype"] != _UNINITIALIZED["str"]:
            cmd += f" --pmtype {self.props['pmtype']}"

        self._stale_search = f"{os.path.basename(self.props['toolpath'])} {devnode}"

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

        self._started = False
        self._collectors = {}
        self.failed_collectors = set()

        # The labels file object.
        self._lfobj = None

        # Statistics collection agent properties.
        self.props = {}
        # The output directory where data like labels will be stored.
        self.props["outdir"] = _UNINITIALIZED["str"]

    def _execute_collectors_methods(self, methods):
        """Execute collector object methods defined by the 'methods' list of strings."""

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
                    msg = f"The '{method}' method of the {collector.name} collector failed:\n" \
                          f"{err.indent(2)}"
                    if collector.props["fallible"]:
                        _LOG.debug(msg)
                    else:
                        raise Error(msg) from err
                else:
                    _LOG.debug("'%s' method of the %s collector succeeded", method, collector.name)

    def create(self, stnames):
        """
        Create the statistics collector objects for the statistics names in the 'stnames' list.
        """

        if not stnames:
            raise Error("Please, specify at least one statistic name")
        if self._started:
            raise Error("Statistics collection has been started, cannot create collectors")

        _LOG.debug("Creating the following collectors: %s", ",".join(stnames))

        # First close the previously initialized collectors.
        for name in list(self._collectors):
            del self._collectors[name]
        self.failed_collectors = set()

        for stname in stnames:
            if stname not in _SUPPORTED_STATS:
                raise Error(f"Unknown statistics name '{stname}'")

        for name in stnames:
            try:
                _LOG.debug("Creating the %s collector", name)
                if name == "turbostat":
                    collector = _TurbostatCollector()
                elif name == "interrupts":
                    collector = _InterruptsCollector()
                elif name == "ipmi-oob":
                    collector = _IPMIOOBCollector()
                elif name == "ipmi-inband":
                    collector = _IPMIInBandCollector()
                elif name == "acpower":
                    collector = _ACPowerCollector()
                else:
                    raise Error(f"Unsupported collector '{name}'")

                self._collectors[name] = collector
            except Error as err:
                raise Error(f"Failed to create the {name} collector:\n{err.indent(2)}") from err

        _LOG.debug("Created the collectors")

    @staticmethod
    def _set_obj_property(obj, name, value):
        """Set a property in object 'obj' (e.g., a statistics collector)."""

        the_type = type(obj.props[name])

        try:
            # Since 'bool("False")' is 'True', boolean props require a special case.
            if the_type == bool:
                if value not in ("True", "False"):
                    raise TypeError
                obj.props[name] = (value == "True")
            else:
                obj.props[name] = the_type(value)
        except TypeError as err:
            raise Error(f"Type conversion error for property '{name}' {obj.name}':\nstring "
                        f"'{value}' cannot be converted to '{the_type}'") from err

    def set_collector_property(self, args):
        """Set a property of a statistic collector."""

        if not self._collectors:
            raise Error("No statistics collectors selected")

        if self._started:
            raise Error("Statistics collection has been started, cannot change properties")

        if len(args.split()) < 3:
            raise Error(f"Incorrect argument '{args}'\nThe argument must be in the following "
                        f"format:\n<stat_name> <property_name> <property_value>")

        args = args.split(maxsplit=2)
        print(args)
        if args[0] not in self._collectors:
            all_stats = ", ".join(_SUPPORTED_STATS)
            raise Error(f"Unknown collector name '{args[0]}', use one of:\n{all_stats}")

        collector = self._collectors[args[0]]

        if collector.name in self.failed_collectors:
            # Ignore failed collectors.
            return

        if args[1] not in collector.props:
            raise Error(f"The '{collector.name}' collector does not support the '{args[1]}' "
                        f"property")

        self._set_obj_property(collector, args[1], args[2])

        _LOG.debug("Set collector '%s' property '%s' to value '%s'",
                   collector.name, args[1], args[2])

    @staticmethod
    def _set_outdir(path):
        """Set 'stc-agent' output directory."""

        if not os.path.isabs(path):
            raise Error(f"The 'stc-agent' output directory path '{path}' is not absolute")
        if os.path.exists(path):
            if not os.path.isdir(path):
                raise Error(f"The 'stc-agent' output directory path '{path}' already exists and it is "
                            f"not a directory")
        else:
            _LOG.debug("Creating 'stc-agent' output directory '%s'", path)
            try:
                os.mkdir(path)
            except OSError as err:
                raise Error(f"Cannot create 'stc-agent' output directory '{path}':\n{err}") from err

    def set_property(self, args):
        """Set an stc-agent property."""

        if len(args.split()) != 2:
            raise Error(f"Incorrect 'stc-agent' property argument '{args}'\nIt must be in the "
                        f"following format:\n<property_name> <property_value>")

        pname, pval = args.split()
        if pname not in self.props:
            supported = ", ".join(self.props)
            raise Error(f"Unsupported 'stc-agent' property '{pname}', supported properties are: "
                        f"{supported}")

        self._set_obj_property(self, pname, pval)
        if pname == "outdir":
            self._set_outdir(pval)

        _LOG.debug("Set 'stc-agent' property '%s' to value '%s'", pname, pval)

    def configure(self):
        """Configure the statistic collectors."""

        if not self._collectors:
            raise Error("No statistics collectors selected")

        if self._started:
            raise Error("Statistics collection has been started, cannot configure")

        self._execute_collectors_methods(("configure", "kill_stale"))
        _LOG.debug("Configured the collectors")

    def add_label(self, args):
        """
        Add a label. The 'args' argument is expected to be a JSON-serialized dictionary. It must
        include the "name" key for the label name, and any number of other keys.
        """

        if not self._collectors:
            raise Error("No statistics collectors selected")

        if self.props["outdir"] == _UNINITIALIZED["str"]:
            raise Error("Cannot add 'stc-agent' label: The output directory was not set")

        _LOG.debug("Adding label '%s'", args)

        import json # pylint: disable=import-outside-toplevel

        try:
            label = json.loads(args)
        except ValueError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to parse label JSON:\n{errmsg}") from err

        # Sanity check: make sure the 'name' key is present and make sense.
        name = label.get("name")
        if not name:
            raise Error(f"No label name provided in '{args}'")
        if not name.isalnum():
            raise Error(f"Bad label name '{name}': Must be alphanumeric")

        # Sanity check: there should be no 'ts' key, stc-agent is supposed to add it.
        if "ts" in label:
            raise Error(f"Found reserved key 'ts' in label '{args}")

        if not self._lfobj:
            try:
                path = Path(self.props["outdir"]) / "labels.txt"
                # pylint: disable=consider-using-with
                self._lfobj = open(path, "w", encoding="utf-8")
            except OSError as err:
                errmsg = Error(str(err)).indent(2)
                raise Error(f"Failed to create file '{path}:\n{errmsg}") from err

            # The first line provides the list of collectors the labels file covers.
            names = ",".join(self._collectors)
            self._lfobj.write(f"# {names}\n")

        label["ts"] = time.time()

        try:
            label = json.dumps(label)
        except ValueError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to serialize label JSON:\n{errmsg}") from err

        self._lfobj.write(f"{label}\n")

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

        _LOG.debug("Stopped the collectors")

        if self._lfobj:
            try:
                self._lfobj.flush()
                os.fsync(self._lfobj.fileno())
            except OSError as err:
                errmsg = Error(str(err)).indent(2)
                raise Error(f"Failed to synchronize 'stc-agent' labels file:\n{errmsg}") from err

            self._lfobj.close()
            self._lfobj = None

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
        cmd: The raw command string received from the client, including any arguments separated
             by a space.
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

def _main() -> int:
    """Implement main logic."""

    if _PID == 1:
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
