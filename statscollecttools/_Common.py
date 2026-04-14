# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam James Hawley <adam.james.hawley@linux.intel.com>

"""This module contains miscellaneous functions used by various 'statscollecttools' modules."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import sys
from pathlib import Path
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error

def configure_log_file(outdir: Path, toolname: str) -> Path:
    """
    Configure the logger to mirror all the standard output and standard error a log file.

    Args:
        outdir: The log file directory.
        toolname: Name of the tool to use in the log file name.

    Returns:
        The path to the log file.
    """

    try:
        outdir.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        errmsg = Error(str(err)).indent(2)
        raise Error(f"Cannot create log directory '{outdir}':\n{errmsg}") from None

    logpath = Path(outdir) / f"{toolname}.log.txt"
    contents = f"Command line: {' '.join(sys.argv)}\n"
    logger = Logging.getLogger(Logging.MAIN_LOGGER_NAME)
    logger.configure_log_file(logpath, contents=contents)

    return logpath

def print_module_paths():
    """
    Print paths to the 'pepc' and 'stats-collect' project modules that have been imported.
    """

    for name, mobj in sys.modules.items():
        path = getattr(mobj, "__file__", "")
        if not path:
            continue

        if not path.endswith(".py"):
            continue

        # Use the top-level package name to identify the project. For a module like
        # 'pepclibs.helperlibs.Trivial', the top-level package is 'pepclibs'.
        toplevel = name.split(".")[0]
        if not toplevel.startswith(("pepc", "statscollect")):
            continue

        print(path)
