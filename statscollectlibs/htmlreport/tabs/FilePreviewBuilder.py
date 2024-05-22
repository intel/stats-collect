# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a 'File Preview'. See '_Tabs.FilePreviewDC' for
more information on file previews.
"""

import difflib
import filecmp
import logging
from pepclibs.helperlibs import Human
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from statscollectlibs.helperlibs import FSHelpers
from statscollectlibs.htmlreport.tabs import _Tabs

_LOG = logging.getLogger()

def _reasonable_file_size(fp, name):
    """
    Returns 'True' if the file at path 'fp' is 2MiB or smaller, otherwise returns 'False'. Also
    returns 'False' if the size could not be verified.  Arguments are as follows:
        * fp - path of the file to check the size of.
        * name - name of the file-preview being generated.
    """

    try:
        fsize = fp.stat().st_size
    except OSError as err:
        _LOG.warning("skipping file preview '%s': unable to check the size of file '%s' before "
                     "copying:\n%s", name, fp, err)
        return False

    if fsize > 2*1024*1024:
        _LOG.warning("skipping file preview '%s': the file '%s' (%s) is larger than 2MiB.",
                     name, fp, Human.bytesize(fsize))
        return False
    return True

class FilePreviewBuilder:
    """This class provides the capability of populating a 'File Preview'."""

    def _generate_diff(self, paths, diff_name):
        """
        Helper function for '_add_fpreviews()'. Generates an HTML diff of the files at 'paths' with
        filename 'diff_name.html' in a "diffs" sub-directory. Returns the path of the HTML diff
        relative to 'outdir'.
        """

        if filecmp.cmp(*paths, shallow=False):
            identical_diff_path = self.outdir / "diffs" / "identical.diff"
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
                msg = Error(err).indent(2)
                raise Error(f"cannot open file at '{fp}' to create diff:\n{msg}") from None

        # Store the diff in a separate directory and with the '.diff' file ending.
        diff_path = (self.outdir / "diffs" / diff_name).with_suffix('.diff')
        try:
            diff_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"cannot create diffs directory '{diff_path.parent}':\n"
                        f"{msg}") from None

        try:
            with open(diff_path, "w", encoding="utf-8") as f:
                reportids = [str(path) for path in paths]
                f.writelines(difflib.unified_diff(lines[0], lines[1],
                                                  fromfile=reportids[0], tofile=reportids[1]))
        except Exception as err:
            msg = Error(err).indent(2)
            raise Error(f"cannot create diff at path '{diff_path}':\n{msg}") from None

        return diff_path.relative_to(self._basedir)

    def _copy_file(self, fp, reportid):
        """
        Helper function for 'build_fpreview()'. Copies the file at path 'fp' to
        'self.outdir / reportid'.
        """

        dst_dir = self.outdir / reportid

        try:
            dst_dir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"can't create directory '{dst_dir}':\n{msg}") from None

        dst_path = dst_dir / fp.name

        try:
            FSHelpers.move_copy_link(fp, dst_path, "copy")
        except ErrorExists:
            _LOG.debug("file '%s' already in output dir: will not replace.", dst_path)
            dst_path = fp

        return dst_path

    def build_fpreview(self, title, files):
        """
        Build file preview. Arguments are as follows:
         * title - the title of the resultant file preview element.
         * files - dictionary in the format '{ReportID: FilePath}' where 'FilePath' is the
                   path to the file which should be included in the file preview for result
                   'ReportID'.
        """

        paths = {}
        for reportid, fp in files.items():
            if not fp.exists():
                # If one of the reports does not have a file, exclude the file preview entirely.
                _LOG.debug("file preview '%s' does not include report '%s' since the file '%s' "
                           "doesn't exist.", title, reportid, fp)
                continue

            # If the file is not in 'outdir' it should be copied to 'outdir'.
            if self.outdir not in fp.parents:
                if not _reasonable_file_size(fp, title):
                    break
                dst_path = self._copy_file(fp, reportid)
            else:
                dst_path = fp

            paths[reportid] = dst_path

        if not paths:
            raise Error("unable to generate file preview")

        if len(paths) == 2:
            try:
                # Name the diff after one of the files.
                diff_paths = list(paths.values())
                diff_name = diff_paths[0].name
                diff = self._generate_diff(diff_paths, diff_name)
            except Error as err:
                _LOG.info("Unable to generate diff for file preview '%s'.", title)
                _LOG.debug(err)
                diff = ""
        else:
            diff = ""

        for reportid, path in paths.items():
            paths[reportid] = path.relative_to(self._basedir)

        return _Tabs.FilePreviewDC(title, paths, diff)

    def __init__(self, outdir, basedir=None):
        """Class constructor. Arguments are the same as in '_TabBuilderBase.TabBuilderBase()'."""

        self.outdir = outdir
        self._basedir = basedir if basedir else outdir
        self.fpreviews = []
