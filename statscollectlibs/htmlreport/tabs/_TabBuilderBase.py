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
import pandas
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.mdc.MDCBase import MDTypedDict
from statscollectlibs.htmlreport.tabs import _DTabBuilder, BuiltTab
from statscollectlibs.htmlreport.tabs._TabConfig import CTabConfig, DTabConfig

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

    # The tab name, must be set by the subclass.
    name = "BUG: tab name was not set"

    # The names of the statistics the class represents. Note, not all tabs represent statistics, so
    # 'stnames' is None for non-statistic tabs.
    stnames: list[str] | None = None

    def __init__(self,
                 dfs: dict[str, pandas.DataFrame],
                 cdd: dict[str, CDTypedDict],
                 outdir: Path ,
                 basedir: Path | None = None,
                 xcolname: str | None = None):
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
            xcolname: Name of the dataframe column to use for the X-axis of the plots. If not
                      provided, the X-axis will use the time elapsed since the beginning of the
                      measurements.
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
        self._xcolname = xcolname

        if self._xcolname and self._xcolname not in cdd:
            raise Error(f"BUG: the X-axis metric '{self._xcolname}' not found in the columns "
                        f"definition dictionary for the '{self.name}' tab")

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to create directory '{self._outdir}':\n{errmsg}") from None

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

    def _build_dtab_cfg(self,
                        ycolname: str,
                        title: str | None = None,
                        hist: bool = False,
                        hover_colnames: list[str] | None = None) -> DTabConfig:
        """
        Build a data tab configuration object ('DTabConfig').

        Args:
            ycolname: The name of the metric to be plotted on the Y-axis of the tab's scatter plot.
            title: A name for the tab. Defaults to the value of 'ycolname'.
            hist: A boolean indicating whether to include a histogram plot for the metric in the
                  tab.
            hover_colnames: A list of column names to include as hover text on the scatter plot.

        Returns:
            An instance of 'DTabConfig' configured with the provided parameters.
        """

        if not self._xcolname:
            raise Error("BUG: the X-axis metric was not set")

        title = title if title is not None else ycolname
        dtabconfig = DTabConfig(title)
        dtabconfig.add_scatter_plot(self._xcolname, ycolname)
        if hist:
            dtabconfig.add_hist(ycolname)

        smry_funcs = self._get_smry_funcs(ycolname)
        dtabconfig.set_smry_funcs({ycolname: smry_funcs})
        dtabconfig.set_hover_colnames(hover_colnames)

        return dtabconfig

    def _add_plots(self,
                   dtabconfig: DTabConfig,
                   dtab_bldr: _DTabBuilder.DTabBuilder) -> _DTabBuilder.DTabBuilder:
        """
        Add plots to the tab based on the metrics specified in the data tab configuration.

        Args:
            dtabconfig: The data tab configuration object containing details about the plots to be
            added, such as scatter plots, histograms, etc.
            dtab_bldr: The data tab builder object that will be used for building the tab.

        Returns:
            The updated data tab builder object with the added plots.
        """

        scatter: list[tuple[CDTypedDict, CDTypedDict]] = []
        for xcolname, ycolname in dtabconfig.scatter_plots:
            scatter.append((self._cdd[xcolname], self._cdd[ycolname]))

        hists: list[CDTypedDict] = []
        for colname in dtabconfig.hists:
            hists.append(self._cdd[colname])

        chists: list[CDTypedDict] = []
        for colname in dtabconfig.chists:
            chists.append(self._cdd[colname])

        hover_mds: list[CDTypedDict] = []
        if dtabconfig.hover_colnames:
            for colname in dtabconfig.hover_colnames:
                if colname == "CPU5-UMHz0.0":
                    print("CDD columns: ", list(self._cdd))
                hover_mds.append(self._cdd[colname])

        dtab_bldr.add_plots(plot_axes=scatter, hist=hists, chist=chists,
                            hover_mds=hover_mds)
        return dtab_bldr

    def _build_dtab(self, outdir: Path, dtabconfig: DTabConfig) -> BuiltTab.BuiltDTab:
        """
        Build and return a data tab based on the provided data tab configuration.

        Args:
            outdir: The output directory where the data tab files will be stored.
            dtabconfig: The data ab configuration object defining the properties of the data tab,
                        including its name, summary functions, alerts, etc.

        Returns:
            A data tab object constructed using the provided configuration.
        """

        dtab_bldr = _DTabBuilder.DTabBuilder(self._dfs, outdir, dtabconfig.name, self._basedir)
        dtab_bldr = self._add_plots(dtabconfig, dtab_bldr)
        dtab_bldr.add_smrytbl(dtabconfig.smry_funcs, self._cdd)
        for alert in dtabconfig.alerts:
            dtab_bldr.add_alert(alert)

        return dtab_bldr.get_tab()

    def _build_ctab(self, outdir, ctabconfig):
        """
        Build a container tab according to the tab configuration 'ctabconfig'. If no sub-tabs can be
        generated then raise an 'Error' and if the config provided is empty then return 'None'. The
        arguments are as follows.
          * outdir - path of the directory in which to store the generated tabs.
          * ctabconfig - an instance of 'CTabConfig' which configures the contents of the resultant
                         container tab.
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
            return BuiltTab.BuiltCTab(ctabconfig.name, sub_tabs)

        raise Error(f"unable to generate a container tab for {self.name}.")

    def get_tab_cfg(self) -> CTabConfig | DTabConfig:
        """
        Return a container tab (C-tab) configuration object ('CTabConfig') or a data tab (D-tab)
        configuration object ('DTabConfig'). The tab configuration object describes how the HTML tab
        should be built.

        Returns:
            The tab configuration object describing how the tab should be built.
        """

        raise NotImplementedError()

    def get_tab(self):
        """
        Return a 'BuiltTab.BuiltDTab' or 'BuiltTab.BuiltCTab' instance which represents statistics
        found in raw statistic files.
        """

        tab_cfg = self.get_tab_cfg()

        if isinstance(tab_cfg, CTabConfig):
            return self._build_ctab(self._outdir, tab_cfg)

        if isinstance(tab_cfg, DTabConfig):
            return self._build_dtab(self._outdir, tab_cfg)

        raise Error(f"unknown tab configuration type '{type(tab_cfg)}, please provide "
                    f"'{CTabConfig.__name__}' or '{DTabConfig.__name__}'")
