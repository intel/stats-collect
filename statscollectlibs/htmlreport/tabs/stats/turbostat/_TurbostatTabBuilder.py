# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the turbostat statistics tab.
"""

import logging
from pepclibs.helperlibs.Exceptions import ErrorNotFound, Error
from statscollectlibs.htmlreport.tabs import _Tabs, TabConfig
from statscollectlibs.htmlreport.tabs.stats.turbostat import _MCPUL2TabBuilder, _TotalsL2TabBuilder

_LOG = logging.getLogger()

class TurbostatTabBuilder:
    """
    This class provides the capability of populating the turbostat statistics tab.

    Public methods overview:
    1. Optionally, retrieve the default 'TabConfig.CTabConfig' instance. See 'TabConfig' for more
       information on tab configurations.
       * 'get_default_tab_cfg()'
    2. Generate a '_Tabs.CTabDC' instance containing turbostat level 2 tabs. Optionally provide a
       tab configuration as a 'CTabConfig' to customise the tab. This can be based on the default
       configuration retrieved using 'get_default_tab_cfg()'.
       * 'get_tab()'
    """

    name = "Turbostat"
    stname = "turbostat"

    def get_default_tab_cfg(self):
        """Same as 'TabBuilderBase.get_default_tab_cfg()'."""

        ctabs = [tbldr.get_default_tab_cfg() for tbldr in self.l2tab_bldrs.values()]
        return TabConfig.CTabConfig(self.name, ctabs=ctabs)

    def get_tab(self, tab_cfg=None):
        """
        Returns a '_Tabs.CTabDC' instance containing turbostat level 2 tabs:

        1. If 'measured_cpus' was provided to the constructor, a "Measured CPU" container tab will
        be generated containing turbostat tabs which visualise turbostat data for the CPU under
        test.
        2. A "Totals" container tab will be generated containing turbostat tabs which
        visualise the turbostat system summaries.
        """

        l2_tabs = []

        if not tab_cfg:
            for stab_bldr in self.l2tab_bldrs.values():
                l2_tabs.append(stab_bldr.get_tab())
            return _Tabs.CTabDC(self.name, l2_tabs)

        # Turbostat tab configs must contain either 'Measured CPU' or 'Totals' container tabs.
        for l2tab_cfg in tab_cfg.ctabs:
            try:
                l2_tabs.append(self.l2tab_bldrs[l2tab_cfg.name].get_tab(tab_cfg=l2tab_cfg))
            except KeyError:
                l2_names = ", ".join(bldr.name for bldr in self.l2tab_bldrs)
                raise Error(f"{self.name} tab configuration should contain one or both of the "
                            f"following container tabs: {l2_names}") from None

        return _Tabs.CTabDC(tab_cfg.name, l2_tabs)

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. Adding a turbostat statistics container tab will create a "Turbostat"
        sub-directory and store level 2 tabs inside it. Level 2 tabs will represent metrics stored
        in the raw turbostat statistics file using data tabs.

        Arguments are the same as in '_TabBuilderBase.TabBuilderBase()' except for the following:
         * rsts - a list of 'RORawResult' instances for different results with statistics which
                  should be included in the turbostat tabs.
        """

        self.l2tab_bldrs = {}

        try:
            mcpu_bldr = _MCPUL2TabBuilder.MCPUL2TabBuilder
            self.l2tab_bldrs[mcpu_bldr.name] = mcpu_bldr(rsts, outdir / self.name, basedir=basedir)
        except ErrorNotFound:
            _LOG.info("No measured CPUs specified for any results so excluding '%s' %s tab.",
                      mcpu_bldr.name, self.name)


        totals_bldr = _TotalsL2TabBuilder.TotalsL2TabBuilder
        self.l2tab_bldrs[totals_bldr.name] = totals_bldr(rsts, outdir / self.name, basedir=basedir)
