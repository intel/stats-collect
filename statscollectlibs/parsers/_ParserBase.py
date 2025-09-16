# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2015-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
The base class for parsers.
"""

from __future__ import annotations  # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error

if typing.TYPE_CHECKING:
    from typing import IO, Generator, Iterator, cast

class ParserBase:
    """The base class for parsers."""

    def __init__(self, path: Path | None = None, lines: Iterator[str] | IO[str] | None = None):
        """
        Initialize a class instance. The arguments are as follows.

        Args:
            path: Path to the turbostat output file that should be parsed.
            lines: An iterable object which provides the turbostat output to parse one-by-one.
        """

        if path and lines:
            raise Error("Please, specify either 'path' or 'lines', but not both")

        if not path and not lines:
            raise Error("Please, specify either 'path' or 'lines'")

        self._path = path
        self._lines = lines

        if path:
            try:
                # pylint: disable=consider-using-with
                self._lines = open(path, "r", encoding="utf-8")
            except OSError as err:
                errmsg = Error(str(err)).indent(2)
                raise Error(f"Failed to open '{path}':\n{errmsg}") from err

    def _next(self) -> Generator[dict, None, None]: # pylint: disable=no-self-use
        """
        Yield the datasets one-by-one. Should be implemented by the derived parser class.

        Yields:
            Parser-specific datasets.
        """

        raise Error("_next() is not implemented")

    def next(self) -> Generator[dict, None, None]:
        """
        Yield the datasets one-by-one. Datasets format are parser-specific.

        Yields:
            Parser-specific datasets.
        """

        yield from self._next()
        if hasattr(self._lines, "close"):
            if typing.TYPE_CHECKING:
                io_lines = cast(IO[str], self._lines)
            else:
                io_lines = self._lines
            io_lines.close()
