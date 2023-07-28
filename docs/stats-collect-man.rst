=============
STATS-COLLECT
=============

:Date: 2023-07-28

.. contents::
   :depth: 3
..

NAME
====

stats-collect

SYNOPSIS
========

**stats-collect** [-h] [-q] [-d] [--version] [--force-color]
{deploy,start,report} ...

DESCRIPTION
===========

stats-collect - a tool for collecting and visualising system statistics
and telemetry.

OPTIONS
=======

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--version**
   Print version and exit.

**--force-color**
   Force coloring of the text output.

COMMANDS
========

**stats-collect** *deploy*
   Deploy stats-collect helpers.

**stats-collect** *start*
   Start the measurements.

**stats-collect** *report*
   Create an HTML report.

COMMAND *'stats-collect* deploy'
================================

usage: stats-collect deploy [-h] [-q] [-d] [--tmpdir-path TMPDIR_PATH]
[--keep-tmpdir] [-H HOSTNAME] [-U USERNAME] [-K PRIVKEY] [-T TIMEOUT]

Deploy stats-collect helpers to a remote SUT (System Under Test).

OPTIONS *'stats-collect* deploy'
================================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--tmpdir-path** *TMPDIR_PATH*
   When 'stats-collect' is deployed, a random temporary directory is
   used. Use this option provide a custom path instead. It will be used
   as a temporary directory on both local and remote hosts. This option
   is meant for debugging purposes.

**--keep-tmpdir**
   Do not remove the temporary directories created while deploying
   'stats-collect'. This option is meant for debugging purposes.

**-H** *HOSTNAME*, **--host** *HOSTNAME*
   Name of the host to run the command on.

**-U** *USERNAME*, **--username** *USERNAME*
   Name of the user to use for logging into the remote host over SSH.
   The default user name is 'root'.

**-K** *PRIVKEY*, **--priv-key** *PRIVKEY*
   Path to the private SSH key that should be used for logging into the
   remote host. By default the key is automatically found from standard
   paths like '~/.ssh'.

**-T** *TIMEOUT*, **--timeout** *TIMEOUT*
   SSH connect timeout in seconds, default is 8.

COMMAND *'stats-collect* start'
===============================

usage: stats-collect start [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME]
[-K PRIVKEY] [-T TIMEOUT] [--cpunum CPUNUM] [--time-limit LIMIT] [-o
OUTDIR] [--reportid REPORTID] [--stats STATS] [--stats-intervals
STATS_INTERVALS] [--report] cmd [cmd ...]

Start collecting statistics.

**cmd**
   Command to run on the SUT during statistics collection. If 'HOSTNAME'
   is provided, the tool will run the command on that host, otherwise
   the tool will run the command on 'localhost'.

OPTIONS *'stats-collect* start'
===============================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**-H** *HOSTNAME*, **--host** *HOSTNAME*
   Name of the host to run the command on.

**-U** *USERNAME*, **--username** *USERNAME*
   Name of the user to use for logging into the remote host over SSH.
   The default user name is 'root'.

**-K** *PRIVKEY*, **--priv-key** *PRIVKEY*
   Path to the private SSH key that should be used for logging into the
   remote host. By default the key is automatically found from standard
   paths like '~/.ssh'.

**-T** *TIMEOUT*, **--timeout** *TIMEOUT*
   SSH connect timeout in seconds, default is 8.

**--cpunum** *CPUNUM*
   If the executed command stresses a particular CPU number, you can
   specify it via this option so that the number is saved in the test
   result and later the 'stats-collect report' command will take this
   into account while generating the test report.

**--time-limit** *LIMIT*
   The time limit for statistics collection, after which the collection
   will stop if the command 'cmd' (given as a positional argument) has
   not finished executing.

**-o** *OUTDIR*, **--outdir** *OUTDIR*

**--reportid** *REPORTID*
   Any string which may serve as an identifier of this run. By default
   report ID is the current date, prefixed with the remote host name in
   case the '-H' option was used: [hostname-]YYYYMMDD. For example,
   "20150323" is a report ID for a run made on March 23, 2015. The
   allowed characters are: ACSII alphanumeric, '-', '.', ',', '_', and
   '~'.

**--stats** *STATS*
   Comma-separated list of statistics to collect. They are stored in the
   the "stats" sub-directory of the output directory. By default, only
   'turbostat, sysinfo' statistics are collected. Use 'all' to collect
   all possible statistics. Use '--stats=""' or '-- stats="none"' to
   disable statistics collection. If you know exactly what statistics
   you need, specify the comma-separated list of statistics to collect.
   For example, use 'turbostat,acpower' if you need only turbostat and
   AC power meter statistics. You can also specify the statistics you do
   not want to be collected by pre-pending the '!' symbol. For example,
   'all,!turbostat' would mean: collect all the statistics supported by
   the SUT, except for 'turbostat'. Use the '--list-stats' option to get
   more information about available statistics. By default, only
   'sysinfo' statistics are collected.

**--stats-intervals** *STATS_INTERVALS*
   The intervals for statistics. Statistics collection is based on doing
   periodic snapshots of data. For example, by default the

seconds. Use 'acpower:5,turbostat:10' to increase the intervals to 5 and
10 seconds correspondingly. Use the '--list-stats' to get the default
interval values.

**--report**

COMMAND *'stats-collect* report'
================================

usage: stats-collect report [-h] [-q] [-d] [-o OUTDIR] [--reportids
REPORTIDS] respaths [respaths ...]

Create an HTML report for one or multiple test results.

**respaths**
   One or multiple stats-collect test result paths.

OPTIONS *'stats-collect* report'
================================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   Path to the directory to store the report at. By default the report
   is stored in the 'stats-collect-report-<reportid>' sub- directory of
   the test result directory. If there are multiple test results, the
   report is stored in the current directory. The

**--reportids** *REPORTIDS*
   Every input raw result comes with a report ID. This report ID is
   basically a short name for the test result, and it used in the HTML
   report to refer to the test result. However, sometimes it is helpful
   to temporarily override the report IDs just for the HTML report, and
   this is what the '--reportids' option does. Please, specify a
   comma-separated list of report IDs for every input raw test result.
   The first report ID will be used for the first raw rest result, the
   second report ID will be used for the second raw test result, and so
   on. Please, refer to the '--reportid' option description in the
   'start' command for more information about the report ID.

AUTHOR
======

::

   Artem Bityutskiy

::

   dedekind1@gmail.com

DISTRIBUTION
============

The latest version of stats-collect may be downloaded from
` <https://github.com/intel/stats-collect>`__
