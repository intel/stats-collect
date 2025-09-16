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

import typing
from pathlib import Path
import pandas
from pepclibs.helperlibs import Logging, Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.dfbuilders import _DFHelpers
from statscollectlibs.parsers import InterruptsParser
from statscollectlibs.mdc import InterruptsMDC

if typing.TYPE_CHECKING:
    from statscollectlibs.parsers.InterruptsParser import DataSetTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class InterruptsDFBuilder:
    """
    Parse raw interrupt statistics file and build a dataframe.
    """

    def __init__(self, cpus: list[int] | None = None):
        """
        Initialize the class instance.

        Args:
            cpus: CPU numbers to include in the dataframe. If 'None', do not include any individual
                  CPU columns in the dataframe.
        """

        self._cpus = cpus

        self.mdo: InterruptsMDC.InterruptsMDC | None = None

        # Number of "numerical" interrupts per scope to include. There are many interrupts, but the
        # idea is to include only the most frequent ones. "Numerical" means interrupts referred to
        # with a number from '/proc/interrupts'. Non-numerical interrupts are referred to by name
        # (e.g., 'LOC' or 'NMI').
        self._irqs_limit = 6

        # Name of the dataframe column containing the time since the epoch time-stamps.
        self.ts_colname = "Timestamp"
        # Name of the dataframe column containing the time elapsed since the beginning of the
        # measurements.
        self.time_colname = "TimeElapsed"

        self.time_colnames = [self.time_colname, self.ts_colname]

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

        # These are initialized in 'build_df()'.
        self._path: Path
        self._data: list[list[int | float]]
        self._first_ts: float | None

    def _get_totals(self, dataset: DataSetTypedDict, sname: str) -> dict[str, int]:
        """
        Calculate and return the total number of interrupts.

        Args:
            dataset: The dataset containing the interrupt counters.
            sname: The scope to calculate the total number of interrupts for.

        Returns:
            dict[str, int]: A dictionary containing the total counts:
              * "Total": The sum of all interrupts.
              * "Total_IRQ": The sum of "IRQ*" interrupts.
              * "Total_XYZ": The sum of non-"IRQ*" interrupts.
        """

        irq_cpu = None
        if sname.startswith("CPU"):
            irq_cpu = int(sname[3:])
        elif sname != "System":
            raise Error(f"BUG: unsupported scope '{sname}'") from None

        total_irqs = 0
        total_xyz = 0

        for cpu, irqs_info in dataset["cpu2irqs"].items():
            if irq_cpu is not None and irq_cpu != cpu:
                continue

            for irqname, cnt in irqs_info.items():
                if irqname.startswith("IRQ"):
                    total_irqs += cnt
                else:
                    total_xyz += cnt

        return {self._total_metric: total_irqs + total_xyz,
                self._total_irq_metric: total_irqs,
                self._total_xyz_metric: total_xyz}

    def _add_dataset(self,
                     dataset: DataSetTypedDict,
                     irq_colnames: list[str],
                     no_data_colnames: list[str]):
        """
        Add a dataset to 'self._data', a temporary dictionary storing all data before building the
        dataframe. The dictionary structure is: "{ index: dataline }", where 'index' is the
        dataframe row index, and 'dataline' is a list containing values for the timestamps and every
        column name in 'irq_colnames'. Here is a list structure example:

            [ TimeElapsed value, Timestamp value,
              System-IRQa value, System-IRQb value, ...,
              CPUx-IRQc value, CPUx-IRQc value, ...
              System-Total, System-Total_IRQ, System-Total_XYZ ]

        Args:
            dataset: Parsed dataset to add.
            irq_colnames: Non-time dataframe column names to include.
            no_data_colnames: Non-time dataframe column names to include, but do not have data yet.
                              Use 0 for the values.
        """

        if "timestamp" not in dataset:
            raise Error("BUG: missing 'timestamp' in the parsed dataset") from None

        if self._first_ts is None:
            self._first_ts = dataset["timestamp"]

        totals: dict[str, dict[str, int]] = {}
        data: list[int | float] = [dataset["timestamp"] - self._first_ts, dataset["timestamp"]]

        # Calculate and add the interrupts for every column in 'irq_colnames'.
        for colname in irq_colnames:
            sname, irqname = _DFHelpers.split_colname(colname)
            if not sname:
                continue

            if irqname.startswith("Total"):
                if sname not in totals:
                    totals[sname] = self._get_totals(dataset, sname)
                data.append(totals[sname][irqname])
                continue

            if sname == "System":
                sum_all_cpus = 0
                for irqs_info in dataset["cpu2irqs"].values():
                    sum_all_cpus += irqs_info.get(irqname, 0)
                data.append(sum_all_cpus)
            elif sname.startswith("CPU"):
                data.append(dataset["cpu2irqs"][int(sname[3:])][irqname])
            else:
                raise Error(f"BUG: unsupported scope '{sname}' in column name "
                            f"'{colname}'") from None

        data += [0] * len(no_data_colnames)
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
        for cpu, irqs_info in first_ds["cpu2irqs"].items():
            for irqname, cnt in irqs_info.items():
                if cpu not in last_ds["cpu2irqs"]:
                    _LOG.warning("CPU '%d' is present in the first '/proc/interrupts' snapshot, "
                                 "but missing in the last one in file '%s'. Skipping CPU%d.",
                                 cpu, self._path, cpu)
                    continue
                if irqname not in last_ds["cpu2irqs"][cpu]:
                    _LOG.warning("Interrupt '%s' is present in the first "
                                 "'/proc/interrupts' snapshot, but missing in the last one in "
                                 "file '%s'. Skipping %s.", irqname, self._path, irqname)
                    continue
                if irqname not in irqs:
                    irqs[irqname] = 0

                irqs[irqname] += last_ds["cpu2irqs"][cpu][irqname] - cnt

        colnames += [f"System-{self._total_metric}", f"System-{self._total_irq_metric}",
                     f"System-{self._total_xyz_metric}"]
        colnames += self._fetch_hottest_irqs(irqs, "System")

        if self._cpus is None:
            return colnames

        for cpu in self._cpus:
            if cpu not in first_ds["cpu2irqs"] or cpu not in last_ds["cpu2irqs"]:
                raise Error(f"No data for CPU '{cpu}' found in interrupts statistics file "
                            f"'{self._path}") from None

            # Calculate how many interrupts of each type occurred.
            irqs = {}
            for irqname, cnt in first_ds["cpu2irqs"][cpu].items():
                irqs[irqname] = last_ds["cpu2irqs"][cpu][irqname] - cnt

            colnames += [f"CPU{cpu}-{self._total_metric}",
                         f"CPU{cpu}-{self._total_irq_metric}",
                         f"CPU{cpu}-{self._total_xyz_metric}"]
            colnames += self._fetch_hottest_irqs(irqs, f"CPU{cpu}")

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
            _, irqname = _DFHelpers.split_colname(colname)
            if irqname in dataset["irq_info"] or irqname in self._total_metrics_set:
                new_colnames.append(colname)

        return new_colnames

    def build_df(self, path: Path) -> pandas.DataFrame:
        """
        Build the interrupts statistics dataframe from the raw statistics file.

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

        irq_colnames = self._construct_irq_colnames()

        # IRQ rate colnames.
        irq_rate_colnames = [colname + "_rate" for colname in irq_colnames]

        # Construct the dataframe. Values for the 'no_data_colnames' columns will be 0, and they
        # will be filled with the actual data later, when the data is available.
        self._add_dataset(dataset, irq_colnames, no_data_colnames=irq_rate_colnames)
        for dataset in generator:
            self._add_dataset(dataset, irq_colnames, no_data_colnames=irq_rate_colnames)

        # The raw file is parsed, and all the data are in 'self._data'. Now build the dataframe.
        colnames = self.time_colnames + irq_colnames

        df = pandas.DataFrame(self._data, columns=colnames + irq_rate_colnames)

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
        intervals = df[self.time_colname].diff().fillna(0)

        # Add requests per second metrics.
        for colname, rate_colname in zip(irq_colnames, irq_rate_colnames):
            df[rate_colname] = df[colname] / intervals

        # Remove the first row, because it contains all zeros the column 'diff()' operation.
        df = df.iloc[1:]

        self._build_mdo(list(df.columns))
        return df

    def _build_mdo(self, colnames: list[str]):
        """
        Build the the Metrics Definition Object (MDO) based on dataframe column names.

        Args:
            colnames: The list of dataframe column names.
        """

        metrics = []
        metrics_set = set()
        for colname in colnames:
            _, metric = _DFHelpers.split_colname(colname)
            if metric not in metrics_set:
                metrics.append(metric)
                metrics_set.add(metric)

        self.mdo = InterruptsMDC.InterruptsMDC(metrics)
