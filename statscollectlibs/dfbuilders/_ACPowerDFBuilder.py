# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the capability of building a 'pandas.DataFrame' object out of a raw AC Power statistics
file.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.mdc import ACPowerMDC

class ACPowerDFBuilder:
    """
    Provide the capability of building a 'pandas.DataFrame' object out of a raw AC Power statistics
    file.
    """

    def __init__(self):
        """The class constructor."""

        self.mdo = ACPowerMDC.ACPowerMDC()

        # Name of the dataframe column containing the time since the epoch time-stamps.
        self.ts_colname = "T"
        # Name of the dataframe column containing the time elapsed since the beginning of the
        # measurements.
        self.time_colname = "TimeElapsed"

    def build_df(self, path: Path) -> pandas.DataFrame:
        """
        Build the AC power statistics dataframe from the raw statistics file.

        Args:
            path: The file path to the raw AC power statistics file.

        Returns:
            pandas.DataFrame: A DataFrame containing the data from the AC power statistics file.
        """

        # Read only the columns defined in the MDC.
        usecols = [metric for metric in self.mdo.mdd if metric != self.time_colname]

        try:
            # The 'skipfooter' parameter only available with the "python" engine.
            df = pandas.read_csv(path, skipfooter=1, engine="python", dtype="float64",
                                 usecols=usecols)
        except (pandas.errors.ParserError, ValueError) as err:
            # Failed 'dtype' conversion can cause 'ValueError', otherwise most parsing exceptions
            # are of type 'pandas.errors.ParserError'.
            msg = Error(str(err)).indent(2)
            raise Error(f"Unable to parse CSV '{path}':\n{msg}.") from err

        if self.ts_colname not in df.columns:
            raise Error(f"The '{self.ts_colname}' (time-stamp) column was not found in AC power "
                        f"CSV file '{path}")

        # Add the 'TImeElapsed' column for the time elapsed since the beginning of measurements.
        df[self.time_colname] = df[self.ts_colname] - df[self.ts_colname].iloc[0]

        return df
