<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

This file is converted to a man page using pandoc. The ":   " prefix uses the
pandoc definition list syntax to produce proper option entries in the man output.
-->

# Command *'start'*

Start collecting statistics. Run the *COMMAND* on the SUT and collect statistics while it runs.
The *COMMAND* string may include placeholders in `{}` braces that will be substituted with actual
values: `{HOSTNAME}`, `{USERNAME}`, `{PRIVKEY}`, `{OUTDIR}`, `{REPORTID}`, `{STATS}`,
`{PIPE_PATH}`.

## General options

**-h**

:   Show this help message and exit.

**-q**

:   Be quiet (print only important messages like warnings).

**-d**

:   Print debugging information.

**--debug-modules** *MODNAME[,MODNAME1,...]*

:   Print debugging information only from the specified modules.

**--force-color**

:   Force colorized output even if the output stream is not a terminal (adds ANSI escape codes).

**-H** *HOSTNAME*, **--host** *HOSTNAME*

:   The hostname of the system under test (SUT). The command will be executed on this system
    using SSH, instead of running it locally. If not specified, the command will be run locally.

**-U** *USERNAME*, **--username** *USERNAME*

:   Name of the user to use for logging into the remote host over SSH. By default, look up the
    user name in SSH configuration files. If not found, use the current user name.

**-K** *PRIVKEY*, **--priv-key** *PRIVKEY*

:   Path to the private SSH key for logging into the remote host. If not specified, keys
    configured for the host in SSH configuration files (e.g. `~/.ssh/config`) are used. If no
    keys are configured there, standard key files (e.g. `~/.ssh/id_rsa`) and the SSH agent are
    tried.

## Statistics collection options

**--time-limit** *LIMIT*

:   The time limit for statistics collection, after which the collection will stop if the command
    (given as a positional argument) has not finished executing. Specify time value in minutes, or
    use one of the following specifiers: d - days, h - hours, m - minutes, s - seconds. For
    example, '--time-limit=1h 30m' means 1 hour and 30 minutes.

**-o** *OUTDIR*, **--outdir** *OUTDIR*

:   Path to the directory to save the results at. By default the results are stored in a directory
    named after the report ID in the current directory.

**--reportid** *REPORTID*

:   Report ID which will serve as an identifier for this run. By default report ID is the current
    date, prefixed with the remote host name in case the '-H' option was used:
    `[hostname-]YYYYMMDD`. For example, "20150323" is a report ID for a run made on March 23,
    2015. The allowed characters are: ASCII alphanumeric, '-', '.', ',', '_', and '~'.

**--stats** *STATS*

:   Comma-separated list of statistics to collect. By default, only 'turbostat, sysinfo'
    statistics are collected. Use 'all' to collect all possible statistics. Use '--stats=""' or
    '--stats="none"' to disable statistics collection. You can also specify the statistics you do
    not want to collect by pre-pending the '!' symbol. For example, 'all,!turbostat' collects all
    statistics supported by the SUT, except for turbostat. Use '--list-stats' to get the full
    list of supported statistics and their descriptions.

**--stats-intervals** *STATS_INTERVALS*

:   Statistics collection intervals as a comma-separated list, e.g. 'acpower:5,turbostat:10' to
    collect SUT power consumption every 5 seconds and turbostat data every 10 seconds. Use
    '--list-stats' to get the default interval values.

**--list-stats**

:   Print information about the statistics 'stats-collect' can collect and exit.

**--report**

:   Generate an HTML report for collected results after the collection is done (same as calling
    'stats-collect report' with default arguments).

**--cmd-local**

:   Run the *COMMAND* on the local host instead of on the SUT (*HOSTNAME*). This is useful for
    client/server workloads where the SUT runs the server and the local host runs the client.

**-P** *PIPE_PATH*, **--pipe-path** *PIPE_PATH*

:   Path to the named pipe where the executed command will write labels to (on *HOSTNAME*). Use
    the special keyword "auto" to instruct 'stats-collect' to automatically create a named pipe
    in the temporary directory (use the `{PIPE_PATH}` placeholder in the workload's command line
    to get the path in this case). No named pipe is created by default.

**--pipe-timeout** *PIPE_TIMEOUT*

:   The longest allowed interval between named pipe input lines. The 'stats-collect' tool exits
    with an error if the interval exceeds *PIPE_TIMEOUT*. The default is 5 minutes. Specify time
    value in minutes, or use one of the following specifiers: d - days, h - hours, m - minutes,
    s - seconds. For example, '--pipe-timeout=1m 20s' means 1 minute and 20 seconds.

**cmd** *CMD [CMD ...]*

:   The command to run on the SUT during statistics collection. If *HOSTNAME* is provided, the
    tool will run the command on that host (unless '--cmd-local' was specified). Otherwise the
    tool will run the command on 'localhost'. The command may include placeholders in `{}` braces
    that will be substituted with actual values. The supported placeholders are `{HOSTNAME}`,
    `{USERNAME}`, `{PRIVKEY}`, `{OUTDIR}`, `{REPORTID}`, `{STATS}`, `{PIPE_PATH}`.
