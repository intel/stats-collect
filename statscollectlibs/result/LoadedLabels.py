
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide a class representing a loaded statistic.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
import json
from pathlib import Path
from pepclibs.helperlibs import Logging, Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat

if typing.TYPE_CHECKING:
    from typing import TypedDict, Final
    from statscollectlibs.mdc.MDCBase import MDTypedDict

    class LoadedLablesTypedDict(TypedDict, total=False):
        """
        Type for a dictionary for storing loaded labels.

        Attributes:
            name: The name of the label.
            ts: The time-stamp of the label.
            metrics: The metrics the lable defines.
        """

        ts: int
        name: str
        metrics: dict[str, str]

_ALLOWED_LABEL_KEYS: Final[set[str]] = {"name", "ts", "metrics"}

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class LoadedLabels:
    """The loaded lables file class."""

    def __init__(self, lpath: Path):
        """
        Initialize a class instance.

        Args:
            lpath: Path to the labels file.
        """

        self._lpath = lpath

        self.ldd: dict[str, MDTypedDict] = {}
        self.labels: list[LoadedLablesTypedDict] = []

        self._allowed_label_keys = _ALLOWED_LABEL_KEYS

        if not self._lpath.exists():
            raise Error(f"Labels file '{lpath}' does not exist")
        if not self._lpath.is_file():
            raise Error(f"Labels file '{lpath}' is not a regular file")

    def _validate_label(self, label: LoadedLablesTypedDict, lnum: int, line: str):
        """
        Validate the label dictionary.

        Args:
            label: The label dictionary to validate.
            lnum: The line number in the labels file where the label was read from.
            line: The JSON line that was read from the labels file and parsed into 'label'.

        Raises:
            ErrorBadFormat: If the label is invalid.
        """

        if not isinstance(label, dict):
            raise ErrorBadFormat(f"Label at line {lnum} in '{self._lpath}' is not a dictionary\n"
                                 f"The bad line is: {line}")

        for key, value in label.items():
            if not isinstance(key, str):
                raise ErrorBadFormat(f"Label key at line {lnum} in '{self._lpath}' is not a "
                                     f"string\nThe bad line is: {line}")

            if key not in self._allowed_label_keys:
                allowed = ", ".join(self._allowed_label_keys)
                raise ErrorBadFormat(f"Label key '{key}' at line {lnum} in '{self._lpath}' is not "
                                     f"allowed\nThe allowed keys are: {allowed}\n"
                                     f"The bad line is: {line}")

        # Validate the label name.
        if "name" not in label:
            raise ErrorBadFormat(f"Label at line {lnum} in '{self._lpath}' does not contain a "
                                 f"'name' key\nThe bad line is: {line}")

        supported_names = ("start", "skip")
        if label["name"] not in supported_names:
            supported = ", ".join(supported_names)
            raise ErrorBadFormat(f"Label at line {lnum} in '{self._lpath}' has an unsupported "
                                 f"name '{label['name']}'\nThe supported names are: {supported}.\n"
                                 f"The bad line is: {line}")

        # Validate label timestamp.
        if "ts" not in label:
            raise ErrorBadFormat(f"Label at line {lnum} in '{self._lpath}' does not contain a "
                                 f"'ts' key\nThe bad line is: {line}")

        if not isinstance(label["ts"], (int, float)):
            raise ErrorBadFormat(f"Label time-stamp at line {lnum} in '{self._lpath}' is not an "
                                 f"integer or a float\nThe bad line is: {line}")


        if label["name"] == "skip":
            return

        # Validate the "start" label metrics.
        if "metrics" not in label:
            return

        for metric, value in label["metrics"].items():
            if metric not in self.ldd:
                raise ErrorBadFormat(f"Label metric '{metric}' at line {lnum} in '{self._lpath}' "
                                     f"does not have a corresponding metric definition\nThe bad "
                                     f"line is: {line}")
            if not isinstance(metric, str):
                raise ErrorBadFormat(f"Label metric at line {lnum} in '{self._lpath}' is not a "
                                     f"string\nThe bad line is: {line}")
            if not Trivial.is_num(value):
                raise ErrorBadFormat(f"Metric {metric} value at line {lnum} in '{self._lpath}' is "
                                     f"not a number\nThe bad line is: {line}")

    def load(self):
        """Load the labels from the labels file."""

        _LOG.debug(f"Loading labels from '{self._lpath}'")

        if not self.ldd:
            raise Error(f"Cannot load lables from '{self._lpath}' because the labels definition "
                        f"dictionary was not set")
        try:
            with open(self._lpath, "r", encoding="utf-8") as fobj:
                for lnum, line in enumerate(fobj):
                    if line.startswith("#"):
                        continue

                    try:
                        label = json.loads(line)
                    except json.JSONDecodeError as err:
                        line = line.strip()
                        raise ErrorBadFormat(f"Failed to parse JSON in labels file at path "
                                             f"'{self._lpath}'\nThe bad line is: {line}") from err

                    self._validate_label(label, lnum, line)
                    self.labels.append(label)
        except OSError as err:
            raise Error(f"Failed to read and parse labels file at path '{self._lpath}'") from err

        if not self.labels:
            raise Error(f"Labels file '{self._lpath}' does not contain any labels")
