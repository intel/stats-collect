# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module contains the tests for the 'stats-collect report' command."""

import common

def test_good_input_data(tmpdir, data_path):
    """Test 'report' command for good input data."""

    good_data_path = data_path / "good"
    args = f"report -o {tmpdir} {good_data_path}"
    common.run_stats_collect(args)