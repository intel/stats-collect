# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the capability of building a 'pandas.DataFrames' object out of IPMI statistics files.

Terminology.
  * column name - the dataframe column name.
  * metric name - name of the IPMI metric as per the raw IPMI statistics file.
  * category - the metric category (e.g., "Temperature"). Column names are constructed as
               "category, dash, metric name".
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.mdc import IPMIMDC
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import IPMIParser

class IPMIDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    Provide the capability of building a 'pandas.DataFrames' object out of IPMI statistics files.
    """

    @staticmethod
    def _ipmi_to_df(parsed_dp, include_metrics=None):
        """
        Convert an 'IPMIParser' datapoint dictionary to a 'pandas.DataFrame' object.
        """

        def _reduce_dp():
            """
            Reduce the parsed IPMI datapoint dictionary to only include metrics in
            'include_metrics'.
            """

            for metric, pair in parsed_dp.items():
                val = pair[0]
                if val is None:
                    # If "no reading" is parsed in a line of a raw IPMI file, 'None' is returned. In
                    # this case, we should exclude that IPMI metric.
                    continue
                if include_metrics and metric not in include_metrics:
                    continue
                yield metric, val

        reduced_dp = {metric:[val] for metric, val in _reduce_dp()}
        return pandas.DataFrame.from_dict(reduced_dp)

    def _read_stats_file(self, path):
        """
        Return a 'pandas.DataFrame' object containing the data stored in the raw IPMI statistics
        file at 'path'.
        """

        parser = IPMIParser.IPMIParser(path, derivatives=True).next()

        try:
            # Read the first data point from raw statistics file.
            parsed_dp = next(parser)
        except StopIteration as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"empty or incorrectly formatted IPMI raw statistics file:\n"
                        f"{errmsg}") from err

        self.mdo = IPMIMDC.IPMIMDC(parsed_dp)

        include_metrics = set(self.mdo.mdd.keys())

        sdf = self._ipmi_to_df(parsed_dp, include_metrics=include_metrics)

        # Add the rest of the data from the raw IPMI statistics file to 'sdf'.
        for parsed_dp in parser:
            df = self._ipmi_to_df(parsed_dp, include_metrics=include_metrics)
            sdf = pandas.concat([sdf, df], ignore_index=True)

        return sdf

    def __init__(self):
        """The class constructor."""

        self.mdo: IPMIMDC.IPMIMDC | None = None
        super().__init__("timestamp", "TimeElapsed")
