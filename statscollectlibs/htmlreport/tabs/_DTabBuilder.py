# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the 'DTabBuider' class that builds an HTML report data tab (D-tab).
"""

# TODO: finish annotating and modernizing this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
import pandas
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs import DFSummary
from statscollectlibs.mdc.MDCBase import MDTypedDict
from statscollectlibs.htmlreport import _Histogram, _ScatterPlot, _SummaryTable
from statscollectlibs.htmlreport.tabs import BuiltTab, FilePreviewBuilder

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

def get_fsname(name: str):
    """
    Generate a file-system and URL-safe version of the input string.

    This function replaces certain special characters in the input string with descriptive words and
    removes non-alphanumeric characters. It is useful for creating safe names for file names and
    URLs.

    Args:
        name: The input string to be sanitized. This can be a dataframe column name, a metric name,
              or a tab name.

    Returns:
        A sanitized string that is safe for use in file systems and URLs.
    """

    name = name.replace("%", "Percent")
    name = name.replace("+", "Plus")
    name = name.replace("-", "Minus")

    # Filter out any remaining non-alphanumeric characters.
    name = "".join([c for c in name if c.isalnum()])
    return name

class DTabBuilder:
    """
    Provide a capability of building a data tab (D-tab) for the HTML report.
    """

    def __init__(self,
                 dfs: dict[str, pandas.DataFrame],
                 outdir: Path,
                 tabname: str,
                 basedir: Path | None = None):
        """
        Initialize a class instance.

        Args:
            dfs: A dictionary indexed by report ID with values being the dataframe containing the
                 data tab data.
            outdir: The output directory where the tab's files will be stored.
            name: The name of the data tab, used as the tab label in the hierarchy of tabs in HTML
                  report.
            basedir: The base directory of the report. The 'outdir' is a sub-director y of
                     'basedir'. All links and pathes generated it the tab will be relative to
                     'basedir', as opposed to be absolute. Defaults to 'outdir'.
        """

        self._dfs = dfs
        self.tabname = tabname
        self._fsname = get_fsname(self.tabname)

        self._outdir = outdir / self._fsname
        self._smry_path = self._outdir / "summary-table.txt"
        self._smrytbl: _SummaryTable.SummaryTable | None = None

        # Sometimes certain diagrams may be skipped for certain column names. In this case there are
        # alerts to inform the user about the reason for absence of the diagram.
        #
        # Using a set to avoid alerting the user of a metric multiple times.
        self._alerted_metrics: set[str] = set()

        # The tab alerts.
        self._alerts: list[str] = []

        if basedir is None:
            self._basedir = outdir
        else:
            self._basedir = basedir

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Failed to create directory '{self._outdir}':\n{msg}") from None

        # Paths to files with plots generated for this tab (all of them - scatter plots and
        # histograms).
        self._ppaths: list[Path] = []

        # File previews which will be added to the data tab.
        self._fpreviews: list[BuiltTab.BuiltDTabFilePreview] = []

    def add_smrytbl(self, smry_funcs: dict[str, list[str]], cdd: dict[str, CDTypedDict]):
        """
        Construct the summary table ('SummaryTable' object) to summarize the tab metrics. The table
        typically contains functions like the average, median, and standard deviation for the
        metrics.

        Args:
            smry_funcs: A dictionary in the format '{colname: list of summary function names}'.
            cdd: The columns definition dictionary describing the dataframe colun names used in
                 'smry_funcs'.

        Notes:
            Example of 'smry_funcs':
                        {
                            "System-Metric1": ["99.999%", "99.99%", ...],
                            "System-Metric2": ["max", "min", ...]
                        }

            The metric name is derived from the column name and the 'cdd' dictionary.

            The 'summary_func' value is allowed to be '[]', which means that no functions will be
            applied to the metric. This can be used for metrics that have only one value.
        """

        self._smrytbl = _SummaryTable.SummaryTable()

        for colname, funcs in smry_funcs.items():
            cd = cdd[colname]
            self._smrytbl.add_metric(cd["title"], cd.get("short_unit"), cd.get("descr"),
                                     fmt="{:.2f}")

            for reportid, df in self._dfs.items():
                if colname not in df:
                    continue

                if funcs:
                    smry_dict = DFSummary.calc_col_smry(df, colname, funcs)
                    for funcname in funcs:
                        self._smrytbl.add_smry_func(reportid, cd["title"], smry_dict[funcname],
                                                    funcname=funcname)
                else:
                    # No functions were specified. Allow this only for metrics that have a single
                    # value.
                    if len(df[colname]) > 1:
                        raise Error(f"BUG: no functions were specified for '{colname}', but there "
                                    f"is more than one metric value")
                    val = df[colname][0]
                    self._smrytbl.add_smry_func(reportid, cd["title"], val, funcname=None)

        try:
            self._smrytbl.generate(self._smry_path)
        except Error as err:
            raise Error(f"Failed to generate the summary table for tab '{self.tabname}'") from err

    @staticmethod
    def _warn_plot_skip_res(reportid: str, plottitle: str, mtitle: str):
        """
        Log when a result is excluded from a plot because it does not have data for the metric.

        Args:
            reportid: The roport ID of the result being excluded.
            plottitle: The title of the plot being the result is excluded from.
            mtitle: The title of the metric for which data is missing.
        """

        _LOG.info("Excluding result '%s' from %s: no data for '%s'.", reportid, plottitle, mtitle)

    def _add_scatter(self, xcd, ycd, hover_cds=None):
        """
        Helper function for 'add_plots()'. Add a scatter plot to the report. Arguments are as
        follows:
         * xcd - the X-axis column definition dictionary.
         * ycd - the Y-axis column definition dictionary.
         * hover_ccs - a list of colunb definition dictionaries to include in the hover text of the
                       scatter plots.
        """

        xcolname = xcd["colname"]
        ycolname = ycd["colname"]

        # Initialise scatter plot.
        fname = f"{get_fsname(ycolname)}-vs-{get_fsname(xcolname)}.html"
        plottitle = f"scatter plot '{ycd['title']} vs {xcd['title']}'"

        s_path = self._outdir / fname
        s = _ScatterPlot.ScatterPlot(xcolname, ycolname, s_path, xcd.get("title"),
                                     ycd.get("title"), xcd.get("short_unit"),
                                     ycd.get("short_unit"))

        for reportid, df in self._dfs.items():
            for cd in [xcd, ycd]:
                if cd["colname"] not in df:
                    self._warn_plot_skip_res(reportid, plottitle, cd["title"])
                    break
            else:
                reduced_df = s.reduce_df_density(df, reportid)
                if hover_cds:
                    hovertext = s.create_hover_template(hover_cds, reduced_df)
                else:
                    hovertext = None
                s.add_df(reduced_df, reportid, hovertext)

        s.generate()
        self._ppaths.append(s_path)

    def _add_histogram(self, cd, cumulative=False, xbins=None):
        """
        Helper function for 'add_plots()'. Add a histogram to the report for datafame column with
        definitions dictionary 'cd'. See '_Histogram.Histogram' for details of 'cumulative' and
        'xbins' arguments.
        """

        colname = cd["colname"]
        if cumulative:
            h_path = self._outdir / f"Percentile-vs-{get_fsname(colname)}.html"
            plottitle = f"cumulative histogram 'Percentile vs {cd['title']}'"
        else:
            h_path = self._outdir / f"Count-vs-{get_fsname(colname)}.html"
            plottitle = f"histogram 'Count vs {cd['title']}'"

        h = _Histogram.Histogram(colname, h_path, cd.get("title"), cd.get("short_unit"),
                                 cumulative=cumulative, xbins=xbins)

        for reportid, df in self._dfs.items():
            if colname not in df:
                self._warn_plot_skip_res(reportid, plottitle, cd["title"])
                continue
            h.add_df(df, reportid)

        h.generate()
        self._ppaths.append(h_path)

    def _skip_metric_plot(self, plotname, xcd, ycd=None):
        """
        Helper function for 'add_plots()'. Checks the data in 'self._dfs' to see if there is
        sufficient data to generate a plot for the metrics 'xcd' and 'ycd'. Returns 'True' or
        'False' if the plot should be skipped or generated respectively.
        """

        if ycd is not None:
            cds = [xcd, ycd]
            plotname = f"{plotname} '{ycd['name']} vs {xcd['name']}'"
        else:
            cds = [xcd]
            plotname = f"{plotname} '{xcd['name']}'"

        for cd in cds:
            colname = cd["colname"]

            sdfs_with_data = [sdf for sdf in self._dfs.values() if colname in sdf]
            # Check that at least one result contains data for column 'colname'.
            if not sdfs_with_data:
                _LOG.debug("skipping %s: no results have data for '%s'", plotname, colname)
                return True

            # Check if there is a constant value for all datapoints.
            sample_dp = sdfs_with_data[0][colname].max()
            if all((sdf[colname] == sample_dp).all() for sdf in sdfs_with_data):
                _LOG.debug("skipping %s: every datapoint in all results is the same, '%s' is "
                           "always '%s'", plotname, colname, sample_dp)
                if colname not in self._alerted_metrics:
                    self._alerts.append(f"'{colname}' was always: '{sample_dp}'. One or more "
                                        f"diagrams have been skipped.")
                    self._alerted_metrics.add(colname)
                return True

        return False

    def add_plots(self,
                  plot_axes: list[tuple[CDTypedDict, CDTypedDict]] | None,
                  hist: list[CDTypedDict] | None = None,
                  chist: list[CDTypedDict] | None = None,
                  hover_mds: list[CDTypedDict] | None = None):
        """
        Add various types of plots to the data tab.

        Args:
            plot_axes: Specifies the X and Y axes metrics for the scatter plots to be added. A list
                       of tuples, where each tuple contains two column definitions (CDTypedDict)
                       representing the X and Y axes for a scatter plot. Each scatter plot will
                       include data from all dataframes.
            hist: Specifies the metrics for the histograms. A list of column definitions
                  (CDTypedDict), where each definition corresponds to a histogram.
            chist: Specifies the metrics for the cumulative histograms. A list of column definitions
                  (CDTypedDict), where each definition corresponds to a cumulative histogram.
            hover_mds: Specifies the metrics to include in the hover text of the scatter plots.  A
                       list of column definitions (CDTypedDict).
        """

        if plot_axes is None and hist is None and chist is None:
            raise Error("BUG: No arguments provided for 'add_plots()', unable to generate plots")

        if plot_axes is None:
            plot_axes = []
        if hist is None:
            hist = []
        if chist is None:
            chist = []

        for xcd, ycd in plot_axes:
            if not self._skip_metric_plot("scatter plot", xcd, ycd):
                self._add_scatter(xcd, ycd, hover_mds)

        for cd in hist:
            if not self._skip_metric_plot("histogram", cd):
                self._add_histogram(cd)

        for cd in chist:
            if not self._skip_metric_plot("cumulative histogram", cd):
                self._add_histogram(cd, cumulative=True)

    def add_fpreview(self, title: str, paths: dict[str, Path], diff: bool = True):
        """
        Add file previews to the data tab (D-tab). Refer to 'FilePreviewBuilder' for more details.

        Args:
            title: The title of the file preview.
            paths: A dictionary containing paths to the files to include in the preview, indexed by
                   report IDs.
            diff: A boolean indicating whether a diff between the files should be generated and
                  included in the file preview.
        """

        fpbuilder = FilePreviewBuilder.FilePreviewBuilder(self._outdir / "file-previews",
                                                          self._basedir, diff=diff)
        self._fpreviews.append(fpbuilder.build_fpreview(title, paths))

    def add_alert(self, alert: str):
        """
        Add an alert to the data tab. Alerts are concise and important messages displayed at the
        top of the data tab HTML page. For example, an alert may explain the reason for a missing
        diagram.

        Args:
            alert: The alert message to be added to the data tab.
        """

        self._alerts.append(alert)

    def build_tab(self) -> BuiltTab.BuiltDTab:
        """
        Build the data tab and return a 'BuiltTab.BuiltDTab' object.

        Returns:
            BuiltTab.BuiltDTab: An object representing the constructed data tab.
        """

        # The relative plot paths.
        rel_ppaths = [path.relative_to(self._basedir) for path in self._ppaths]

        if self._smrytbl is not None:
            smry_path = self._smry_path.relative_to(self._basedir)
        else:
            smry_path = None

        return BuiltTab.BuiltDTab(self.tabname, rel_ppaths, smry_path, self._fpreviews,
                                  self._alerts)
