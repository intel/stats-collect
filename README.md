<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

Copyright (C) 2022-2023 Intel, Inc.
SPDX-License-Identifier: BSD-3-Clause

Author: Adam Hawley <adam.james.hawley@intel.com>
-->

# Introduction

The Statistics Collection Tool project provides the 'stats-collect' command-line tool. This tool
collects system statistics and telemetry, and visualizes them. It’s for debugging and tracing
purposes only. It is for lab usage, not for production usage. The users are software engineers
debugging a problem in the Linux operating system.

The 'stats-collect' man page is available [here](docs/stats-collect-man.rst).

# Installation

## Dependency on 'pepc'

Note, the 'stats-collect' project is dependent on the ['pepc' tool](https://github.com/intel/pepc).

This means that you will need to install 'pepc' before installing 'stats-collect'. Please check the
['pepc' documentation](https://github.com/intel/pepc#installation) for information on how to install
it.

## Fedora

'stats-collect' is part of Fedora starting from Fedora 35. To install 'stats-collect', run

```
sudo dnf install stats-collect
```

Fedora packages are maintained by Ali Erdinç Köroğlu <ali.erdinc.koroglu@intel.com>.

In case of Fedora 34 or older Fedora, use the 'pip' installation method.

## CentOS 8 Stream

To install 'stats-collect' in CentOS stream, you can use the
["copr"](https://copr.fedorainfracloud.org/coprs/aekoroglu/c8s-py39/) repository
maintained by Ali Erdinç Köroğlu <ali.erdinc.koroglu@intel.com>.

Run the following commands.

```
sudo dnf copr enable aekoroglu/c8s-py39 centos-stream-8-x86_64
sudo dnf install stats-collect
```

## Ubuntu and Debian

We do not provide Ubuntu/Debian packages, so you'll need to use the 'pip' installation method.

## Installing with 'pip'

Run the following command:

```
sudo pip3 install --upgrade git+https://github.com/intel/stats-collect.git@release
```

This command will download 'stats-collect' from the 'release' branch of the git repository and
install it to the system.

The other way of doing this is by first cloning the git repository and running

```
git clone https://github.com/intel/stats-collect.git --branch release stats-collect
cd stats-collect
pip3 install --upgrade .
```

Note, 'stats-collect' has to be run with superuser (root) privileges in many cases, and if you
install it with the '--user' option of 'pip3', it won't work "out of the box". This is why we do not
recommend using '--user'.

# Basic Usage

Below outlines basic local usage of the 'stats-collect' tool involving how to collect and visualise
statistics.

All of the commands listed below can be used in conjunction with the `-h` option to learn more about
the command and other options that can be used with it. For more information, it is recommended that
users refer to the 'stats-collect' [man page](docs/stats-collect-man.rst).

## Start Statistics Collection

Start statistics collection using the `stats-collect start` command.

A command must be passed to `stats-collect start` to run on the system during the test (e.g. `sleep
30` is used in the example below).

Note that below the optional `-o` argument is used to specify an output directory.

```
stats-collect start -o stats-result 'sleep 30'
```

## Generate Report

Generate an HTML report to visualise the statistics collected using `stats-collect start`.

```
stats-collect report stats-result
```

To view the report, open the 'index.html' file in the report directory in a browser.

# Remote Usage

`stats-collect` can be used to collect statistics on a remote system. Generally, the process is very
similar to the local usage but there are some differences.

**Please note: in the following steps, the name of the system to measure should be used. For
documentation purposes, the example comands below will use a placeholder name 'SUTNAME'. Therefore,
please replace any instances of 'SUTNAME' with the name of the system you are trying to measure
before running the commands.**

## Deploy 'stats-collect'

Before collecting statistics with 'stats-collect' start, 'stats-collect deploy' should be used. This
is to deploy the 'stats-collect' helpers to the system which are required to collect statistics.

```
stats-collect deploy -H SUTNAME
```

## Start Remote Statistics Collection

The statistics collection step is very similar to the equivalent step in local usage. However it
differs because it requires the host option `-H SUTNAME` (like in the previous deployment step).

See [local usage](#start-statistics-collection), for more information on the other elements of this
command.

```
stats-collect start -H SUTNAME -o stats-result 'sleep 30'
```

## Generate Report Containing Remote Data

Generating a report for remote data works exactly the same way as locally. Remember to make sure
that the result directory you specify is the same as the directory passed as the output directory
the statistics collection step (using the `-o` option).

```
stats-collect report stats-result
```

# Authors and contributors

* Artem Bityutskiy <dedekind1@gmail.com> - original author, project maintainer.
* Antti Laakso <antti.laakso@linux.intel.com> - contributor, project maintainer.
* Adam Hawley <adam.james.hawley@intel.com> - contributor, project maintainer.
* Niklas Neronin <niklas.neronin@intel.com> - contributor.
