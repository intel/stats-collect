<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
-->

# Installation Guide

- Author: Artem Bityutskiy <dedekind1@gmail.com>

## Table of Contents

- [Stats-collect Packages](#stats-collect-packages)
- [Running From Source](#running-from-source)
- [Installation Script](#installation-script)
- [Manual Installation](#manual-installation)
  - [Stats-collect Package Dependencies](#stats-collect-package-dependencies)
  - [Installation Using pip](#installation-using-pip)
  - [Using uv](#using-uv)
  - [Sudo Configuration](#sudo-configuration)
  - [Tab completions](#tab-completions)
  - [Man pages](#man-pages)
  - [Example of .bashrc](#example-of-bashrc)

## Stats-collect Packages

Some Linux distributions provide `stats-collect` as an installable package. However, these packages
are out of date, do not use them.

## Running From Source

You can run `stats-collect` directly from the source code without installation. Clone both
repositories (`pepc` is required as a dependency), and run `stats-collect` from the cloned
directory.

```bash
git clone https://github.com/intel/pepc.git
git clone https://github.com/intel/stats-collect.git
cd stats-collect
./stats-collect --help
```

This method is not recommended for regular use. For regular use, a proper installation is
recommended: it configures shell tab completions and man pages, so commands like
`man stats-collect-start` work out of the box.

## Installation Script

The `tools/install-stats-collect` script is the simplest way to install `stats-collect`. It takes
care of everything: installing `pepc` (a required dependency), installing OS dependencies, creating
the Python virtual environment, configuring shell tab completions, man pages, and adding a `sudo`
alias if needed.

Clone both repositories. The installation script spans both of them:

```bash
git clone https://github.com/intel/pepc.git
git clone https://github.com/intel/stats-collect.git
cd stats-collect
```

**Install the latest release from GitHub**

Run `tools/install-stats-collect` without arguments. It fetches and installs the latest `pepc` and
`stats-collect` releases directly from GitHub. The local clones are only used to run the script.

```bash
sudo -v && ./tools/install-stats-collect
```

**Install from local clones**

Use `--src-path` to install from the local clones instead. The script automatically looks for
`pepc` sources in the sibling directory (`../pepc`).

```bash
sudo -v && ./tools/install-stats-collect --src-path .
```

**Note**: the script runs most steps as the current user, but it requires `sudo` for installing OS
dependencies. The `sudo -v` pre-authorizes `sudo` credentials so the script can install
dependencies without prompting for a password.

**What the script does**

The script performs the steps described below in the [Manual Installation](#manual-installation)
section. Here is a high-level overview:

- Install OS dependencies using the system package manager (`dnf` or `apt`).
- Create a Python virtual environment in `~/.pmtools` and install `pepc`, `stats-collect`, and
  their Python dependencies there.
- Create `~/.pmtools/.pepc-rc.sh` and `~/.pmtools/.stats-collect-rc.sh` with all the necessary
  configuration and add lines to `~/.bashrc` to source them. The configuration includes the
  following:
  - Add `~/.pmtools/bin` to `PATH`.
  - Configure tab completions.
  - Configure manual pages.
  - Create `sudo` aliases for `pepc` and `stats-collect`.

`tools/install-stats-collect` has additional options to tune the installation (e.g., the
installation path), install `stats-collect` on a remote host over SSH, and control `sudo` alias
creation and style. Run `./tools/install-stats-collect --help` to see all available options.

## Manual Installation

The following sections describe how to install `stats-collect` manually, without using the
`tools/install-stats-collect` script. This is useful if you want full control over the
installation, use a custom environment, or prefer a different package manager.

`stats-collect` depends on `pepc`. Install `pepc` first. Refer to the
[pepc installation guide](https://github.com/intel/pepc/blob/main/docs/guide-install.md) for
instructions.

### Stats-collect Package Dependencies

`stats-collect` requires a few OS packages. Most are typically pre-installed, but verify they are
present on your system.

**Tools used by `stats-collect` at runtime:**

- `cat`, `id`, `uname` from the `coreutils` package.
- `pgrep`, `ps` from the `procps` package.

`stats-collect` uses statistics collectors such as `turbostat` and `ipmi`. The `turbostat`
collector requires the `turbostat` tool, and the `ipmi` collector requires `ipmitool`. Not all
collectors need to work: `stats-collect` runs with whichever collectors are available, but it does
need at least some. Install the tools for the collectors you intend to use separately.

There is also a special `sysinfo` collector that takes a snapshot of system information. It uses
various tools such as `lspci`, but does not require all of them: if a tool is missing, `sysinfo`
skips that piece of system information and continues.

**Tools needed for installation:**

- `pip3` and `virtualenv`: required for `pip`-based installation
   (see [Installation Using pip](#installation-using-pip)).
- `uv`: an alternative to `pip3` + `virtualenv` (see [Using uv](#using-uv)). Install one or the
  other.
- `rsync`: used to copy sources to a temporary directory during installation from a local path.

The commands below install the `pip3`-based tools. If you prefer `uv`, install it instead and skip
`python3-pip` and `python3-virtualenv`.

**Fedora / CentOS**

```bash
sudo dnf install -y procps-ng python3-pip python3-virtualenv rsync
```

**Ubuntu**

```bash
sudo apt install -y procps python3-pip python3-venv rsync
```

### Installation Using pip

This method installs `pepc` and `stats-collect` into the same Python virtual environment. The
installation does not require superuser privileges.

The example below uses `~/.pmtools` as the installation directory, consistent with the `pepc`
installation guide. If you installed `pepc` into a different location, adjust the path accordingly.

First, install `pepc`, then install `stats-collect` into the same virtual environment:

```bash
python3 -m venv ~/.pmtools
~/.pmtools/bin/pip3 install git+https://github.com/intel/pepc.git@release
~/.pmtools/bin/pip3 install git+https://github.com/intel/stats-collect.git@release
```

Ensure that `~/.pmtools/bin` is in your `PATH`. Add the following line to your `~/.bashrc` to make
it persistent.

```bash
export PATH="$PATH:$HOME/.pmtools/bin"
```

### Using uv

`uv` is a modern Python project and package manager. Install it using your distribution's package
manager. For example, on Fedora:

```bash
sudo dnf install uv
```

Install `pepc` first, then `stats-collect`:

```bash
uv tool install git+https://github.com/intel/pepc.git@release
uv tool install git+https://github.com/intel/stats-collect.git@release
```

`uv` installs tools to `$HOME/.local/bin`. Add the following line to your `~/.bashrc` to ensure
`stats-collect` is found.

```bash
export PATH="$PATH:$HOME/.local/bin"
```

### Sudo Configuration

Many `stats-collect` operations require superuser privileges. When `stats-collect` is installed in
a Python virtual environment, running it with `sudo` requires extra configuration: `sudo` resets
`PATH` and environment variables, which breaks virtual environment activation.

The same applies to `pepc`, which `stats-collect` depends on. The `pepc` installation guide covers
this in detail, but the snippets below include aliases for both tools for convenience.

Two `~/.bashrc` snippets are provided below for quick reference.

**Option 1: refresh**

The alias pre-authorizes `sudo` credentials before invoking the tool. Requires passwordless `sudo`
or prompts once per session.

```bash
alias pepc='sudo -v && pepc'
alias stats-collect='sudo -v && stats-collect'
```

**Option 2: wrap**

The alias passes the virtual environment variables to `sudo` explicitly.

```bash
VENV="$HOME/.pmtools"
VENV_BIN="$VENV/bin"
alias pepc="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/pepc"
alias stats-collect="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/stats-collect"
```

### Tab completions

`pepc` and `stats-collect` both support tab completions. Add the relevant lines to `~/.bashrc`,
depending on how the tools were installed.

```bash
# For pip installation (adjust path if you used a different location):
eval "$($HOME/.pmtools/bin/register-python-argcomplete pepc)"
eval "$($HOME/.pmtools/bin/register-python-argcomplete stats-collect)"

# For uv installation:
eval "$($HOME/.local/bin/register-python-argcomplete pepc)"
eval "$($HOME/.local/bin/register-python-argcomplete stats-collect)"
```

### Man pages

`pepc` and `stats-collect` both provide man pages (e.g., `man pepc-cstates`,
`man stats-collect-start`). When installed via `pip` or `uv`, the man pages land in Python's
`site-packages` directory, which `man` does not search by default. Add the following lines to
`~/.bashrc` to make them available.

```bash
export MANPATH="$MANPATH:$(pepc --print-man-path)"
export MANPATH="$MANPATH:$(stats-collect --print-man-path)"
```

Verify with:

```bash
man pepc-cstates
man stats-collect-start
```

### Example of .bashrc

The example below is for a `pip`-based installation into `~/.pmtools`, using the `refresh` sudo
approach. Adjust paths and the sudo alias as needed for your setup.

```bash
# === pepc and stats-collect settings ===
VENV="$HOME/.pmtools"
VENV_BIN="$VENV/bin"

# Ensure the virtual environment's bin directory is in the PATH.
export PATH="$PATH:$VENV_BIN"

# Sudo aliases: pre-authorize sudo credentials before invoking the tools.
alias pepc='sudo -v && pepc'
alias stats-collect='sudo -v && stats-collect'

# Enable tab completion for pepc and stats-collect.
eval "$($VENV_BIN/register-python-argcomplete pepc)"
eval "$($VENV_BIN/register-python-argcomplete stats-collect)"

# Enable man pages.
export MANPATH="$MANPATH:$($VENV_BIN/pepc --print-man-path)"
export MANPATH="$MANPATH:$($VENV_BIN/stats-collect --print-man-path)"
# === end of pepc and stats-collect settings ===
```
