# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Common bits for the tests."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
from pepclibs.helperlibs import ProcessManager

if typing.TYPE_CHECKING:
    from typing import TypedDict
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType

    class CommonTestParamsTypedDict(TypedDict):
        """
        A dictionary of common test parameters.

        Attributes:
            hostname: The hostname of the target system.
            pman: The process manager instance for managing processes on the target system.
        """

        hostname: str
        pman: ProcessManagerType

def get_prj_src_path() -> Path:
    """
    Return the path to the stats-collect project source tree root directory.

    Returns:
        Path to the project source tree root directory.
    """

    return Path(__file__).parent.parent.resolve()

def get_test_data_base() -> Path:
    """
    Return the path to the test data base directory.

    Returns:
        Path to the test data base directory.
    """

    return get_prj_src_path() / "tests" / "data"

def get_pman(hostspec: str, username: str = "") -> ProcessManagerType:
    """
    Create and return a process manager for the specified host.

    Args:
        hostspec: The hostname to create a process manager for. Use 'localhost' for the local host.
        username: Name of the user to use for logging into the remote host over SSH.

    Returns:
        A process manager instance: 'LocalProcessManager' for localhost, 'SSHProcessManager' for
        remote hosts.
    """

    return ProcessManager.get_pman(hostspec, username=username)

def build_params(pman: ProcessManagerType) -> CommonTestParamsTypedDict:
    """
    Build and return a dictionary containing common test parameters.

    Args:
        pman: The process manager object that defines the host where the tests will be run.

    Returns:
        A 'CommonTestParamsTypedDict' initialized with the hostname and process manager.
    """

    return {"hostname": pman.hostname, "pman": pman}
