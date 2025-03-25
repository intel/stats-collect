# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2054 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the base class and common logic for tab builder classes.
"""

# TODO: finish annotating this module
from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from typing import cast
import pandas
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.mdc.MDCBase import MDTypedDict
from statscollectlibs.htmlreport.tabs import _DTabBuilder, _Tabs, TabConfig

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class CDTypedDict(MDTypedDict, total=False):
    """
    The column definition dictionary for a dataframe column. It is same as the metrics definition
    dictionary 'MDTypedDict', but describes a dataframe column, like "CPU0-PkgPower".

    Attributes:
        colname: Column name the definition dictionary describes.
        sname: Column scope, for example "System" or "CPU0".
    """

    colname: str
    sname: str

class TabBuilderBase:
    """
    The base class for tab builder classes.
    """

    # The tab name.
    name: str | None = None
    # The name of the statistics the class represents.
    stname: str | None = None
    stnames: list[str] | None = None

    def _get_smry_funcs(self, colname: str) -> list[str]:
        """
        Return the list of summary function names to include to the D-tab summary table for
        dataframe column 'colname' (e.g., "max" for the maximum value, etc).

        Args:
            colname: dataframe column name to return the summary funcion names for.

        Returns:
            A summary function names list.
        """

        colinfo = self._cdd[colname]
        unit = colinfo.get("unit")
        if not unit:
            funcs = ["max", "avg", "min", "std"]
        else:
            funcs = ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min", "std"]

        return funcs

    def _build_def_dtab_cfg(self, y_metric, x_metric, hover_defs, hist=False, title=None):
        """
        Provide a way to build a default data tab configuration. Return an instance of
        'TabConfig.DTabConfig'. The arguments are as follows.
          * y_metric - the name of the metric which will be plotted on the y-axis of the tab's
                       scatter plot.
          * x_metric - the name of the metric which will be plotted on the x-axis of the tab's
                       scatter plot.
          * hover_defs - a dictionary in the format '{reportid: hov_defs}' where 'hov_defs' is a
                         list of metric definition dictionaries for the metrics which should be
                         included on plots as hover text for the relevant report with id 'reportid'.
          * hist - whether to include a histogram plot for the metric.
          * title - optionally customize the name of the tab. Defaults to 'y_metric'.
        """

        title = title if title is not None else y_metric
        dtab = TabConfig.DTabConfig(title)
        dtab.add_scatter_plot(x_metric, y_metric)
        if hist:
            dtab.add_hist(y_metric)

        smry_funcs = self._get_smry_funcs(y_metric)
        dtab.set_smry_funcs({y_metric: smry_funcs})
        dtab.set_hover_defs(hover_defs)

        return dtab

    def _build_def_ctab_cfg(self, ctab_name, metrics, def_x_metric, smry_funcs, hover_defs):
        """
        Provide a way to build a default container tab configuration. Return an instance of
        'TabConfig.CTabConfig'. The arguments are the same as 'self._build_def_dtab_cfg()' except
        for the following.
          * ctab_name - the name of the container tab.
          * metrics - a list of names of metrics, for which each should have a data tab.
          * def_x_metric - the name of the metric used on the x-axis of plots for all metrics.
        """

        dtabs = []

        for metric in metrics:
            if metric not in self._cdd:
                continue
            dtabs.append(self._build_def_dtab_cfg(metric, def_x_metric, smry_funcs, hover_defs))

        return TabConfig.CTabConfig(ctab_name, dtabs=dtabs)

    def _resolve_metric(self, metric):
        """
        Resolve 'metric' to a metric definition dictionary from 'self._mdd'. If 'metric' is already
        a metric definition dictionary, then do nothing. Else, try to find the relevant definition
        dictionary from 'self._mdd'.
        """

        def _is_mdef(dct):
            """Returns 'True' if 'dct' is a metric definition dictionary. Else, returns 'False'."""

            try:
                # Try and access the required fields for a metric definition dictionary.
                _ = dct["name"]
                _ = dct["title"]
                _ = dct["descr"]
                return True
            except TypeError:
                return False
            except KeyError:
                return False

        if _is_mdef(metric):
            return metric

        if metric not in self._cdd:
            raise Error(f"BUG: unsupported metric '{metric}'")

        return self._cdd[metric]

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

        tab = _DTabBuilder.DTabBuilder(self._dfs, outdir, dtabconfig.name, self._basedir)
        tab = self._add_plots(dtabconfig, tab)
        tab.add_smrytbl(dtabconfig.smry_funcs, self._cdd)
        for alert in dtabconfig.alerts:
            tab.add_alert(alert)

        return tab.get_tab()

    def _build_ctab(self, outdir, ctabconfig):
        """
        Build a container tab according to the tab configuration 'ctabconfig'. If no sub-tabs can be
        generated then raise an 'Error' and if the config provided is empty then return 'None'. The
        arguments are as follows.
          * outdir - path of the directory in which to store the generated tabs.
          * ctabconfig - an instance of 'TabConfig.CTabConfig' which configures the contents of the
                         resultant container tab.
        """

        if not (ctabconfig.ctabs or ctabconfig.dtabs):
            return None

        # Sub-tabs which will be contained by the returned container tab.
        sub_tabs = []

        for dtabconfig in ctabconfig.dtabs:
            try:
                sub_tabs.append(self._build_dtab(outdir, dtabconfig))
            except Error as err:
                _LOG.debug_print_stacktrace()
                _LOG.warning("failed to generate '%s' tab in '%s' tab:\n%s",
                             dtabconfig.name, self.name, err.indent(2))

        for subtab_cfg in ctabconfig.ctabs:
            subdir = Path(outdir) / _DTabBuilder.get_fsname(subtab_cfg.name)
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
        Return a '_Tabs.DTabDC' or '_Tabs.CTabDC' instance which represents statistics found in raw
        statistic files. The arguments are as follows.
          * tab_cfg - an instance of 'TabConfig.CTabConfig' or 'Tab.DTabConfig'. If provided, the
            tab builder will attempt to build the tab according to the provided configuration.
            Otherwise, by default, the default tab configuration will be used to build the tab.
        """

        if tab_cfg is None:
            return self.get_tab(self.get_default_tab_cfg())

        if isinstance(tab_cfg, TabConfig.CTabConfig):
            return self._build_ctab(self._outdir, tab_cfg)

        if isinstance(tab_cfg, TabConfig.DTabConfig):
            return self._build_dtab(self._outdir, tab_cfg)

        raise Error(f"unknown tab configuration type '{type(tab_cfg)}, please provide "
                    f"'{TabConfig.CTabConfig.__name__}' or '{TabConfig.DTabConfig.__name__}'")

    def _build_cdd(self,
                   mdd: dict[str, MDTypedDict],
                   colnames: list[str] | None = None) -> dict[str, CDTypedDict]:
        """
        Build a columns definition dictionary (CDD) that describes columns in dataframes.

        Args:
            mdd: The metrics definition dictionary (MDD) for metrics that will be included in the
                 tab. It describes metrics, while CDD describes columns. Coulumns may include the
                 scope as well. For example, there is a "C1%" metric, which may have 2 columns -
                 "System-C1%" for system-wide C1 residency, and "CPU5-C1%" C1 residency for CPU5.
            colnames: list of dataframe column names to use for the CDD. By default, assume column
                      names are the same as metric names.

        Returns:
            CDTypedDict: The Columns Definition Dictionary.
        """

        cdd: dict[str, CDTypedDict] = {}

        if colnames is None:
            colnames = list(mdd)

        # Build a metrics definition dictionary describing all columns in the dataframe.
        for colname in colnames:
            sname, metric = _DFBuilderBase.split_colname(colname)
            cd = cdd[colname] = cast(CDTypedDict, mdd[metric].copy())
            cd["colname"] = colname
            if sname:
                cd["sname"] = sname

        return cdd

    def __init__(self,
                 dfs: dict[str, pandas.DataFrame],
                 cdd: dict[str, CDTypedDict],
                 outdir: Path ,
                 basedir: Path | None = None):
        """
        Initialize a class instance.

        Args:
            dfs: A the dataframes dictionary with report IDs as the keys and dataframes as values.
            cdd: A columns definition dictionary describing the dataframe columns to include in the
                 tab.
            outdir: The output directory where the sub-directory with tab files will be created
                    created.
            basedir: The base directory of the report. The 'outdir' is a sub-director y of
                     'basedir'. All links and pathes generated it the tab will be relative to
                     'basedir', as opposed to be absolute. Defaults to 'outdir'.
        """

        if self.name is None:
            raise Error(f"BUG: failed to initialise '{type(self).__name__}': 'name' class "
                        f"attribute not populated.")

        if not dfs:
            raise ErrorNotFound(f"BUG: No data for '{self.name}'")

        self._dfs = dfs
        self._cdd = cdd
        self._outdir = outdir / _DTabBuilder.get_fsname(self.name)
        self._basedir = basedir if basedir else outdir

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to create directory '{self._outdir}':\n{errmsg}") from None
