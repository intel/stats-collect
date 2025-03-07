.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

:Date:  25-03-2024
:Title: START

.. Contents::
    :depth: 2
..

=================
Command *'start'*
=================

usage: stats-collect start [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME]
[-K PRIVKEY] [-T TIMEOUT] [--cpus CPUS] [--time-limit LIMIT]
[-o OUTDIR] [--reportid REPORTID] [--stats STATS]
[--stats-intervals STATS_INTERVALS] [--list-stats] [--report] COMMAND

Run a command and collecting statistics. The COMMAND string may include
placeholders in "{}" braces, which will be replaced with actual values. The
following placeholders are supported:
 * {HOSTNAME}: The name of the host to run the command on.
 * {USERNAME}: The name of the user to use for logging into the remote host over SSH.
 * {PRIVKEY}: Path to the private SSH key that should be used for logging into the remote host.
              Defaults to "none".
 * {TIMEOUT}: SSH connect timeout in seconds.
 * {CPUS}: The list of CPUs to measure. Defaults to "none".
 * {OUTDIR}: The output directory where the result will be stored.
 * {REPORTID}: The Report ID of the result.
 * {STATS}: Comma-separated list of statistics names that will be collected.

General options
===============

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

**--cpus** *CPUS*
   If the executed command stresses particular CPU numbers, specify them
   via this option so that the numbers are saved in the test result and
   later the 'stats-collect report' command will take this into account
   while generating the test report. CPU numers should be specified as
   a comma-separated list of integers or integer ranges. For For example,
   '1-4,7,8,10-12' would mean CPUs 1 to 4, CPUs 7, 8, and 10 to 12.

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
   all possible statistics. Use ' --stats=""' or '--stats="none"' to
   disable statistics collection. If you know exactly what statistics
   you need, specify the comma-separated list of statistics to collect.
   For example, use 'turbostat,acpower' if you need only turbostat and
   AC power meter statistics. You can also specify the statistics you do
   not want to be collected by pre-pending the '!' symbol. For example,
   'all,!turbostat' would mean: collect all the statistics supported by
   the SUT, except for

**--stats-intervals** *STATS_INTERVALS*
   The intervals for statistics. Statistics collection is based on doing
   periodic snapshots of data. For example, by default the 'acpower'
   statistics collector reads SUT power consumption for the last second
   every second, and 'turbostat' default interval is 5 seconds. Use
   'acpower:5,turbostat:10' to increase the intervals to 5 and 10
   seconds correspondingly. Use the '--list-stats' to get the default
   interval values.

**--list-stats**
   Print information about the statistics 'stats-collect' can collect
   and exit.

**--report**
   Generate an HTML report for collected results (same as calling
   'report' command with default arguments).
