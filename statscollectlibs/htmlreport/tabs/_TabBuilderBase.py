# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides a base class and common logic for populating a group of statistics tabs.
"""

from pathlib import Path
import logging
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.defs import DefsBase
from statscollectlibs.htmlreport.tabs import _DTabBuilder, _Tabs, TabConfig

_LOG = logging.getLogger()

class TabBuilderBase:
    """
    This base class can be inherited from to populate a group of statistics tabs.

    For classes with names such as '_XStatsTabBuilder' and the 'Builder' suffix, their purpose is to
    produce a tab containing data from 'XStats'. These classes do not represent the tab itself but a
    builder which creates those tabs.

    This base class requires child classes to implement the following methods:
    1. Read a raw statistics file and convert the statistics data into a 'pandas.DataFrame'.
       * '_read_stats_file()'
    2. Optionally, retrieve the default 'TabConfig.DTabConfig' or 'TabConfig.CTabConfig' instance.
       See 'TabConfig' for more information on tab configurations.
       * 'get_default_tab_cfg()'
    3. Generate a '_Tabs.DTabDC' or '_Tabs.CTabDC' instance which represents statistics found in raw
       statistics files. Optionally provide a tab configuration ('DTabConfig' or 'CTabConfig') to
       customise the tab. This can be based on the default configuration retrieved using
       'get_default_tab_cfg()'.
       * 'get_tab()'
    """

    # The name of the statistics represented in the produced tab.
    name = None

    def _build_def_dtab_cfg(self, y_metric, x_metric, smry_funcs, hover_defs):
        """
        Provides a way to build a default data tab configuration. Returns an instance of
        'TabConfig.DTabConfig'. Arguments are as follows:
          * y_metric - the name of the metric which will be plotted on the y-axis of the tab's
                       scatter plot.
          * x_metric - the name of the metric which will be plotted on the x-axis of the tab's
                       scatter plot.
          * smry_funcs - a dictionary in the format '{metric: summary_func}', for example:
                         {
                            Metric1: ["99.999%", "99.99%",...],
                            Metric2: ["max", "min",...]
                         }
          * hover_defs - a dictionary in the format '{reportid: hov_defs}' where 'hov_defs' is a
                         list of metric definition dictionaries for the metrics which should be
                         included on plots as hover text for the relevant report with id 'reportid'.
        """

        dtab = TabConfig.DTabConfig(y_metric)
        dtab.add_scatter_plot(x_metric, y_metric)
        dtab.add_hist(y_metric)
        dtab.set_smry_funcs({y_metric: smry_funcs[y_metric]})
        dtab.set_hover_defs(hover_defs)

        return dtab

    def _build_def_ctab_cfg(self, ctab_name, metrics, def_x_metric, smry_funcs, hover_defs):
        """
        Provides a way to build a default container tab configuration. Returns an instance of
        'TabConfig.CTabConfig'. Arguments are the same as 'self._build_def_dtab_cfg()' except for:
          * ctab_name - the name of the container tab.
          * metrics - a list of names of metrics, for which each should have a data tab.
          * def_x_metric - the name of the metric used on the x-axis of plots for all metrics.
        """

        dtabs = []

        for metric in metrics:
            if metric not in self._defs.info:
                continue
            dtabs.append(self._build_def_dtab_cfg(metric, def_x_metric, smry_funcs, hover_defs))

        return TabConfig.CTabConfig(ctab_name, dtabs=dtabs)

    def _resolve_metric(self, metric):
        """
        Resolve 'metric' to a metric definition dictionary from 'self._defs'. If 'metric' is already
        a metric definition dictionary, then do nothing. Else, try to find the relevant definition
        dictionary from 'self._defs'.
        """

        if DefsBase.is_mdef(metric):
            return metric

        if metric not in self._defs.info:
            raise Error(f"BUG: unsupported metric '{metric}'")

        return self._defs.info[metric]

    def _add_plots(self, dtabconfig, tab):
        """Add plots to 'tab' based on the metrics specified in the configuration 'dtabconfig'."""

        scatter = []
        for xmetric, ymetric in dtabconfig.scatter_plots:
            x_def = self._resolve_metric(xmetric)
            y_def = self._resolve_metric(ymetric)
            scatter.append((x_def, y_def))

        hists = []
        for metric in dtabconfig.hists:
            hists.append(self._resolve_metric(metric))

        chists = []
        for metric in dtabconfig.chists:
            chists.append(self._resolve_metric(metric))

        hover_defs = {}
        if dtabconfig.hover_defs:
            for reportid, metrics in dtabconfig.hover_defs.items():
                hover_defs[reportid] = [self._resolve_metric(metric) for metric in metrics]

        hover_defs = hover_defs if hover_defs else None

        tab.add_plots(plot_axes=scatter, hist=hists, chist=chists, hover_defs=hover_defs)
        return tab

    def _build_dtab(self, outdir, dtabconfig):
        """Build a data tab according to the tab configuration 'dtabconfig'."""

        tab = _DTabBuilder.DTabBuilder(self._reports, outdir, dtabconfig.name, self._basedir)
        tab = self._add_plots(dtabconfig, tab)
        tab.add_smrytbl(dtabconfig.smry_funcs, self._defs)
        for alert in dtabconfig.alerts:
            tab.add_alert(alert)

        return tab.get_tab()

    def _build_ctab(self, outdir, ctabconfig):
        """
        Build a container tab according to the tab configuration 'ctabconfig'. If no sub-tabs can be
        generated then raises an 'Error' and if the config provided is empty then returns 'None'.
        Arguments are as follows:
         * outdir - path of the directory in which to store the generated tabs.
         * ctabconfig - an instance of 'TabConfig.CTabConfig' which configures the contents of the
                        resultant container tab.
        """

        if not (ctabconfig.ctabs or ctabconfig.dtabs):
            return None

        # Sub-tabs which will be contained by the returned container tab.
        sub_tabs = []

        for dtabconfig in ctabconfig.dtabs:
            results = {rid: sdf for rid, sdf in self._reports.items() if dtabconfig.name in sdf}
            if not results:
                _LOG.info("Skipping '%s' tab in '%s' tab: no results contain data for this "
                          "metric.", dtabconfig.name, self.name)
                continue

            try:
                sub_tabs.append(self._build_dtab(outdir, dtabconfig))
            except Error as err:
                _LOG.info("Skipping '%s' tab in '%s' tab: error occured during tab generation.",
                          dtabconfig.name, self.name)
                _LOG.debug(err)

        for subtab_cfg in ctabconfig.ctabs:
            subdir = Path(outdir) / DefsBase.get_fsname(subtab_cfg.name)
            subtab = self._build_ctab(subdir, subtab_cfg)

            if subtab:
                sub_tabs.append(subtab)

        if sub_tabs:
            return _Tabs.CTabDC(ctabconfig.name, sub_tabs)

        raise Error(f"unable to generate a container tab for {self.name}.")

    def get_default_tab_cfg(self):
        """
        Generate a 'TabConfig.DTabConfig' or 'TabConfig.CTabConfig' instance representing the
        default tab configuration.
        """

        raise NotImplementedError()

    def get_tab(self, tab_cfg=None):
        """
        Returns a '_Tabs.DTabDC' or '_Tabs.CTabDC' instance which represents statistics found in raw
        statistic files. Arguments are as follows:
         * tab_cfg - an instance of 'TabConfig.CTabConfig' or 'Tab.DTabConfig'. If provided, the tab
                     builder will attempt to build the tab according to the provided configuration.
                     Otherwise, by default, the default tab configuration will be used to build the
                     tab.
        """

        if tab_cfg is None:
            return self.get_tab(self.get_default_tab_cfg())

        if isinstance(tab_cfg, TabConfig.CTabConfig):
            return self._build_ctab(self._outdir, tab_cfg)

        if isinstance(tab_cfg, TabConfig.DTabConfig):
            return self._build_dtab(self._outdir, tab_cfg)

        raise Error(f"unkown tab configuration type '{type(tab_cfg)}, please provide "
                    f"'{TabConfig.CTabConfig.__name__}' or '{TabConfig.DTabConfig.__name__}'")

    def __init__(self, dfs, outdir, basedir=None, defs=None):
        """
        The class constructor. Adding a statistics container tab will create a sub-directory and
        store tabs inside it. These tabs will represent all of the metrics stored in 'stats_file'.
        Arguments are as follows:
         * dfs - a dictionary in the format '{ReportId: pandas.DataFrame}' for each result where the
                 'pandas.DataFrame' contains that statistics data for that result.
         * outdir - the output directory in which to create the sub-directory for the container tab.
         * basedir - base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
         * defs - a '_DefsBase.DefsBase' instance containing definitions for the metrics which
                  should be included in the output tab.
        """

        if self.name is None:
            raise Error(f"failed to initalise '{type(self).__name__}': 'name' class attribute not "
                        f"populated.")

        if not dfs:
            raise ErrorNotFound(f"failed to initalise '{type(self).__name__}': no results contain "
                                f"data for this statistic.")

        self._reports = dfs
        self._outdir = outdir / DefsBase.get_fsname(self.name)
        self._basedir = basedir if basedir else outdir
        self._defs = defs

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create directory '{self._outdir}':\n{msg}") from None
