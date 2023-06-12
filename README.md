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

## CentOS 9 Stream

'stats-collect' is available for CentOS 9 Stream via the 'epel' repository. Here is how to add 'epel' and
install 'stats-collect'.

```
sudo dnf install epel-release
sudo dnf install stats-collect
```

Epel packages are maintained by Ali Erdinç Köroğlu <ali.erdinc.koroglu@intel.com>.

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

# Authors and contributors

* Artem Bityutskiy <dedekind1@gmail.com> - original author, project maintainer.
* Antti Laakso <antti.laakso@linux.intel.com> - contributor, project maintainer.
* Adam Hawley <adam.james.hawley@intel.com> - contributor, project maintainer.
* Niklas Neronin <niklas.neronin@intel.com> - contributor.
