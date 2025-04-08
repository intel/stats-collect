# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the API used to configure the contents of container and data tabs by providing
the following classes:
  * 'DTabConfig' - specifies the contents of a data tab. For example, dictates which plots should be
                   included in the tab.
  * 'CTabConfig' - specifies the contents of a container tab. For example, outlines a tab hierarchy
                   by specifying child container or data tabs.
"""

# TODO: finish annotating and modernizing this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

from pepclibs.helperlibs.Exceptions import Error

class DTabConfig:
    """This class provides the API used to configure the contents of a data tab."""

    def add_hist(self, colname):
        """Add a histogram for dataframe column 'colname' to the data tab."""
        self.hists.append(colname)

    def add_chist(self, colname):
        """
        Add a cumulative histogram for dataframe column 'colname' to the data tab.
        """
        self.chists.append(colname)

    def add_scatter_plot(self, xcolname, ycolname):
        """
        Add a scatter plot for dataframe columns 'xcolname' and 'ycolname' to the data tab.
        """
        assert isinstance(xcolname, str)
        assert isinstance(ycolname, str)
        self.scatter_plots.append((xcolname, ycolname,))

    def add_alert(self, alert):
        """Set the alert message for the data tab."""
        self.alerts.append(alert)

    def set_smry_funcs(self, smry_funcs):
        """
        Set the summary functions which will be used in the summary table for the data tab.

        Expects 'smry_funcs' to be a dictionary in the format '{metric: list[function_name]}'.
        """
        self.smry_funcs = smry_funcs

    def set_hover_colnames(self, hover_colnames: list[str] | None):
        """
        Configure the list of column names to be used for hover text in the scatter plot.

        Args:
            hover_colnames: A list of column names to use for hover text. Use 'None' to disable
            hover text.
        """
        self.hover_colnames = hover_colnames

    def __init__(self, name):
        """
        Class constructor. 'name' represents the name of the tab. See 'BuiltDTab.name' for more
        information.
        """

        self.name = name

        self.scatter_plots = []
        self.chists = []
        self.hists = []

        self.smry_funcs = {}
        self.hover_colnames = None
        self.alerts = []

class CTabConfig:
    """This class provides the API used to configure the contents of a container tab."""

    def __init__(self, name, dtabs=None, ctabs=None):
        """
        Class constructor. Arguments are as follows:
          * name - the name of the container tab.
          * dtabs - a list of 'DTabConfig' instances.
          * ctabs - a list of 'CTabConfig' instances.

        Note that a container tab can exclusively contain either data tabs or other container tabs.
        For this reason, the 'dtabs' and 'ctabs' options are mutually exclusive.
        """

        if dtabs and ctabs:
            raise Error("the options 'dtabs' and 'ctabs' are mutually exclusive, please only "
                        "provide one")

        self.name = name
        self.dtabs = [] if dtabs is None else dtabs
        self.ctabs = [] if ctabs is None else ctabs
