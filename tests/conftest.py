# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This pytest configuration file adds fixtures for 'stats-collect' pytests."""

from pathlib import Path
import pytest

@pytest.fixture
def data_path():
    """Returns a path to the 'testdata' directory."""

    testsdir = Path(__file__).parent.resolve() # pylint: disable=no-member
    return  testsdir / "testdata"
