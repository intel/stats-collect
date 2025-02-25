# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Parse raw interrupt statistics file and build a dataframe.
"""

from __future__ import annotations  # Remove when switching to Python 3.10+.

from pathlib import Path
from pandas import DataFrame
from pepclibs.helperlibs import Logging, Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import InterruptsParser
from statscollectlibs.parsers.InterruptsParser import DataSetTypedDict

_LOG = Logging.getLogger(f"stats-collect.{__name__}")

class InterruptsDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    Parse raw interrupt statistics file and build a dataframe.
    """

    def __init__(self, colnames: list[str] | None = None, cpunum: int | None = None):
        """
        Initialize the class instance.

        Args:
            colnames: List of column names to include in the dataframe. If 'None', column names are
                      automatically determined based on the most frequent interrupts.
            cpunum: CPU number to include in the dataframe. If 'None', do not include any individual
                    CPU columns in the dataframe.
        """

        self._cpunum = cpunum
        self.colnames = colnames

        # Number of "numerical" interrupts per scope to include. There are many interrupts, but the
        # idea is to include only the most frequent ones. "Numerical" means interrupts referred to
        # with a number from '/proc/interrupts'. Non-numerical interrupts are referred to by name
        # (e.g., 'LOC' or 'NMI').
        self._irqs_limit = 6

        self._ts_colname = "Timestamp"
        self._time_colname = "TimeElapsed"
        self._time_colnames = [self._time_colname, self._ts_colname]

        # Total number of all interrupts on all CPUs.
        self._total_metric = "Total"
        # Total number of all "IRQ<number>" sort of interrupts on all CPUs (the interrupts that have
        # an interrupt number in '/proc/interrupts').
        self._total_irq_metric = "Total_IRQ"
        # Total number of all "XYZ" sort of interrupts on all CPUs (the interrupts that do not have
        # an interrupt number in '/proc/interrupts', for example "LOC").
        self._total_xyz_metric = "Total_XYZ"

        self._total_metrics_set = {self._total_metric, self._total_irq_metric,
                                   self._total_xyz_metric}

        # These are initialized in '_read_stats_file()'.
        self._path: Path
        self._data: list[list[int | float]]
        self._first_ts: float | None
        self._irqcnt_colnames: list[str] # All 'self.colnames' columns, excluding time columns.

        super().__init__(self._ts_colname, self._time_colname)

    def _get_totals(self, dataset: DataSetTypedDict, scope: str) -> dict[str, int]:
        """
        Calculate and return the total number of interrupts.

        Args:
            dataset: The dataset containing the interrupt counters.
            scope: The scope to filter the interrupts. If it starts with "IRQ", it will filter by
                   CPU number.

        Returns:
            dict[str, int]: A dictionary containing the total counts:
                "Total": The sum of all interrupts.
                "Total_IRQ": The sum of "IRQ*" interrupts.
                "Total_XYZ": The sum of non-"IRQ*" interrupts.
        """

        cpunum = None
        if scope.startswith("IRQ"):
            cpunum = int(scope[3:])
        elif scope != "System":
            raise Error(f"BUG: unsupported scope '{scope}'") from None

        total_irqs = 0
        total_xyz = 0

        for cpu, irqs_info in dataset["cpus"].items():
            if cpunum is not None and cpunum != cpu:
                continue

            for irqname, cnt in irqs_info.items():
                if irqname.startswith("IRQ"):
                    total_irqs += cnt
                else:
                    total_xyz += cnt

        return {self._total_metric: total_irqs + total_xyz,
                self._total_irq_metric: total_irqs,
                self._total_xyz_metric: total_xyz}

    def _add_dataset(self, dataset: DataSetTypedDict, irq_colnames: list[str]):
        """
        Add a dataset to 'self._data', a temporary dictionary storing all data before building the
        dataframe. The dictionary structure is: "{ index: dataline }", where 'index' is the
        dataframe row index, and 'dataline' is a list containing values for timestamps, totals, and
        each column name in 'irq_colnames'. Here is a list structure example:

            [ TimeElapsed, Timestamp,
              System-IRQa, System-IRQb, ...,
              CPUx-IRQc, CPUx-IRQc, ...
              System-Total, System-Total_IRQ, System-Total_XYZ ]

        Args:
            dataset: Parsed dataset to add.
            irq_colnames: Non-time dataframe column names to include.
        """

        if "timestamp" not in dataset:
            raise Error("BUG: missing 'timestamp' in the parsed dataset") from None

        if self._first_ts is None:
            self._first_ts = dataset["timestamp"]

        totals: dict[str, int] | None = None
        data: list[int | float] = [dataset["timestamp"] - self._first_ts, dataset["timestamp"]]

        # Calculate and add the interrupts for every column in 'irq_colnames'.
        for colname in irq_colnames:
            scope, irqname = colname.split("-")

            if irqname.startswith("Total"):
                if totals is None:
                    totals = self._get_totals(dataset, scope)
                data.append(totals[irqname])
                continue

            if scope == "System":
                sum_all_cpus = 0
                for irqs_info in dataset["cpus"].values():
                    sum_all_cpus += irqs_info.get(irqname, 0)
                data.append(sum_all_cpus)
            elif scope.startswith("CPU"):
                data.append(dataset["cpus"][int(scope[3:])][irqname])
            else:
                raise Error(f"BUG: unsupported scope '{scope}' in column name "
                            f"'{colname}'") from None

        self._data.append(data)

    def _fetch_hottest_irqs(self, irqs: dict[str, int], scope: str) -> list[str]:
        """
        Fetch and return 'self._irqs_limit' number of "hottest" interrupts from the interrupts
        dictionary.  The "hottest" interrupts are those with the highest counter value (most
        frequent interrupts).

        Note, the "non-numbered" interrupts like "NMI" or "LOC" are always included, regardless of
        their "hotness". The assumption is that the "non-numbered" interrupts are always interesting
        or important.

        Args:
            irqs: Interrupts dictionary, where keys are interrupt names and values are the
                  numbers of interrupt occurrences.
            scope: Scope name to use for composing column names (e.g., System, CPU0, etc.).

        Returns:
            List of dataframe column names for the "hottest" "numerical" interrupts (e.g.,
            'System-IRQ87' or 'CPU0-IRQ5').
        """

        sorted_irqs = dict(sorted(irqs.items(), key=lambda item: item[1], reverse=True))

        colnames = []
        counter = 0
        for irqname, cnt in sorted_irqs.items():
            if counter >= self._irqs_limit or cnt == 0:
                break
            colnames.append(f"{scope}-{irqname}")
            if irqname.startswith("IRQ") and Trivial.is_int(irqname[3:]):
                counter += 1

        return colnames

    def _construct_irq_colnames(self) -> list[str]:
        """
        Construct the dataframe column names. Include all the necessary scopes, the totals, and
        the hottest interrupts.

        Returns:
            List of column names to include in the dataframe (all except for time columns).
        """

        colnames = []

        parser = InterruptsParser.InterruptsParser(self._path)
        first_ds, last_ds = parser.get_first_and_last()

        # Calculate how many interrupts of each type occurred for the System scope.
        irqs = {}
        for cpu, irqs_info in first_ds["cpus"].items():
            for irqname, cnt in irqs_info.items():
                if cpu not in last_ds["cpus"]:
                    _LOG.warning("CPU '%d' is present in the first '/proc/interrupts' snapshot, "
                                 "but missing in the last one in file '%s'. Skipping CPU%d.",
                                 cpu, self._path, cpu)
                    continue
                if irqname not in last_ds["cpus"][cpu]:
                    _LOG.warning("Interrupt '%s' is present in the first "
                                 "'/proc/interrupts' snapshot, but missing in the last one in "
                                 "file '%s'. Skipping %s.", irqname, self._path, irqname)
                    continue
                if irqname not in irqs:
                    irqs[irqname] = 0

                irqs[irqname] += last_ds["cpus"][cpu][irqname] - cnt

        colnames += [f"System-{self._total_metric}", f"System-{self._total_irq_metric}",
                     f"System-{self._total_xyz_metric}"]
        colnames += self._fetch_hottest_irqs(irqs, "System")

        if self._cpunum is not None:
            if self._cpunum not in first_ds["cpus"] or self._cpunum not in last_ds["cpus"]:
                raise Error(f"No data for CPU '{self._cpunum}' found in interrupts statistics file "
                            f"'{self._path}") from None

            # Calculate how many interrupts of each type occurred.
            irqs = {}
            for irqname, cnt in first_ds["cpus"][self._cpunum].items():
                irqs[irqname] = last_ds["cpus"][self._cpunum][irqname] - cnt

            colnames += [f"CPU{self._cpunum}-{self._total_metric}",
                         f"CPU{self._cpunum}-{self._total_irq_metric}",
                         f"CPU{self._cpunum}-{self._total_xyz_metric}"]
            colnames += self._fetch_hottest_irqs(irqs, f"CPU{self._cpunum}")

        return colnames

    def _get_existing_colnames(self, dataset: DataSetTypedDict, colnames: list[str]) -> list[str]:
        """
        Find and return the list of column names from 'colnames' present in 'dataset'.

        Args:
            dataset: Dataset to check for 'colnames' in.
            colnames: List of column names to check.

        Returns:
            List of column names from 'colnames' present in 'dataset'.
        """

        new_colnames = []

        for colname in colnames:
            _, irqname = colname.split("-")
            if irqname in dataset["irq_info"] or irqname in self._total_metrics_set:
                new_colnames.append(colname)

        return new_colnames

    def _read_stats_file(self, path: Path) -> DataFrame:
        """
        Parse the raw interrupt statistics file and build the dataframe.

        Args:
            path: Raw interrupts statistics file path.

        Returns:
            Pandas dataframe including the parsed interrupt statistics data.
        """

        self._path = path
        self._data = []
        self._first_ts = None

        parser = InterruptsParser.InterruptsParser(path)
        generator = parser.next()

        dataset = next(generator)

        colnames: list[str] # All column names to include in the dataframe.
        irq_colnames: list[str] # All non-time column names to include in the dataframe.

        if not self.colnames:
            self._irqcnt_colnames = self._construct_irq_colnames()
            irq_colnames = self._irqcnt_colnames
            self.colnames = self._time_colnames + self._irqcnt_colnames
        else:
            irq_colnames = self._get_existing_colnames(dataset, self._irqcnt_colnames)

        self._add_dataset(dataset, irq_colnames)

        for dataset in generator:
            self._add_dataset(dataset, irq_colnames)

        # The raw file is parsed, and all the data are in 'self._data'. Now build the dataframe.
        colnames = self._time_colnames + irq_colnames
        df = DataFrame(self._data, columns=colnames)

        # Drop the unneeded and potentially large 'self._data'.
        del self._data
        self._data = []

        # Interrupt counters are counts of serviced interrupts since the system has booted up. Turn
        # them into counts of interrupts serviced during the measurement interval. Ensure the type
        # is integer.
        #
        # The first row will end up with zeros (would be 'NaN's, but 'fillna(0)' turns them to
        # zeros). This is because the delta cannot be calculated for the first row.
        df[irq_colnames] = df[irq_colnames].diff().fillna(0).astype(int)

        # Calculate the measurement intervals.
        intervals = df[self._time_colname].diff().fillna(0)

        # Add requests per second metrics.
        for colname in irq_colnames:
            df[colname + "_rate"] = df[colname] / intervals

        # Remove the first row, because it contains all zeros.
        df = df.iloc[1:]

        return df
