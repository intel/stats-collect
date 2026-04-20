<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

Copyright (C) 2022-2024 Intel, Inc.
SPDX-License-Identifier: BSD-3-Clause

Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
-->

# Introduction

The Statistics Collection Tool project provides the 'stats-collect' command-line tool. This tool
collects system statistics and telemetry, and visualizes them. It’s for debugging and tracing
purposes only. It is for lab usage, not for production usage. The users are software engineers
debugging a problem in the Linux operating system.

## Installation

See [docs/guide-install.md](docs/guide-install.md) for full installation instructions.

## Basic Usage

Below outlines basic local usage of the 'stats-collect' tool involving how to collect and visualise
statistics.

All of the commands listed below can be used in conjunction with the `-h` option to learn more about
the command and other options that can be used with it.

### Start Statistics Collection

Start statistics collection using the `stats-collect start` command.

A command must be passed to `stats-collect start` to run on the system during the test (e.g. `sleep
30` is used in the example below).

Note that below the optional `-o` argument is used to specify an output directory.

```bash
stats-collect start -o stats-result 'sleep 30'
```

### Generate Report

Generate an HTML report to visualise the statistics collected using `stats-collect start`.

```bash
stats-collect report stats-result
```

To view the report, open the 'index.html' file in the report directory in a browser.

## Remote Usage

`stats-collect` can be used to collect statistics on a remote system. Generally, the process is very
similar to the local usage but there are some differences.

**Please note: in the following steps, the name of the system to measure should be used. For
documentation purposes, the example comands below will use a placeholder name 'SUTNAME'. Therefore,
please replace any instances of 'SUTNAME' with the name of the system you are trying to measure
before running the commands.**

### Deploy 'stats-collect'

Before collecting statistics with 'stats-collect' start, 'stats-collect deploy' should be used. This
is to deploy the 'stats-collect' helpers to the system which are required to collect statistics.

```bash
stats-collect deploy -H SUTNAME
```

### Start Remote Statistics Collection

The statistics collection step is very similar to the equivalent step in local usage. However it
differs because it requires the host option `-H SUTNAME` (like in the previous deployment step).

See [local usage](#start-statistics-collection), for more information on the other elements of this
command.

```bash
stats-collect start -H SUTNAME -o stats-result 'sleep 30'
```

### Generate Report Containing Remote Data

Generating a report for remote data works exactly the same way as locally. Remember to make sure
that the result directory you specify is the same as the directory passed as the output directory
the statistics collection step (using the `-o` option).

```bash
stats-collect report stats-result
```

## Documentation

For more information, documentation is available for each 'stats-collect' command accordingly:

* `stats-collect deploy` - [Documentation](docs/stats-collect-deploy.rst)
* `stats-collect start` - [Documentation](docs/stats-collect-start.rst)
* `stats-collect report` - [Documentation](docs/stats-collect-report.rst)
