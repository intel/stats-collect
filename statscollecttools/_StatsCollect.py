# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""stats-collect - a tool for collecting and visualizing system statistics and telemetry."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import sys
from pathlib import Path

try:
    import argcomplete
    argcomplete_imported = True
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    argcomplete_imported = False

from pepclibs.helperlibs import Logging, ArgParse
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.deploy import _Deploy
from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict
from statscollectlibs.collector import StatsCollectBuilder
from statscollecttools import ToolInfo

_STC_DEPLOY_INFO: DeployInfoTypedDict = {
    "installables": {
        "stc-agent": {
            "category": "pyhelpers",
            "deployables": ("stc-agent",
                            "stc-agent-ipmi-helper",
                            "stc-agent-proc-interrupts-helper"),
        },
        "stc-wl-cpu-wake-walk": {
            "category": "pyhelpers",
            "deployables": ("stc-wl-cpu-wake-walk",),
        },
    },
}

_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=ToolInfo.TOOLNAME)

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    if argcomplete_imported:
        completer = argcomplete.completers.DirectoriesCompleter()
    else:
        completer = None

    text = "stats-collect - a tool for collecting and visualizing system statistics and telemetry."
    parser = ArgParse.ArgsParser(description=text, prog=ToolInfo.TOOLNAME, ver=ToolInfo.VERSION)

    text = "Force coloring of the text output."
    parser.add_argument("--force-color", action="store_true", help=text)
    subparsers = parser.add_subparsers(title="commands", dest="a command")
    subparsers.required = True

    #
    # Create parsers for the "deploy" command.
    #
    subpars = _Deploy.add_deploy_cmdline_args(ToolInfo.TOOLNAME, subparsers, _deploy_command)

    #
    # Create parsers for the "start" command.
    #
    text = "Start the measurements."
    descr = """Start collecting statistics."""
    subpars = subparsers.add_parser("start", help=text, description=descr)
    subpars.set_defaults(func=_start_command)
    man_msg = "Please, refer to 'stats-collect-start' manual page for more information."

    # Adjust the help message for the '-H' option.
    ssh_options = []
    for optinfo in ArgParse.SSH_OPTIONS:
        if optinfo["short"] == "-H":
            optinfo = optinfo.copy()
            optinfo["kwargs"]["help"] = "The hostname of the system under test (SUT)."
        ssh_options.append(optinfo)

    ArgParse.add_options(subpars, ssh_options)

    text = """The time limit for statistics collection, after which the collection will stop if the
              command 'cmd' (given as a positional argument) has not finished executing."""
    subpars.add_argument("--time-limit", help=text, dest="tlimit", metavar="LIMIT", default=None)
    subpars.add_argument("-o", "--outdir",
                         type=Path).completer = completer # type: ignore[attr-defined]

    text = """Report ID which will serve as an identifier for this run. By default report ID is
              the current date, prefixed with the remote host name in case the '-H' option was 
              used. """ + man_msg
    subpars.add_argument("--reportid", help=text)

    default_stats = ", ".join(StatsCollectBuilder.DEFAULT_STNAMES)
    text = f"""Comma-separated list of statistics to collect. By default, only '{default_stats}'
               statistics are collected. """ + man_msg
    subpars.add_argument("--stats", default="default", help=text)

    text = """The intervals for statistics collection as a comma-separated list, e.g.
              'acpower:5,turbostat:10' to collect SUT power consumption every 5 seconds and
              turbostat data every 10 seconds. Use the '--list-stats' to get the default interval
              values. """ + man_msg
    subpars.add_argument("--stats-intervals", help=text)

    text = f"""Print information about the statistics '{ToolInfo.TOOLNAME}' can collect and exit."""
    subpars.add_argument("--list-stats", action="store_true", help=text)

    text = """Generate an HTML report for collected results (same as calling 'report' command with
              default arguments)."""
    subpars.add_argument("--report", action="store_true")

    text = """Run the command on the local host instead of the SUT ('HOSTNAME'). This is useful for
              client/server workloads where the SUT runs the server and the local host runs the
              client."""
    subpars.add_argument("--cmd-local", action="store_true", help=text)

    text = """Path to the named pipe where the executed command is going to write the lables to (on
              'HOSTNAME'). Use the special keyword "auto" to instruct 'stats-collect' to
              automatically create a named pipe in the temporary directory (use the "{PIPE_PATH}"
              placeholder on workload's command line to get the path in this case). No named pipe is
              created by default."""
    subpars.add_argument("-P", "--pipe-path", help=text, type=Path)

    duration_descr = "d - days, h - hours, m - minutes, s - seconds"
    text = f"""The longest allowed interval between named pipe input lines. The
               '{ToolInfo.TOOLNAME}' tool exits with an error if the interval exceeds
               'PIPE_TIMEOUT'. The default is 5 minutes. Specify time value in minutes, or use one
               of the following specifiers: {duration_descr}. For example, '--pipe-timeout=1m 20s'
               would mean mean 1 minute and 20 seconds."""
    subpars.add_argument("--pipe-timeout", help=text, type=Path, default="5m")

    text = """Command to run on the during statistics collection. If 'HOSTNAME' is provided,
              the tool will run the command on that host (unless '--cmd-local' was specified).
              Otherwise the tool will run the command on 'localhost'. The command may include
              placeholders in "{}" braces, which will be replaced with actual values. The supported
              placeholders are "{HOSTNAME}", "{USERNAME}", "{PRIVKEY}", "{TIMEOUT}", "{CPUS}",
              "{OUTDIR}", "{REPORTID}", "{STATS}", "{PIPE_PATH}". They will be substituted with the
              actual values of the corresponding options."""

    subpars.add_argument("cmd", type=str, nargs="+", help=text)

    #
    # Create parsers for the "report" command.
    #
    text = "Create an HTML report."
    descr = """Create an HTML report for one or multiple test results."""
    subpars = subparsers.add_parser("report", help=text, description=descr)
    subpars.set_defaults(func=_report_command)
    man_msg = "Please, refer to 'stats-collect-report' manual page for more information."

    text = f"""Path to the directory in which the report will be generated. By default the report
               is stored in the '{ToolInfo.TOOLNAME}-report-<reportid>' sub-directory of the test
               result directory. If there are multiple test results, the report is stored in the
               current directory. The '<reportid>' is report ID of {ToolInfo.TOOLNAME} test
               result."""
    subpars.add_argument("-o", "--outdir", type=Path, help=text)

    text = """A comma-separated list containing a report ID for every input raw test
              result. """ + man_msg
    subpars.add_argument("--reportids", help=text)

    text = """Copy raw test results to the output directory."""
    subpars.add_argument("--copy-raw", action="store_true", help=text)

    text = f"""One or multiple {ToolInfo.TOOLNAME} test result paths."""
    subpars.add_argument("respaths", nargs="+", type=Path, help=text)

    text = """The CPU numbers to include in the report, along with the system-wide statistics. By
              default, only the system-wide statistics are included. CPU numers should be specified
              as a comma-separated list of integers or integer ranges. For example, '1-4,7,8,10-12'
              would mean CPUs 1 to 4, CPUs 7, 8, and 10 to 12."""
    subpars.add_argument("--cpus", help=text)

    if argcomplete_imported:
        argcomplete.autocomplete(parser)

    return parser

def parse_arguments():
    """Parse input arguments."""

    parser = _build_arguments_parser()
    return parser.parse_args()

def _deploy_command(args):
    """Implements the 'stats-collect deploy' command."""

    from statscollecttools import _StatsCollectDeploy # pylint: disable=import-outside-toplevel

    _StatsCollectDeploy.deploy_command(args, _STC_DEPLOY_INFO)

def _start_command(args):
    """Implements the 'stats-collect start' command."""

    from statscollecttools import _StatsCollectStart # pylint: disable=import-outside-toplevel

    if args.list_stats:
        from statscollectlibs.collector import StatsCollect # pylint: disable=import-outside-toplevel

        StatsCollect.list_stats()
        return

    _StatsCollectStart.start_command(args, _STC_DEPLOY_INFO)

def _report_command(args):
    """Implements the 'stats-collect report' command."""

    from statscollecttools import _StatsCollectReport # pylint: disable=import-outside-toplevel

    _StatsCollectReport.report_command(args)

def main():
    """Script entry point."""

    try:
        args = parse_arguments()

        if not getattr(args, "func", None):
            _LOG.error("please, run '%s -h' for help", ToolInfo.TOOLNAME)
            return -1

        args.func(args)
    except KeyboardInterrupt:
        _LOG.info("Interrupted, exiting")
        return -1
    except Error as err:
        _LOG.error_out(err)

    return 0

# The script entry point.
if __name__ == "__main__":
    sys.exit(main())
