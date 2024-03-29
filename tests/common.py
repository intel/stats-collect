# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""Common bits for the 'stats-collect' tests."""

import os
from pathlib import Path
from pepclibs.helperlibs import TestRunner
from statscollecttools import _StatsCollect, ToolInfo

def run_stats_collect(arguments, exp_exc=None):
    """
    Run stats-collect command and verify the outcome. The arguments are as follows.
      * arguments - the arguments to run the command with, e.g. 'report -o tmpdir'.
      * exp_exc - the expected exception, by default, any exception is considered to be a failure.
                  But when set if the command did not raise the expected exception then the test is
                  considered to be a failure.
    """

    # Set the environment variable to force the tester to use the data files of
    # the 'stats-collect' installation being tested.
    os.environ["STATS_COLLECT_DATA_PATH"] = str(Path(__file__).parents[1])
    TestRunner.run_tool(_StatsCollect, ToolInfo.TOOLNAME, arguments, exp_exc=exp_exc)
