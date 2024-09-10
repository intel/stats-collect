# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of building 'pandas.DataFrames' out of IPMI statistics files.
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.defs import IPMIDefs
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import IPMIParser

class IPMIDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    This class provides the capability of building a 'pandas.DataFrames' out of raw IPMI statistics
    files.
    """

    def decode_ipmi_colname(self, colname):
        """
        IPMI 'pandas.DataFrames' are loaded with column names containing the "rawname" which refers
        to the original name used in the raw IPMI statistics file and the relevant IPMI metric
        (which represents a category of IPMI statistics, e.g. "FanSpeed", "Power", etc.). Decode
        'colname' to get a tuple containing the metric and the raw IPMI name. If 'colname' is not a
        valid 'ipmi' column name, returns 'None, None'.
        """

        split = colname.split("-", 1)
        if len(split) < 2 or split[0] not in self._defs.info:
            return None, None

        rawname = split[1] if len(split) > 1 else None
        return split[0], rawname

    def _encode_colnames(self, ipmi):
        """
        Encode column names in the IPMIParser dict 'ipmi' to include the metrics they represent. For
        example, 'FanSpeed' can be represented by several columns such as 'Fan1'. This function will
        encode that column name as 'FanSpeed-Fan1'. Returns a dictionary in the format
        '{rawname: encoded_colname}' where 'rawname' represents the name used in the raw IPMI file
        and 'encoded_colname' is the name including the metric name as well as the rawname.
        """

        colnames = {}

        for colname, val in ipmi.items():
            unit = val[1]
            metric = self._defs.get_metric_from_unit(unit)
            if metric:
                colnames[colname] = f"{metric}-{colname}"

        return colnames

    @staticmethod
    def _ipmi_to_df(ipmi):
        """Convert IPMIParser dict to 'pandas.DataFrame'."""

        # Reduce IPMI values from ('value', 'unit') to just 'value'.
        # If "no reading" is parsed in a line of a raw IPMI file, 'None' is returned. In this
        # case, we should exclude that IPMI metric.
        i = {k:[v[0]] for k, v in ipmi.items() if v[0] is not None}
        return pandas.DataFrame.from_dict(i)

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw IPMI statistics file at
        'path'.
        """

        parser = IPMIParser.IPMIParser(path).next()

        try:
            # Try to read the first data point from raw statistics file.
            parsed_dp = next(parser)
        except StopIteration:
            raise Error("empty or incorrectly formatted IPMI raw statistics file") from None

        # The first data point is used to determine the column names of the 'pandas.DataFrame'. The
        # column names will include the raw names used in the raw IPMI statistics file as well as
        # the metric category they belong to such as "FanSpeed", "Temperature" etc. See
        # 'self._encode_colnames()' for more information.
        renaming_cols = self._encode_colnames(parsed_dp)

        # Initialise 'sdf' with the first datapoint in the raw statistics file.
        sdf = self._ipmi_to_df(parsed_dp)

        # Add the rest of the data from the raw IPMI statistics file to 'sdf'.
        for parsed_dp in parser:
            df = self._ipmi_to_df(parsed_dp)
            sdf = pandas.concat([sdf, df], ignore_index=True)

        # The timestamps will be converted to represent time elapsed since the beginning of the
        # statistics collection, therefore rename the 'timestamp' column to 'self._timecolname'
        # which represents this better.
        renaming_cols["timestamp"] = self._time_metric
        sdf = sdf.rename(columns=renaming_cols)

        return sdf

    def __init__(self):
        """
        The class constructor.

        Note, the constructor does not load the potentially huge test result data into the memory.
        The data are loaded "on-demand" by 'load_df()'.
        """

        self._defs = IPMIDefs.IPMIDefs()

        super().__init__("Time")
