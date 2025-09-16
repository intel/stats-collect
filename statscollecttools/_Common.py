# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
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
        outdir: the log file directory.
        toolname: name of the tool to use in the log file name.

    Returns:
        Path: the path to the log file.
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
