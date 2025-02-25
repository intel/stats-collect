# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a data tab.
"""

from pathlib import Path
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs import DFSummary
from statscollectlibs.htmlreport import _Histogram, _ScatterPlot, _SummaryTable
from statscollectlibs.htmlreport.tabs import _Tabs, FilePreviewBuilder

_LOG = Logging.getLogger(f"stats-collect.{__name__}")

def get_fsname(metric):
    """
    Return a file-system and URL-safe name for a metric. The arguments are as follows.
      * metric - name of the metric to return an FS and URL-safe name for.
    """

    # If 'metric' contains "%", we maintain the meaning by replacing with "Percent".
    metric = metric.replace("%", "Percent")

    # Filter out any remaining non-alphanumeric characters.
    metric = "".join([c for c in metric if c.isalnum()])
    return metric

class DTabBuilder:
    """
    This base class provides the capability of populating a data tab.

    Note, each tab element is optional and can be added in any order. See '_Tabs.DTabDC' docstring
    for more information on each tab element.

    Public methods overview:
    1. Add a summary table to the tab.
       * 'add_smrytbl()'
    2. Add plots to the tab.
       * 'add_plots()'
    3. Add file previews to the tab.
       * 'add_fpreviews()'
    4. Add an alert to the tab.
       * 'add_alert()'
    5. Generate a '_Tabs.DTabDC' instance containing all of the tab features added with the methods
       listed above.
       * 'get_tab()'
    """

    def _get_colname(self, md: dict) -> str:
        """
        Return dataframe column name for the metric described by 'md'.

        Args:
            md: the metric definition dictionary

        Returns:
            The dataframe column name.
        """

        if "colname" in md:
            return md["colname"]
        return md["name"]

    def add_smrytbl(self, smry_funcs, mdd):
        """
        Construct a 'SummaryTable' to summarise the metrics in 'smry_funcs' in the results given
        to the constructor as 'reports'. Arguments are as follows.
          * smry_funcs - a dictionary in the format '{metric: summary_func}', for example:
                         {Metric1: ["99.999%", "99.99%",...],
                          Metric2: ["max", "min",...]}
                         Note, 'summary_func' is allowed to be 'None', which means that no functions
                         will be applied to the metric, and can be used for metrics that have only
                         on value.
         * mdd - the metrics definition dictionary describing the metrics in 'smry_funcs'.
        """

        self._smrytbl = _SummaryTable.SummaryTable()

        for metric, funcs in smry_funcs.items():
            md = mdd[metric]
            self._smrytbl.add_metric(md["title"], md.get("short_unit"), md.get("descr"),
                                     fmt="{:.2f}")

            for rep, df in self._dfs.items():
                # Only try to calculate summary values if result 'rep' contains data for the metric.
                if metric not in df:
                    continue
                if funcs:
                    smry_dict = DFSummary.calc_col_smry(df, metric, funcs)
                    for funcname in funcs:
                        self._smrytbl.add_smry_func(rep, md["title"], smry_dict[funcname],
                                                    funcname=funcname)
                else:
                    # Special case: there is only one metric value, so no functions can be applied.
                    if len(df[metric]) > 1:
                        raise Error(f"BUG: no functions were specified for metric '{metric}', "
                                    f"but there is more than one metric value.")
                    val = df[metric][0]
                    self._smrytbl.add_smry_func(rep, md["title"], val, funcname=None)

        try:
            self._smrytbl.generate(self.smry_path)
        except Error as err:
            raise Error("Failed to generate summary table.") from err

    @staticmethod
    def _warn_plot_skip_res(reportid, plottitle, mtitle):
        """
        Helper function for '_add_scatter()' and '_add_histogram()'. Logs when a result is excluded
        from a diagram because it does not have data for the metric with title 'mtitle'.
        """

        _LOG.info("Excluding result '%s' from %s: result does not have data for '%s'.", reportid,
                   plottitle, mtitle)

    def _add_scatter(self, xdef, ydef, hover_defs=None):
        """
        Helper function for 'add_plots()'. Add a scatter plot to the report. Arguments are as
        follows:
         * xdef - definitions dictionary for the metric on the X-axis.
         * ydef - definitions dictionary for the metric on the Y-axis.
         * hover_defs - a mapping between report ID and lists of definitions dictionaries which
                        represent metrics for which hovertext should be generated for that result.
                        By default, only includes hovertext for 'xdef' and 'ydef'.
        """

        xcolname = self._get_colname(xdef)
        ycolname = self._get_colname(ydef)

        # Initialise scatter plot.
        fname = f"{get_fsname(ycolname)}-vs-{get_fsname(xcolname)}.html"
        plottitle = f"scatter plot '{ydef['title']} vs {xdef['title']}'"

        s_path = self._outdir / fname
        s = _ScatterPlot.ScatterPlot(xcolname, ycolname, s_path, xdef.get("title"),
                                     ydef.get("title"), xdef.get("short_unit"),
                                     ydef.get("short_unit"))

        for reportid, df in self._dfs.items():
            for mdef in [xdef, ydef]:
                if self._get_colname(mdef) not in df:
                    self._warn_plot_skip_res(reportid, plottitle, mdef["title"])
                    break
            else:
                reduced_df = s.reduce_df_density(df, reportid)
                if hover_defs is not None:
                    hovertext = s.create_hover_template(hover_defs[reportid], reduced_df)
                else:
                    hovertext = None
                s.add_df(reduced_df, reportid, hovertext)

        s.generate()
        self._ppaths.append(s_path)

    def _add_histogram(self, mdef, cumulative=False, xbins=None):
        """
        Helper function for 'add_plots()'. Add a histogram to the report for metric with
        definitions dictionary 'mdef'. See '_Histogram.Histogram' for details of 'cumulative' and
        'xbins' arguments.
        """

        colname = self._get_colname(mdef)
        if cumulative:
            h_path = self._outdir / f"Percentile-vs-{get_fsname(colname)}.html"
            plottitle = f"cumulative histogram 'Percentile vs {mdef['title']}'"
        else:
            h_path = self._outdir / f"Count-vs-{get_fsname(colname)}.html"
            plottitle = f"histogram 'Count vs {mdef['title']}'"

        h = _Histogram.Histogram(colname, h_path, mdef.get("title"), mdef.get("short_unit"),
                                 cumulative=cumulative, xbins=xbins)

        for reportid, df in self._dfs.items():
            if colname not in df:
                self._warn_plot_skip_res(reportid, plottitle, mdef["title"])
                continue
            h.add_df(df, reportid)

        h.generate()
        self._ppaths.append(h_path)

    def _skip_metric_plot(self, plotname, xdef, ydef=None):
        """
        Helper function for 'add_plots()'. Checks the data in 'self._dfs' to see if there is
        sufficient data to generate a plot for the metrics 'xdef' and 'ydef'. Returns 'True' or
        'False' if the plot should be skipped or generated respectively.
        """

        if ydef is not None:
            mdefs = [xdef, ydef]
            plotname = f"{plotname} '{ydef['name']} vs {xdef['name']}'"
        else:
            mdefs = [xdef]
            plotname = f"{plotname} '{xdef['name']}'"

        for mdef in mdefs:
            colname = self._get_colname(mdef)

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

    def add_plots(self, plot_axes=None, hist=None, chist=None, hover_defs=None):
        """
        Initialise the plots and populate them using the 'pandas.DataFrame' objects in 'self._dfs'.
        The arguments are as follows.
         * plot_axes - tuples of defs which represent axes to create scatter plots for in the format
                       (xdef, ydef).
         * hist - a list of defs which represent metrics to create histograms for.
         * chist - a list of defs which represent metrics to create cumulative histograms for.
         * hover_defs - a mapping from 'reportid' to defs of metrics which should be included in
                        the hovertext of scatter plots.
        """

        if plot_axes is None and hist is None and chist is None:
            raise Error("BUG: no arguments provided for 'add_plots()', unable to generate plots")

        if plot_axes is None:
            plot_axes = []
        if hist is None:
            hist = []
        if chist is None:
            chist = []

        for xdef, ydef in plot_axes:
            if not self._skip_metric_plot("scatter plot", xdef, ydef):
                self._add_scatter(xdef, ydef, hover_defs)

        for mdef in hist:
            if not self._skip_metric_plot("histogram", mdef):
                self._add_histogram(mdef)

        for mdef in chist:
            if not self._skip_metric_plot("cumulative histogram", mdef):
                self._add_histogram(mdef, cumulative=True)


    def add_fpreview(self, title: str, paths: dict[str, Path], diff: bool = True):
        """
        Add file previews to the D-tab. Refer to 'FilePreviewBuilder' for more information.

        Args:
            title: the file preview title.
            paths: paths to the files to include to the preview (a dictionary containing the paths
                   and indexed by report IDs).
            diff: whether the diff between the files should be generated and added to the file
                  preview.
        """

        fpbuilder = FilePreviewBuilder.FilePreviewBuilder(self._outdir / "file-previews",
                                                          self._basedir, diff=diff)
        self.fpreviews.append(fpbuilder.build_fpreview(title, paths))

    def add_alert(self, alert):
        """Add an alert to the data tab."""

        self._alerts.append(alert)

    def get_tab(self):
        """
        Return a '_Tabs.DTabDC' instance which contains an aggregate of all of the data 'self._dfs'.
        Return a '_Tabs.DTabDC' object that can be used to populate an HTML tab.
        """

        ppaths = [p.relative_to(self._basedir) for p in self._ppaths]

        if self._smrytbl is not None:
            smry_path = self.smry_path.relative_to(self._basedir)
        else:
            smry_path = ""

        return _Tabs.DTabDC(self.tabname, ppaths, smry_path, self.fpreviews, self._alerts)

    def __init__(self, dfs, outdir, tabname, basedir=None):
        """
        The class constructor. Adding a data tab will create a sub-directory named after the metric
        in 'metric_def' and store plots and the summary table in it.

        Arguments are the same as in '_TabBuilderBase.TabBuilderBase()' except for the following:
         * dfs - dictionary containing indexed by report ID with values being the dataframe
                 including the data for the tab.
         * tabname - the name of the tab. See 'DTabDC.name' for more information.
        """

        self._dfs = dfs
        self.tabname = tabname
        # File system-friendly tab name.
        self._fsname = get_fsname(self.tabname)

        self._outdir = outdir / self._fsname
        self.smry_path = self._outdir / "summary-table.txt"
        self._smrytbl = None

        # Sometimes certain metrics cause diagrams to be skipped. See '_skip_metric_plot()' for more
        # info. Add alerts to '_alerts' to inform the user why some diagrams have been skipped.
        self._alerted_metrics = set() # Avoid alerting the user of a metric multiple times.
        self._alerts = []

        if basedir is None:
            self._basedir = outdir
        else:
            self._basedir = basedir

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create directory '{self._outdir}':\n{msg}") from None

        # Paths of plots generated for this tab.
        self._ppaths = []

        # Instances of '_Tabs.FilePreview' which will be generated with the tab.
        self.fpreviews = []
