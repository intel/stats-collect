# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Common bits for the tests."""

import os
from pathlib import Path
from pepclibs.helperlibs import TestRunner
from statscollecttools import _StatsCollect, ToolInfo

def run_stats_collect(arguments: str, exp_exc: Exception | None = None):
    """
    Run 'stats-collect' command and verify the outcome.

    Args:
      arguments: The arguments to run the command with.
      exp_exc (Exception, optional): The expected exception. By default, any exception is 
        considered to be a failure. If set, the test is considered to be a failure if the 
        command did not raise the expected exception.
    """

    # Set the environment variable to force the tester to use the data files of
    # the 'stats-collect' installation being tested.
    os.environ["STATS_COLLECT_DATA_PATH"] = str(Path(__file__).parents[1])
    TestRunner.run_tool(_StatsCollect, ToolInfo.TOOLNAME, arguments, exp_exc=exp_exc)
