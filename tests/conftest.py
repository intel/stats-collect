# Copyright (C) 2023-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Add custom options for the tests."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import logging
import typing

# pylint: disable-next=wrong-import-order,unused-import
import tests._ForceSourceTree

import pytest
from pepclibs.helperlibs import Logging
from statscollecttools import ToolInfo

if typing.TYPE_CHECKING:
    pass

# The test modules that do not require a host connection.
_NOHOST_MODULES: frozenset[str] = frozenset({
    "tests.test_logging_cmdl",
    "tests.test_module_InterruptsDFBuilder",
    "tests.test_module_InterruptsParser",
    "tests.test_report_command",
})

def pytest_addoption(parser: pytest.Parser):
    """Add custom command-line options for pytest."""

    text = """Name of the host to run the tests on. Defaults to 'localhost'. Provide a hostname
              to run the tests on a remote host over SSH."""
    parser.addoption("-H", "--host", dest="hostname", default="localhost", help=text)

    text = """Name of the user to use for logging into the remote host over SSH. By default,
              the user name is looked up in SSH configuration files, and if not found, the
              current user name is used."""
    parser.addoption("-U", "--username", dest="username", default="", help=text)

def pytest_generate_tests(metafunc: pytest.Metafunc):
    """
    Parametrize test cases based on custom options.

    Args:
        metafunc: The pytest 'Metafunc' object that provides information about the test function
                  being collected.
    """

    assert metafunc.module is not None

    if metafunc.module.__name__ in _NOHOST_MODULES:
        return

    hostname = metafunc.config.getoption("hostname")
    username = metafunc.config.getoption("username")
    assert isinstance(hostname, str)
    assert isinstance(username, str)

    metafunc.parametrize("hostspec", [hostname], scope="module")
    metafunc.parametrize("username", [username], scope="module")

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
