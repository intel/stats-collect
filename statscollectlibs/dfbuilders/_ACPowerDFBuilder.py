# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the capability of building a 'pandas.DataFrame' object out of a raw AC Power statistics
file.
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.dfbuilders import _DFBuilderBase

class ACPowerDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    Provide the capability of building a 'pandas.DataFrame' object out of a raw AC Power statistics
    file.
    """

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' object containing the data stored in the raw AC Power
        statistics CSV file at 'path'.
        """

        try:
            # 'skipfooter' parameter only available with Python the pandas engine.
            df = pandas.read_csv(path, skipfooter=1, engine="python", dtype="float64")
        except (pandas.errors.ParserError, ValueError) as err:
            # Failed 'dtype' conversion can cause 'ValueError', otherwise most parsing exceptions
            # are of type 'pandas.errors.ParserError'.
            msg = Error(err).indent(2)
            raise Error(f"unable to parse CSV '{path}':\n{msg}.") from err

        if "T" not in df.columns:
            raise Error(f"the 'T' (time-stamp) column was not found in AC power CSV file '{path}")

        # Add the 'TImeElapsed' column for the time elapsed since the beginning of measurements.
        df[self._time_metric] = df["T"] - df["T"].iloc[0]
        return df

    def __init__(self):
        """The class constructor."""

        self._time_metric = "TimeElapsed"
        super().__init__("T", self._time_metric)
