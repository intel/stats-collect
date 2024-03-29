# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "SysInfo" data tab.

"SysInfo" tabs contain various system information about the systems under test (SUTs).
"""

from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport.tabs import _DTabBuilder

class SysInfoTabBuilderBase(_DTabBuilder.DTabBuilder):
    """
    This base class provides the capability of populating a "SysInfo" tab.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which represents system information.
    """

    def get_tab(self):
        """Returns a '_Tabs.DTabDC' instance which represents system information."""

        self.add_fpreviews(self.stats_paths, self.files)

        if self.fpreviews:
            return super().get_tab()

        raise Error(f"unable to build '{self.name}' SysInfo tab, no file previews could be "
                    f"generated.")

    def __init__(self, name, outdir, files, stats_paths, basedir=None):
        """
        Class constructor. Arguments are the same as in '_TabBuilderBase.TabBuilderBase()' except
        for the following:
         * name - name to give the tab produced when 'get_tab()' is called.
         * files - a dictionary containing the paths of files to include file previews for.
                   Expected to be in the format '{Name: FilePath}' where 'Name' will be the title
                   of the file preview and 'FilePath' is the path of the file to preview.
                   'FilePath' should be relative to the directories in 'stats_paths'
         * stats_paths - a dictionary in the format '{ReportID: StatsDir}' where 'StatsDir' is the
                         path to the directory which contains raw statistics files for 'ReportID'.
        """

        if not any(fp for fp in stats_paths.values()):
            raise Error("unable to add file previews since not all reports have a statistics dir")

        super().__init__({}, outdir, name, basedir=basedir)

        self.name = name
        self.files = files
        self.stats_paths = stats_paths
