# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
API for creating and populating file previews. A file preview is a data tab element that includes
the contents of one or multiple files, and possibly a diff between the files.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import difflib
import filecmp
from pathlib import Path
from pepclibs.helperlibs import Logging, Human
from pepclibs.helperlibs.Exceptions import Error, ErrorExists, ErrorNotFound
from statscollectlibs.helperlibs import FSHelpers
from statscollectlibs.htmlreport.tabs import _BuiltTab

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

_RESONABLE_FILE_SIZE = 2 * 1024 * 1024

def _has_reasonable_size(file_path: Path, title: str) -> bool:
    """
    Check if a file that is intended to be included to a file preview has "reasonable" size.

    Args:
        file_path: path to the file to check the size for.
        title: the file preview title.

    Returns:
        'True' if file size is reasonable, otherwise 'False'
    """

    try:
        fsize = file_path.stat().st_size
    except OSError as err:
        errmsg = Error(str(err)).indent(2)
        _LOG.warning("Skipping file preview '%s': Unable to check the size of file '%s' before "
                     "copying:\n%s", title, file_path, errmsg)
        return False

    if fsize > _RESONABLE_FILE_SIZE:
        _LOG.warning("Skipping file preview '%s': file '%s' size is %s, which is larger than the "
                     "%s limit", title, file_path, Human.bytesize(fsize),
                     Human.bytesize(_RESONABLE_FILE_SIZE))
        return False

    return True

class FilePreviewBuilder:
    """
    Create and Populate file previews. A file preview is a data tab element that includes the
    contents of one or multiple files, and possibly a diff between the files.
    """

    def __init__(self, outdir: Path, basedir: Path | None = None, diff: bool = True):
        """
        The class constructor.

        Args:
            outdir: The output directory path (where the file preview files should be placed).
            basedir: The report base directory directory path, defaults to 'outdir'.
            diff: whether the diff should be generated.
        """

        self._outdir = outdir
        self._basedir = basedir if basedir else outdir
        self._diff = diff

    def _generate_html_diff(self, paths: list[Path], diff_name: str) -> Path:
        """
        Generate an HTML diff of the files at 'paths' with file name 'diff_name.html'.

        Args:
            paths: paths to the files to diff.
            diff_name: base name of the resulting diff HTML file.

        Returns:
            Path of the resulting diff HTML file relative to the result base directory
            ('self.basedir').
        """

        if filecmp.cmp(paths[0], paths[1], shallow=False):
            identical_diff_path = self._outdir / "diffs" / "identical.diff"
            if not identical_diff_path.exists():
                identical_diff_path.parent.mkdir(parents=True, exist_ok=True)
                with open(identical_diff_path, "w", encoding="utf-8") as f:
                    f.write("Diff not generated: identical content.")
            return identical_diff_path.relative_to(self._basedir)

        # Read the contents of the files into 'lines'.
        lines = []
        for fp in paths:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    lines.append(f.readlines())
            except OSError as err:
                msg = Error(str(err)).indent(2)
                raise Error(f"Cannot open file at '{fp}' to create diff:\n{msg}") from None

        # Store the diff in a separate directory and with the '.diff' file ending.
        diff_path = (self._outdir / "diffs" / diff_name).with_suffix('.diff')
        try:
            diff_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Cannot create diffs directory '{diff_path.parent}':\n"
                        f"{msg}") from None

        try:
            with open(diff_path, "w", encoding="utf-8") as f:
                reportids = [str(path) for path in paths]
                f.writelines(difflib.unified_diff(lines[0], lines[1],
                                                  fromfile=reportids[0], tofile=reportids[1]))
        except Exception as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Cannot create diff at path '{diff_path}':\n{msg}") from None

        return diff_path.relative_to(self._basedir)

    def _copy_file(self, file_path: Path, reportid: str) -> Path:
        """
        Copy file a file preview path from the raw result directory to the output directory.

        Args:
            file_path: the raw file preview file path.
            reportid: report ID of the result the file belongs to.

        Returns:
            Path of the copy.
        """

        dst_dir = self._outdir / reportid

        try:
            dst_dir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Can't create directory '{dst_dir}':\n{errmsg}") from err

        dst_path = dst_dir / file_path.name

        try:
            FSHelpers.copy(file_path, dst_path)
        except ErrorExists:
            _LOG.debug("File '%s' is already in output dir: will not replace", dst_path)
            dst_path = file_path

        return dst_path

    def build_fpreview(self, title: str, paths: dict[str, Path]) -> _BuiltTab.BuiltDTabFilePreview:
        """
        Build and return a file preview element.

        Args:
            title: The title of the resultant file preview element.
            paths: a dictionary in the format of '{ReportID: FilePath}' where 'FilePath' is the path
                   to the file which should be included in the file preview for result 'ReportID'.

        Returns:
            The file preview element object ('_BuiltTab.FilePreviewDC').
        """

        new_paths: dict[str, Path] = {}
        for reportid, file_path in paths.items():
            if not file_path.exists():
                # If one of the files does not exist, do not add it to the file preview.
                _LOG.debug("File preview '%s' does not include report '%s' since the file '%s' "
                           "doesn't exist", title, reportid, file_path)
                continue

            if not _has_reasonable_size(file_path, title):
                continue

            # If the file is not in 'outdir' it should be copied to 'outdir'.
            if self._outdir not in file_path.parents:
                dst_path = self._copy_file(file_path, reportid)
            else:
                dst_path = file_path

            new_paths[reportid] = dst_path

        if not new_paths:
            raise ErrorNotFound(f"Unable to generate file preview '{title}'")

        if self._diff and len(new_paths) == 2:
            try:
                # Name the diff after one of the files.
                diff_paths = list(new_paths.values())
                diff_name = diff_paths[0].name
                diff = self._generate_html_diff(diff_paths, diff_name)
            except Error as err:
                _LOG.info("Unable to generate diff for file preview '%s'", title)
                _LOG.debug(err)
                diff = None
        else:
            diff = None

        for reportid, path in new_paths.items():
            new_paths[reportid] = path.relative_to(self._basedir)

        return _BuiltTab.BuiltDTabFilePreview(title, new_paths, diff)
