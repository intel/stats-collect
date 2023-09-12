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

from pepclibs.helperlibs.Exceptions import Error

class DTabConfig:
    """This class provides the API used to configure the contents of a data tab."""

    def add_hist(self, mdef):
        """Add a histogram for metric with definition dictionary 'mdef' to the data tab."""
        self.hists.append(mdef)

    def add_chist(self, mdef):
        """
        Add a cumulative histogram for metric with definition dictionary 'mdef' to the data tab.
        """
        self.chists.append(mdef)

    def add_scatter_plot(self, xdef, ydef):
        """
        Add a scatter plot for metrics with definition dictionary 'xdef', and 'ydef' to the data
        tab.
        """
        self.scatter_plots.append((xdef, ydef,))

    def add_alert(self, alert):
        """Set the alert message for the data tab."""
        self.alerts.append(alert)

    def set_smry_funcs(self, smry_funcs):
        """
        Set the summary functions which will be used in the summary table for the data tab.

        Expects 'smry_funcs' to be a dictionary in the format '{metric: list[function_name]}'.
        """
        self.smry_funcs = smry_funcs

    def set_hover_defs(self, hover_defs):
        """
        Set the hover text metric definitions.

        Expects 'hover_defs' to be a dictionary in the format '{reportid: list[definitiod_dicts]}'.
        """
        self.hover_defs = hover_defs

    def __init__(self, name):
        """
        Class constructor. 'name' represents the name of the tab. See 'DTabDC.name' for more
        information.
        """

        self.name = name

        self.scatter_plots = []
        self.chists = []
        self.hists = []

        self.smry_funcs = {}
        self.hover_defs = None
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
