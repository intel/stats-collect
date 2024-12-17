# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the capability of building 'pandas.DataFrames' out of raw turbostat statistics files.
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import TurbostatParser

TOTALS_SNAME = "Totals"

def get_col_scope(colname):
    """
    Return the scope name of 'pandas.DataFrame' column. The arguments are as follows.
      * colname - name of the column to return the scope name for.

    Return 'None' if 'colname' does not apply to a single scope.
    """

    split = colname.split("-")
    if len(split) == 1:
        return None
    return split[0]

class TurbostatDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    Provides the capability of building a 'pandas.DataFrames' out of raw turbostat statistics files.
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
        for metric, value in tstat.items():
            colprefix = TOTALS_SNAME if totals else f"CPU{self._cpunum}"
            colname = f"{colprefix}-{metric}"
            self.col2metric[colname] = metric
            renamed_tstat[colname] = value

        return renamed_tstat

    def _extract_totals(self, tstat):
        """Extract the 'totals' data from the 'tstat' dictionary."""

        totals_tstat = tstat["totals"]

        tdpsum = tstat["nontable"]["TDP"] * tstat["pkg_count"]

        # Add the 'PkgWatt%TDP' column which contains package power (from the 'PkgWatt' turbostat
        # column) as a percentage of TDP (from the turbostat header).
        totals_tstat["PkgWatt%TDP"] = (totals_tstat["PkgWatt"] / tdpsum) * 100.0
        return self._add_tstat_scope(totals_tstat, totals=True)

    def _extract_cpu(self, tstat):
        """
        Get a dictionary containing the turbostat statistics for the measured CPU. The dictionary
        contains values from the package, core, and CPU levels.
        """

        cpunum = str(self._cpunum)

        # Traverse dictionary looking for measured CPUs.
        for package in tstat["packages"].values():
            for core in package["cores"].values():
                if cpunum not in core["cpus"]:
                    continue

                # Include the package and core totals as for metrics which are not available at the
                # CPU level.
                return self._add_tstat_scope({**package["totals"], **core["totals"],
                                              **core["cpus"][cpunum]})

        raise Error(f"no data for measured CPU '{self._cpunum}'")

    def _turbostat_to_df(self, tstat):
        """
        Convert the 'tstat' dictionary to a 'pandas.DataFrame'. Arguments are as follows:
         * tstat - dictionary produced by 'TurbostatParser'.
        """

        new_tstat = self._extract_totals(tstat)
        if self._cpunum is not None:
            new_tstat.update(self._extract_cpu(tstat))

        return pandas.DataFrame.from_dict(new_tstat)

    def _read_stats_file(self, path):
        """
        Return a 'pandas.DataFrame' containing the data stored in the raw turbostat statistics file
        at path 'path'.
        """

        parser = TurbostatParser.TurbostatParser(path, derivatives=True)
        generator = parser.next()

        try:
            # Try to read the first data point from raw statistics file.
            parsed_dp = next(generator)
        except StopIteration:
            raise Error(f"empty or incorrectly formatted 'turbostat' statistics file "
                        f"'{path}") from None

        # Initialise 'sdf' with the first datapoint in the raw statistics file.
        sdf = self._turbostat_to_df(parsed_dp)

        # Add the rest of the data from the raw turbostat statistics file to 'sdf'.
        for parsed_dp in generator:
            df = self._turbostat_to_df(parsed_dp)
            sdf = pandas.concat([sdf, df], ignore_index=True)

        return sdf

    def __init__(self, cpunum=None):
        """
        The class constructor. The arguments are as follows.
          * cpunum - the measured CPU number.

        Note, the constructor does not load the potentially huge test result data into the memory.
        The data are loaded "on-demand" by 'load_df()'.
        """

        self._cpunum = cpunum

        # A dictionary mapping 'pandas.DataFrame' column names (built by 'load_df()') to the
        # corresponding turbostat metric name. E.g., column "Totals-CPU%c1" will be mapped to
        # 'CPU%c1'.
        self.col2metric = {}

        super().__init__("Time")
