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

TOTALS_SNAME = "Totals"

def get_col_scope(colname):
    """
    Return the scope name of 'colname', returns 'None' if 'colname' does not apply to a single
    scope.
    """

    split = colname.split("-")
    if len(split) == 1:
        return None
    return split[0]

class TurbostatDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    This class provides the capability of building a 'pandas.DataFrames' out of raw turbostat
    statistics files.
    """

    def _add_tstat_scope(self, tstat, totals=False):
        """
        The 'tstat' dictionary contains the turbostat statistics for a particular scope (e.g. for
        a specific CPU or a summary of the whole system). Add that scope to the keys in the
        dictionary. Arguments are as follows:
         * tstat - a dictionary containing the turbostat statistics.
         * totals - a boolean indicating whether the 'tstat' dictionary contains totals data.
        """

        renamed_tstat = {self._time_metric: [tstat["Time_Of_Day_Seconds"]]}
        for rawname, value in tstat.items():
            colprefix = TOTALS_SNAME if totals else f"CPU{self._mcpu}"
            colname = f"{colprefix}-{rawname}"
            self.col2rawnames[colname] = rawname
            renamed_tstat[colname] = value

        return renamed_tstat

    def _extract_totals(self, tstat):
        """Extract the 'totals' data from the 'tstat' dictionary."""

        totals_tstat = tstat["totals"]

        # Note: on multi-socket systems, this is the sum of TDP across sockets (packages).
        tdp = tstat["nontable"]["TDP"]

        # Add the 'PkgWatt%TDP' column which contains package power (from the 'PkgWatt' turbostat
        # column) as a percentage of TDP (from the turbostat header).
        totals_tstat["PkgWatt%TDP"] = (totals_tstat["PkgWatt"] / tdp) * 100.0
        return self._add_tstat_scope(totals_tstat, totals=True)

    def _extract_cpu(self, tstat):
        """
        Get a dictionary containing the turbostat statistics for the measured CPU. The dictionary
        contains values from the package, core, and CPU levels.
        """

        mcpu = str(self._mcpu)

        # Traverse dictionary looking for measured CPUs.
        for package in tstat["packages"].values():
            for core in package["cores"].values():
                if mcpu not in core["cpus"]:
                    continue

                # Include the package and core totals as for metrics which are not available at the
                # CPU level.
                return self._add_tstat_scope({**package["totals"], **core["totals"],
                                              **core["cpus"][mcpu]})

        raise Error(f"no data for measured CPU '{self._mcpu}'")

    def _turbostat_to_df(self, tstat):
        """
        Convert the 'tstat' dictionary to a 'pandas.DataFrame'. Arguments are as follows:
         * tstat - dictionary produced by 'TurbostatParser'.
        """

        new_tstat = self._extract_totals(tstat)
        if self._mcpu is not None:
            new_tstat.update(self._extract_cpu(tstat))

        return pandas.DataFrame.from_dict(new_tstat)

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw turbostat statistics file
        at 'path'.
        """

        parser = TurbostatParser.TurbostatParser(path).next()

        try:
            # Try to read the first data point from raw statistics file.
            parsed_dp = next(parser)
        except StopIteration:
            raise Error("empty or incorrectly formatted turbostat raw statistics file") from None

        # Initialise 'sdf' with the first datapoint in the raw statistics file.
        sdf = self._turbostat_to_df(parsed_dp)

        # Add the rest of the data from the raw turbostat statistics file to 'sdf'.
        for parsed_dp in parser:
            df = self._turbostat_to_df(parsed_dp)
            sdf = pandas.concat([sdf, df], ignore_index=True)

        return sdf

    def __init__(self, mcpu=None):
        """
        The class constructor. The arguments are as follows:
          * mcpu - the measured CPU number.

        Note, the constructor does not load the potentially huge test result data into the memory.
        The data are loaded "on-demand" by 'load_df()'.
        """

        self._mcpu = mcpu

        # Expose the mapping between "column names" which are the names used in the
        # 'pandas.DataFrame' and "raw names" which are the names used in raw turbostat statistic
        # files.
        self.col2rawnames = {}

        super().__init__("Time")
