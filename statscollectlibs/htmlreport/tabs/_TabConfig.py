# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide container and data tab configuration classes. The classes describe how the HTML tabs should
be built.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pepclibs.helperlibs.Exceptions import Error

class DTabConfig:
    """A data tab configuration class, describing the contents of a data tab."""

    def __init__(self, name: str):
        """
        Initialize a class instance.

        Args:
            name: The name of the data tab, will be used as the tab label in the hierarchy of tabs
                  in HTML report.
        """

        self.name = name

        # The list of scatter plots to be included in the data tab. The elements of the list are
        # tuples of the form (xcolname, ycolname), where 'xcolname' and 'ycolname' are the names of
        # the dataframe columns to be used for the X and Y axes of the scatter plot, respectively.
        self.scatter_plots: list[tuple[str, str]] = []

        # List of dataframe column names to be used for hover text in the scatter plot. The hover
        # text is displayed when the user hovers over a point in the scatter plot.
        self.hover_colnames: list[str] = []

        # The list of histograms to be included in the data tab. The elements of the list are the
        # names of the dataframe columns to be visualized as histograms.
        self.hists: list[str] = []

        # The list of cumulative histograms to be included in the data tab. The elements of the list
        # are # the names of the dataframe columns to be visualized as cumulative histograms.
        self.chists: list[str] = []

        # A dictionary with dataframe column names as keys and list of summary function names as
        # values. They are used for the summary table in the data tab. Typically the comumn names
        # are the the scatter plot and histogram column names, and summary functions are the average
        # value, the median, the standard deviation, and so on.
        self.smry_funcs: dict[str, list[str]] = {}

        # List of alert messages to include into the D-tab. The alert messages are displayed to the
        # user to notify them of important information related to the tab, such as missing diagrams
        # or other elements.
        self.alerts: list[str] = []

    def add_scatter_plot(self, xcolname: str, ycolname: str):
        """
        Add a scatter plot for dataframe columns 'xcolname' and 'ycolname' to the data tab.

        Args:
            xcolname: Name of the dataframe column to be used for the X-axis of the scatter plot.
            ycolname: Name of the dataframe column to be used for the Y-axis of the scatter plot.
        """

        self.scatter_plots.append((xcolname, ycolname,))

    def set_hover_colnames(self, hover_colnames: list[str]):
        """
        Configure the list of column names to be used for hover text in the scatter plot.

        Args:
            hover_colnames: A list of column names to use for hover text.
        """

        self.hover_colnames = hover_colnames

    def add_hist(self, colname: str):
        """
        Add a histogram for dataframe column 'colname' to the data tab.

        Args:
            colname: The name of the dataframe column to be visualized as a histogram.
        """

        self.hists.append(colname)

    def add_chist(self, colname: str):
        """
        Add a cumulative histogram for dataframe column 'colname' to the data tab.

        Args:
            colname: The name of the dataframe column to be visualized as a cumulative histogram.
        """

        self.chists.append(colname)

    def set_smry_funcs(self, smry_funcs: dict[str, list[str]]):
        """
        Set the summary functions which will be used in the summary table for the data tab.

        Args:
            smry_funcs: A dictionary where keys are dataframe column names and values are lists of
                        summary function names to be applied to the corresponding metrics.
        """

        self.smry_funcs = smry_funcs

    def add_alert(self, alert: str):
        """
        Add an alert message to the data tab.

        Args:
            alert: The alert message to be added.
        """

        self.alerts.append(alert)

class CTabConfig:
    """A container tab configuration class, describing the contents of a container tab."""

    def __init__(self, name: str, dtabs: list[DTabConfig] | None = None,
                 ctabs: list[CTabConfig] | None = None):
        """
        Initialize a class instance.

        Args:
            name: The name of the container tab.
            dtabs: A list of data tab configuration objects to add to the container tab. Each data
                   tab configuration object is an instance of the 'DTabConfig' class. This argument
                   is mutually exclusive with the 'ctabs' argument.
            ctabs: A list of container tab configuration objects to add to the container tab. Each
                   container tab configuration object is an instance of the 'CTabConfig' class. This
                   argument is mutually exclusive with the 'dtabs' argument.
        """

        if dtabs and ctabs:
            raise Error("BUG: The 'dtabs' and 'ctabs' arguments are mutually exclusive")
        if not dtabs and not ctabs:
            raise Error("BUG: Cannot create a C-tab without contents")

        self.name = name
        self.dtabs = [] if dtabs is None else dtabs
        self.ctabs = [] if ctabs is None else ctabs
