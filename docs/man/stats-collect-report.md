<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

This file is converted to a man page using pandoc. The ":   " prefix uses the
pandoc definition list syntax to produce proper option entries in the man output.
-->

# Command *'report'*

Create an HTML report for one or multiple test results.

## General options

**-h**

:   Show this help message and exit.

**-q**

:   Be quiet (print only important messages like warnings).

**-d**

:   Print debugging information.

**--debug-modules** *MODNAME[,MODNAME1,...]*

:   The '-d' option enables all debug messages. This option limits them to the specified
    modules. For example, '-d --debug-modules MSR' will only show debug messages from the
    'MSR' module.

**--force-color**

:   Force colorized output even if the output stream is not a terminal (adds ANSI escape codes).

## Report options

**-o** *OUTDIR*, **--outdir** *OUTDIR*

:   Path to the directory in which the report will be generated. By default the report is stored
    in the 'stats-collect-report-\<reportid\>' sub-directory of the test result directory. If
    there are multiple test results, the report is stored in the current directory. The
    '\<reportid\>' is the report ID of the first stats-collect test result.

**--reportids** *REPORTIDS*

:   A comma-separated list containing a report ID for every input raw test result. Every input
    raw result comes with a report ID, which is a short name used in the HTML report to refer to
    the test result. Use this option to temporarily override the report IDs just for the HTML
    report. The first report ID will be used for the first raw test result, the second for the
    second raw test result, and so on. Please refer to the '--reportid' option description in the
    'stats-collect start' manual page for more information about the report ID format.

**--copy-raw**

:   Copy raw test results to the output directory (unless the output directory is already part of
    the raw result sub-directory).

**--cpus** *CPUS*

:   The CPU numbers to include in the report, along with the system-wide statistics. By default,
    only the system-wide statistics are included. CPU numbers should be specified as a
    comma-separated list of integers or integer ranges. For example, '1-4,7,8,10-12' would mean
    CPUs 1 to 4, CPUs 7, 8, and 10 to 12.

**respaths** *RESPATH [RESPATH ...]*

:   One or multiple stats-collect test result paths.
