# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Parse raw interrupts statistics, which may contain multiple snapshots of the "/proc/interrupts" file
contents separated by "timestamp: <time_since_epoch>" lines.
"""

from __future__ import annotations  # Remove when switching to Python 3.10+.

import itertools
import re
import os
from pathlib import Path
from typing import IO, Generator, Iterator, TypedDict, Sequence, Literal

from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat

# Regular expression to match timestamp lines in the input data.
_TIMESTAMP_REGEX = re.compile(r"^timestamp: (\d+\.\d+)$")

class IRQInfoTypedDict(TypedDict, total=False):
    """
    The IRQ information dictionary type.

    Attributes:
        irq_num: The interrupt number or special name, such as "NMI".
        chip_name: The interrupt chip name.
        hwirq: The platform-specific HW interrupt information, on x86 it is the HW interrupt number
               and type.
        action: The interrupt handler name.
    """

    irq_num: int | str
    chip_name: str | None
    hwirq: str | None
    action: str | None

class DataSetTypedDict(TypedDict, total=False):
    """
    The data set dictionary type yielded by the '_InterruptsParser' parser.

    Attributes:
        timestamp: Time since epoch when the '/proc/interrupts' snapshot was taken.
        cpu2irqs: A dictionary indexed by CPU numbers, where the values are dictionaries indexed by
                  IRQ names with the interrupt counts as values.
        irq_info: A dictionary indexed by IRQ names, where the values are dictionaries of type
                  'IRQInfoTypedDict'.
    """

    timestamp: float
    cpu2irqs: dict[int, dict[str, int]]
    irq_info: dict[str, IRQInfoTypedDict]

class InterruptsParser:
    """
    Parser for raw interrupts statistics, which may contain multiple snapshots of the
    "/proc/interrupts" file contents separated by "timestamp: <time_since_epoch>" lines.
    """

    def __init__(self, path: Path | None = None, lines: Iterator[str] | IO[str] | None = None):
        """
        Initialize a class instance. The arguments are as follows.

        Args:
            path: The path to the file containing the interrupts data.
            lines: An iterator or file object providing the lines of the interrupts data.
        """

        if path and lines:
            raise Error("Please specify either 'path' or 'lines', but not both")

        if not path and not lines:
            raise Error("Please specify either 'path' or 'lines'")

        if path:
            if not isinstance(path, Path):
                raise Error("Please provide a Path object for 'path'")
        elif not isinstance(lines, Iterator):
            raise Error("Please provide an iterator for 'lines'")

        self._path = path
        self._lines = lines

        # These are initialized in '_next()'. Just type hints here.
        self._probe_exception_msg: str | None
        self._timestamp: float
        self._dataset: DataSetTypedDict
        self._last_yielded_dataset: DataSetTypedDict
        self._cpu2irqs: dict[int, dict[str, int]]
        self._irq_info: dict[str, IRQInfoTypedDict]
        self._cpus: list[int]
        self._first_lines: list[str]
        self._yielded_cnt: int

    def _parse_timestamp(self, line: str) -> float | None:
        """
        Parse a (presumably) timestamp line.

        Args:
            line: The line to parse.

        Returns:
            If the line is a timestamp line, return the floating point timestamp value.
            Otherwise, return 'None'.
        """

        match = re.match(_TIMESTAMP_REGEX, line)
        if not match:
            return None

        return float(match[1])

    def _parse_header(self, line: str) -> list[int]:
        """
        Parse the header line of the "/proc/interrupts" table - it contains the CPU numbers.

        Args:
            line: The line to parse.

        Raises:
            ErrorBadFormat: Bad header format.

        Returns:
            The header elements.
        """

        cpus = []
        for elt in line.split():
            elt = elt.strip()
            if not elt.startswith("CPU"):
                raise ErrorBadFormat(f"Bad '/proc/interrupts' header element '{elt}': should start "
                                     f"with 'CPU'")
            cpu = Trivial.str_to_int(elt[len("CPU"):], what="CPU number")
            if cpu < 0:
                raise ErrorBadFormat(f"Bad '/proc/interrupts' header element '{elt}': negative CPU "
                                     f"number")
            cpus.append(cpu)

        return cpus

    def probe(self, lines: Iterator[str] | IO[str]) -> bool:
        """
        Check if the input data looks like raw interrupts statistics.

        Args:
            lines: The lines to probe.

        Raises:
            ErrorBadFormat: The input data is not raw interrupt statistics data.

        Returns:
            True if the input data looks like raw interrupt statistics data.
        """

        if self._probe_exception_msg is not None:
            raise ErrorBadFormat(self._probe_exception_msg)

        try:
            line1 = next(lines)
            line2 = next(lines)
        except StopIteration:
            self._probe_exception_msg = "Too short input (less than 2 lines)"
            raise ErrorBadFormat(self._probe_exception_msg) from None

        # The very first line must be a timestamp.
        timestamp = self._parse_timestamp(line1)
        if timestamp is None:
            self._probe_exception_msg = "Not '/proc/interrupts' data: expected timestamp at the " \
                                        "first line"
            raise ErrorBadFormat(self._probe_exception_msg)

        self._timestamp = timestamp

        # The second line must be the header.
        self._cpus = self._parse_header(line2)

        self._first_lines = [line1, line2]
        return True

    def _finalise_dataset(self):
        """
        Compose the final dataset from the parsed data in 'self._datadict'.
        """

        if not self._cpu2irqs:
            raise Error("BUG: No CPUs found in the interrupts statistics")
        if not self._irq_info:
            raise Error("BUG: No IRQs found in the interrupts statistics")

        self._dataset["cpu2irqs"] = self._cpu2irqs
        self._dataset["irq_info"] = self._irq_info

    def _parse_line(self, line: str) -> Generator[DataSetTypedDict, None, None]:
        """
        Parse a single line of the raw interrupts statistics file.

        Args:
            line: The line to parse.

        Yields:
            DataSetTypedDict: A dataset dictionary containing the parsed '/proc/interrupts'
            snapshot.
        """

        timestamp = self._parse_timestamp(line)
        if timestamp is not None:
            # A new dataset starts.
            self._timestamp = timestamp

            if not self._dataset:
                # This is the very first dataset.
                self._dataset = DataSetTypedDict(timestamp=self._timestamp)
                return

            self._finalise_dataset()
            yield self._dataset

            self._last_yielded_dataset = self._dataset
            self._yielded_cnt += 1

            self._dataset = DataSetTypedDict(timestamp=self._timestamp)
            self._cpu2irqs = {}
            self._irq_info = {}
        else:
            if line.startswith("CPU"):
                # This is the header line. Keep in mind that CPUs may go online/offline, which
                # adds/removes CPUs in '/proc/interrupt' snapshots. For this reason, it is necessary
                # to parse all header lines. Otherwise, it would be enough to parse only the first
                # one.
                self._cpus = self._parse_header(line)
                return

            # The last "Actions" column may contain spaces. Limiting the splits to the number of
            # columns ensures the "Actions" column is not split.
            elts = line.split(maxsplit=len(self._cpus) + 3 - 1)

            # Drop the trailing ":" symbol.
            irq_name = elts[0][:-1]

            if Trivial.is_int(irq_name):
                irq_name = f"IRQ{irq_name}"

            irq_counts = []
            for cpu, irq_cnt in zip(self._cpus, elts[1:]):
                cnt = Trivial.str_to_int(irq_cnt, what=f"{irq_name} count for CPU{cpu}")
                irq_counts.append(cnt)

            if len(irq_counts) != len(self._cpus):
                # There are special lines like "MIS" and "ERR", which count various sorts of
                # errors, and they do not have per-CPU counters. Extend the list with the same
                # counter value.
                cnt = irq_counts[-1]
                missing_cnt = len(self._cpus) + 1 - len(irq_counts)
                irq_counts.extend([cnt] * missing_cnt)

            for cpu, irqcnt in zip(self._cpus, irq_counts):
                if cpu not in self._cpu2irqs:
                    self._cpu2irqs[cpu] = {}
                self._cpu2irqs[cpu][irq_name] = irqcnt

            irq_num = elts[0][:-1]
            irq_infos: list[str | None] = [irq_num]
            for val in elts[len(self._cpus) + 1:]:
                irq_infos.append(val)

            # Sometimes one or more of the last 3 columns are missing. Pad the list with 'None's.
            #
            # TODO: a hack to silence mypy "literal-required" warnings. It might have been fixed in
            # newer # mypy so that the 'tuple' type is fine to use. Refer to
            # https://github.com/python/mypy/issues/7178
            keys: Sequence[Literal["irq_num", "chip_name", "hwirq", "action"]] = \
                                                        ("irq_num", "chip_name", "hwirq", "action")
            for _ in range(len(keys) - len(irq_infos)):
                irq_infos.append(None)

            self._irq_info[irq_name] = {}
            for key, val in zip(keys, irq_infos):
                self._irq_info[irq_name][key] = val

    def _next(self, lines: Iterator[str] | IO[str]) -> Generator[DataSetTypedDict, None, None]:
        """
        Yield dataset dictionaries corresponding to one snapshot of interrupts statistics.

        Args:
            lines: The lines to parse.

        Yields:
            DataSetTypedDict: A dataset dictionary containing the parsed '/proc/interrupts'
                              snapshot.

        Raises:
            ErrorBadFormat: The input data is not raw interrupt statistics data.
        """

        self._probe_exception_msg = None
        self._timestamp = 0.0
        self._dataset = {}
        self._cpu2irqs = {}
        self._irq_info = {}
        self._cpus = []
        self._first_lines = []
        self._last_yielded_dataset = {}
        self._yielded_cnt = 0

        self.probe(lines)

        if len(self._cpus) == 0:
            raise ErrorBadFormat("No CPUs found in the '/proc/interrupts' header")

        for line in itertools.chain(self._first_lines, lines):
            line = line.strip()

            if not line:
                # Skip empty lines.
                continue

            if line.startswith("#"):
                # Assume this is a comment.
                continue

            try:
                yield from self._parse_line(line)
            except ErrorBadFormat:
                if line == "stc-agent-proc-interrupts-helper: error: interrupted, exiting":
                    # This is the message from 'proc-interrupts-handler' when it is interrupted, and
                    # this indicates the end of the interrupts statistics.
                    break
                raise

        if self._yielded_cnt == 0:
            if not self._dataset.get("timestamp"):
                raise ErrorBadFormat("No 'timestamp:' lines found")
            if not self._cpu2irqs:
                raise ErrorBadFormat("No '/proc/interrupts' snapshots found")

        if self._cpu2irqs:
            self._finalise_dataset()
            # If the last dataset is incomplete, do not yield it.
            if self._yielded_cnt == 0:
                # No datasets yielded yet, can't really detect if the current one is cut or not,
                # just yield it.
                yield self._dataset
            else:
                last_irqname = list(self._last_yielded_dataset["irq_info"])[-1]
                if list(self._irq_info)[-1] == last_irqname:
                    yield self._dataset

    def next(self) -> Generator[DataSetTypedDict, None, None]:
        """
        Yield dictionaries of type 'DataSetTypedDict' corresponding to one snapshot of interrupts
        statistics at a time.

        Yields:
            Datasets of type 'DataSetTypedDict' containing the parsed '/proc/interrupts' snapshot.
        """

        if self._path:
            try:
                # pylint: disable=consider-using-with
                self._lines = open(self._path, "r", encoding="utf-8")
            except OSError as err:
                msg = Error(err).indent(2)
                raise Error(f"Failed to open '{self._path}':\n{msg}") from err
        elif not isinstance(self._lines, Iterator):
            raise Error("Please provide an iterator or a file path")

        try:
            yield from self._next(self._lines)
        except OSError as err:
            msg = "An error occurred"
            if self._path:
                msg += f" while parsing file '{self._path}'"
            msg += f":\n{Error(err).indent(2)}"
            raise Error(msg) from err

        if isinstance(self._lines, IO):
            self._lines.close()
            self._lines = None

    def _locate_last_snapshot(self, fobj: IO[str], max_pos: int | None = None) -> int:
        """
        Locate the file position of the last interrupts statistics snapshot in a file.

        Args:
            fobj: The interrupts statistics file object to search for the last snapshot in.
            max_pos: Limit the search to the first 'max_pos' bytes of the file. In other words,
                     assume that file size is 'max_pos'. If 'None', the file size will be the
                     true size of the file.

        Returns:
            The file position of the last interrupts statistics snapshot in the file.
        """

        # Will search from the end in blocks of size 'block_size'.
        block_size = 4096

        # Get the file size.
        fobj.seek(0, os.SEEK_END)
        file_size = fobj.tell()

        if max_pos is None:
            max_pos = file_size
        elif max_pos > file_size:
            raise Error(f"File '{self._path}' is smaller than the specified size {max_pos}")

        block_size = min(block_size, max_pos)

        last_timestamp_pos = -1

        # Start from the end of the file, and search for the timestamp line in 'block_size' blocks.
        for iteration in range(max_pos // block_size):
            position = max(max_pos - block_size * (iteration + 1), 0)

            fobj.seek(position)

            # Skip the first incomplete line.
            fobj.readline()

            while True:
                prev_pos = fobj.tell()
                if prev_pos > position + block_size:
                    break

                line = fobj.readline()
                if not line:
                    break

                if fobj.tell() >= max_pos:
                    break

                timestamp = self._parse_timestamp(line)
                if timestamp is not None:
                    last_timestamp_pos = prev_pos

            if last_timestamp_pos >= 0:
                break

            if position == 0:
                break

        if last_timestamp_pos < 0:
            raise Error(f"Failed to locate the last interrupts statistics snapshot in "
                        f"'{self._path}' in file positions range of 0-{max_pos}")

        return last_timestamp_pos

    def get_first_and_last(self) -> tuple[DataSetTypedDict, DataSetTypedDict]:
        """
        Parse and return the first and last interrupts statistics datasets.

        Returns:
            A tuple containing the first and last interrupts statistics datasets. If there is only
            one '/proc/interrupts' snapshot, the first and second elements of the tuple will be the
            same (different objects, same contents).
        """

        if not self._path:
            raise Error("Cannot get first and last snapshots from an iterator, please provide the "
                        "file path instead")

        dataset1 = next(self.next())
        dataset1 = dataset1.copy()

        try:
            # pylint: disable=consider-using-with
            fobj = open(self._path, "r", encoding="utf-8")
        except OSError as err:
            errmsg = Error(err).indent(2)
            raise Error(f"Failed to open '{self._path}':\n{errmsg}") from err

        try:
            pos = self._locate_last_snapshot(fobj)
        except OSError as err:
            errmsg = Error(err).indent(2)
            raise Error(f"I/O error on file '{self._path}':\n{errmsg}") from err

        try:
            fobj.seek(pos)
        except OSError as err:
            errmsg = Error(err).indent(2)
            raise Error(f"Cannot set file position to {pos} for file "
                        f"'{self._path}':\n{errmsg}") from err

        try:
            dataset2 = next(self._next(fobj))
        except StopIteration:
            raise Error("Failed to locate the last interrupts statistics snapshot in "
                        f"'{self._path}") from None

        # Check if the last snapshot is cut.
        last_irqname1 = list(dataset1["irq_info"].keys())[-1]
        last_irqname2 = list(dataset2["irq_info"].keys())[-1]

        if last_irqname1 == last_irqname2:
            return dataset1, dataset2.copy()

        # The last snapshot is cut, find the second to last snapshot.
        try:
            pos = self._locate_last_snapshot(fobj, max_pos=pos)
        except OSError as err:
            errmsg = Error(err).indent(2)
            raise Error(f"I/O error on file '{self._path}':\n{errmsg}") from err

        try:
            fobj.seek(pos)
        except OSError as err:
            errmsg = Error(err).indent(2)
            raise Error(f"Cannot set file position to {pos} for file "
                        f"'{self._path}':\n{errmsg}") from err

        try:
            dataset2 = next(self._next(fobj))
        except StopIteration:
            raise Error(f"Failed to locate the last interrupts statistics snapshot in "
                        f"'{self._path}") from None

        return dataset1, dataset2.copy()
