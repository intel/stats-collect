# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of building 'pandas.DataFrames' out of raw turbostat statistics
files.
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import TurbostatParser

TOTALS_SCOPE = "Totals"

def decode_colname(colname):
    """Decode 'colname' into a tuple of (scope, rawname)."""

    split = colname.split("-")
    if len(split) == 1:
        return None, split[0]
    return split[0], split[1]

class TurbostatDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    This class provides the capability of building a 'pandas.DataFrames' out of raw turbostat
    statistics files.
    """

    def _encode_tstat(self, tstat, totals=False):
        """
        Encode the keys of the 'tstat' dictionary so that the resultant 'pandas.DataFrame' can
        contain data for totals data and one or more CPUs. Arguments are as follows:
         * tstat - the dictionary containing the turbostat statistics which should be encoded.
         * totals - a boolean indicating whether the 'tstat' dictionary contains totals data and
                    should be encoded as such.
        """

        encoded_tstat = {self._time_metric: [tstat["Time_Of_Day_Seconds"]]}
        for rawname, value in tstat.items():
            colprefix = TOTALS_SCOPE if totals else f"CPU{self._mcpu}"
            colname = f"{colprefix}-{rawname}"
            self.colnames[colname] = rawname
            encoded_tstat[colname] = value

        return encoded_tstat

    def _extract_totals(self, tstat):
        """Extract the 'totals' data from the 'tstat' dictionary."""

        totals_tstat = tstat["totals"]

        # Note: on multi-socket systems, this is the sum of TDP across sockets (packages).
        tdp = tstat["nontable"]["TDP"]

        # Add the 'PkgWatt%TDP' column which contains package power (from the 'PkgWatt' turbostat
        # column) as a percentage of TDP (from the turbostat header).
        totals_tstat["PkgWatt%TDP"] = (totals_tstat["PkgWatt"] / tdp) * 100.0
        return self._encode_tstat(totals_tstat, totals=True)

    def _extract_cpu(self, tstat):
        """
        Get a dictionary containing the turbostat statistics for the measured CPU. The dictionary
        contains values from the package, core, and CPU levels.
        """

        # Traverse dictionary looking for measured CPUs.
        for package in tstat["packages"].values():
            for core in package["cores"].values():
                if self._mcpu not in core["cpus"]:
                    continue

                # Include the package and core totals as for metrics which are not available at the
                # CPU level.
                return self._encode_tstat({**package["totals"], **core["totals"],
                                           **core["cpus"][self._mcpu]})

        raise Error(f"no data for measured cpu '{self._mcpu}'")

    def _turbostat_to_df(self, tstat):
        """
        Convert the 'tstat' dictionary to a 'pandas.DataFrame'. Arguments are as follows:
         * tstat - dictionary produced by 'TurbostatParser'.
        """

        new_tstat = self._extract_totals(tstat)
        if self._mcpu:
            new_tstat.update(self._extract_cpu(tstat))

        return pandas.DataFrame.from_dict(new_tstat)

    def _read_stats_file(self, path, labels=None):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw turbostat statistics file
        at 'path'.
        """

        try:
            tstat_gen = TurbostatParser.TurbostatParser(path).next()

            # Use the first turbostat snapshot to see which hardware and requestable C-states the
            # platform under test has.
            tstat = next(tstat_gen)

            # Initialise the stats 'pandas.DataFrame' ('sdf') with data from the first 'tstat'
            # dictionary.
            sdf = self._turbostat_to_df(tstat)

            # Add the rest of the data from the raw turbostat statistics file to 'sdf'.
            for tstat in tstat_gen:
                df = self._turbostat_to_df(tstat)
                sdf = pandas.concat([sdf, df], ignore_index=True)
        except Exception as err:
            msg = Error(err).indent(2)
            raise Error(f"error reading raw statistics file '{path}':\n{msg}.") from None

        # Confirm that the time column is in the 'pandas.DataFrame'.
        if self._time_metric not in sdf:
            raise Error(f"timestamps could not be parsed in raw statistics file '{path}'.")

        if labels:
            self._apply_labels(sdf, labels)

        # Convert 'Time' column from time since epoch to time since first data point was recorded.
        sdf[self._time_metric] = sdf[self._time_metric] - sdf[self._time_metric].iloc[0]
        sdf[self._time_metric] = pandas.to_datetime(sdf[self._time_metric], unit="s")

        return sdf

    def __init__(self, mcpu=None):
        """
        The class constructor.

        Note, the constructor does not load the potentially huge test result data into the memory.
        The data are loaded "on-demand" by 'load_df()'. Arguments are as follows:
         * mcpu - the name of the measured CPU for which data should be extracted from the raw
                  turbostat statistics file.
        """

        self._mcpu = mcpu

        # Expose the mapping between "raw names" which are the names used in raw turbostat statistic
        # files and "column names" which are the names used in the 'pandas.DataFrame'.
        self.colnames = {}

        super().__init__("Time")
