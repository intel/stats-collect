.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

:Date:  25-03-2024
:Title: REPORT

.. Contents::
    :depth: 2
..

==================
Command *'report'*
==================

usage: stats-collect report [-h] [-q] [-d] [-o OUTDIR] [--reportids REPORTIDS]
[--copy-raw] respaths [respaths ...]

Create an HTML report for one or multiple test results.

**respaths**
   One or multiple stats-collect test result paths.

General options
===============

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   Path to the directory to store the report at. By default the report
   is stored in the 'stats-collect-report-<reportid>' sub-directory of
   the test result directory. If there are multiple test results, the
   report is stored in the current directory. The '<reportid>' is report
   ID of stats-collect test result.

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

**--copy-raw**
   Copy raw test results to the output directory (unless the output
   direcory is already part of the raw result sub-directory).

**--cpus** *CPUS*
    The CPU numbers to include in the report, along with the system-wide
    statistics. By default, only the system-wide statistics are included. CPU numers should be
    specified as a comma-separated list of integers or integer ranges. For example, '1-4,7,8,10-12'
    would mean CPUs 1 to 4, CPUs 7, 8, and 10 to 12.
