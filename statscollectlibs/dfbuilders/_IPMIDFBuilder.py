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
from statscollectlibs.defs import IPMIDefs
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import IPMIParser

class IPMIDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    Provide the capability of building a 'pandas.DataFrames' object out of IPMI statistics files.
    """

    def split_colname(self, colname):
        """
        Split column name and return a tuple of category name, metric name. The arguments are as
        follows.
          * colname - the dataframe column name to decode.
        """

        split = colname.split("-", 1)
        if len(split) < 2:
            return None, colname
        if split[0] not in self._defs.info:
            raise Error(f"BUG: unknown IPMI categorey '{split[0]}")

        return split[0], split[1]

    def _get_metric2colname(self, parsed_dp):
        """
        Build and return the metric name -> column name dictionary. The dictionary keys are metric
        names from the 'parsed_dp' dictionary (yielded by 'IPMIParser'). The values are the
        dataframe column names.

        The column names are basically metric names prefixed with the category name. For example, if
        metric "Fan1" is from the 'FanSpeed' category, its column name is going to be
        "FanSpeed-Fan1".
        """

        metric2colname = {}

        for metric, val in parsed_dp.items():
            unit = val[1]
            category = self._defs.get_category(unit)
            if category:
                metric2colname[metric] = f"{category}-{metric}"

        return metric2colname

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

        parser = IPMIParser.IPMIParser(path).next()

        try:
            # Read the first data point from raw statistics file.
            parsed_dp = next(parser)
        except StopIteration as err:
            errmsg = Error(err).indent(2)
            raise Error(f"empty or incorrectly formatted IPMI raw statistics file:\n"
                        f"{errmsg}") from err

        # The first data point is used to determine the raw IPMI metric names.
        metric2colname = self._get_metric2colname(parsed_dp)

        sdf = self._ipmi_to_df(parsed_dp)

        # Exclude the metrics that do not have the category, except for the timestamp.
        metric2colname["timestamp"] = self._time_metric
        for metric in sdf.columns:
            if metric not in metric2colname:
                sdf = sdf.drop(columns=[metric,])

        # Add the rest of the data from the raw IPMI statistics file to 'sdf'.
        for parsed_dp in parser:
            df = self._ipmi_to_df(parsed_dp, include_metrics=metric2colname)
            sdf = pandas.concat([sdf, df], ignore_index=True)

        sdf = sdf.rename(columns=metric2colname)
        return sdf

    def __init__(self):
        """The class constructor."""

        self._defs = IPMIDefs.IPMIDefs()

        super().__init__("Time")
