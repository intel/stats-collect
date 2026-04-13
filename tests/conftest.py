# Copyright (C) 2023-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Add custom options for the tests."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import logging
import typing
import pytest
from pepclibs.helperlibs import Logging
from statscollecttools import ToolInfo

if typing.TYPE_CHECKING:
    pass

def pytest_configure(config: pytest.Config):
    """
    Configure pytest before running tests.

    Args:
        config: The pytest configuration object.
    """

    # Configure the stats-collect logger. Read the log level from the pytest config so that
    # '--log-cli-level=DEBUG' makes stats-collect emit debug messages.
    log_level_str = config.getoption("log_cli_level")
    if log_level_str and isinstance(log_level_str, str):
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    else:
        log_level = logging.INFO
    Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.{ToolInfo.TOOLNAME}").configure(
        prefix=ToolInfo.TOOLNAME, level=log_level, argv=[])
