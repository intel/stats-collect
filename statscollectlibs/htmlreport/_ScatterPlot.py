# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""Provide a class for generating Plotly scatter plots."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import itertools
from pathlib import Path
import numpy
import pandas
import plotly
from pandas.core.dtypes.common import is_datetime64_any_dtype
from pepclibs.helperlibs import Logging
from statscollectlibs.htmlreport import _Plot

# List of diagram markers that we use in scatter plots.
_SCATTERPLOT_MARKERS = ["circle", "square", "diamond", "cross", "triangle-up", "pentagon"]

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class ScatterPlot(_Plot.Plot):
    """Provide functionality for generating Plotly scatter plots."""

    def __init__(self,
                 xcolname: str,
                 ycolname: str,
                 outpath: Path,
                 xaxis_label: str | None = None,
                 yaxis_label: str | None = None,
                 xaxis_unit: str | None = None,
                 yaxis_unit: str | None = None,
                 opacity: float | None = None):
        """
        Initialize a class instance.

        Args:
            xcolname: Name of the dataframe column to use as the X-axis.
            ycolname: Name of the dataframe column to use as the Y-axis.
            outpath: Path for the resultant plot HTML file.
            xaxis_label: Label describing the data plotted on the X-axis, 'xcolname' by default.
            yaxis_label: Label describing the data plotted on the Y-axis, 'ycolname' by default.
            xaxis_unit: The X-axis metric unit.
            yaxis_unit: The Y-axis metric unit.
            opacity: Opacity of the plotly trace. Overrides the project default value if provided.
        """

        super().__init__(xcolname, ycolname, outpath, xaxis_label=xaxis_label,
                         yaxis_label=yaxis_label, xaxis_unit=xaxis_unit, yaxis_unit=yaxis_unit,
                         opacity=opacity)

        self._markers = itertools.cycle(_SCATTERPLOT_MARKERS)

    def reduce_df_density(self, rawdf: pandas.DataFrame, reportid: str):
        """
        Reduce the density of a dataframe to optimize scatter plot rendering.

        Reduce the number of data points in a dataframe to make scatter plots more manageable for
        visualization. Large datasets can result in scatter plots that are too large for web
        browsers to handle effectively. The reduction process retains outliers and proportionally
        scales down dense regions of data.

        Args:
            rawdf: The dataframe containing the data to reduce.
            reportid: The report ID corresponding to the DataFrame.

        Steps:
            1. Divide the scatter plot into NxN bins, where N is the number of bins.
            2. Compute a 2D histogram to determine the number of data points in each bin.
            3. Retain bins with fewer data points (defined by a low threshold) as they likely
               contain outliers.
            4. For bins with many data points, reduce the number of points to a maximum defined by a
               high threshold. Scale the retained points proportionally between the low and high
               thresholds.

        Returns:
            A reduced dataframe containing fewer data points, optimized for scatter plot rendering.
        """

        def _map_non_numeric(colname: str):
            """
            Map a non-numeric column to unique numeric values.

            Reduce the density of a non-numeric column by mapping its unique values to numeric
            identifiers. It checks if the column is scalar, and if not, create a mapping of unique
            values to integers. Apply this mapping to the column and returns the transformed column
            pandas 'Series'.

            Args:
                colname: The name of the column to process.

            Returns:
                A pandas 'Series' where non-numeric values are replaced with unique numeric
                identifiers. If the column is already scalar, it is returned unchanged.
            """

            if not self._is_numeric(df, colname):
                num_rmap = {name: idx for idx, name in enumerate(df[colname].unique())}
                return df[colname].map(num_rmap)
            return df[colname]

        lo_thresh = 10
        hi_thresh = 100
        bins_cnt = 100

        _LOG.info("Reducing density for report ID '%s', diagram '%s vs %s'",
                  reportid, self.yaxis_label, self.xaxis_label)

        # Create a new dataframe with just the X- and Y-columns, which we'll be reducing.
        # It should be a bit more optimal than reducing the bigger original dataframe.
        df = rawdf[[self.xcolname, self.ycolname]]

        xdata = _map_non_numeric(self.xcolname)
        ydata = _map_non_numeric(self.ycolname)

        # Crete a histogram for the columns in question.
        hist, xbins, ybins = numpy.histogram2d(xdata, ydata, bins_cnt)
        # Turn the histogram into a dataframe.
        hist = pandas.DataFrame(hist, dtype=int)

        hist_max = hist.max().max()
        if hist_max <= lo_thresh:
            _LOG.debug("Cancel density reduction: max frequency for '%s vs %s' is %d, but scaling "
                       "threshold is %d", self.yaxis_label, self.xaxis_label, hist_max, lo_thresh)
            return rawdf

        # The histogram scaling factor.
        factor = hi_thresh / hist_max

        # Scale the histogram down. Do not change the buckets with few datapoints (< lo_thresh),
        # scale down all the other buckets so that they would have maximum 'hi_thresh' datapoints.
        hist = hist.map(lambda f: max(int(f * factor), lo_thresh) if f > lo_thresh else f)

        # Create a copy of the histogram, but populate it with zeroes.
        cur_hist = pandas.DataFrame(0, columns=hist.columns, index=hist.index)

        # Calculate bin indexes for all the X and Y values in the dataframe.
        xindeces = numpy.digitize(xdata, xbins[:-1])
        yindeces = numpy.digitize(ydata, ybins[:-1])

        # This is how many datapoints we are going to have in the reduced dataframe.
        reduced_datapoints_cnt = hist.values.sum()
        _LOG.debug("Reduced datapoints count is %d", reduced_datapoints_cnt)

        # Here we'll store 'df' indexes of the rows that will be included into the resulting
        # reduced dataframe.
        copy_cols = []

        for idx in range(0, len(df)):
            xidx = xindeces[idx] - 1
            yidx = yindeces[idx] - 1

            if cur_hist.at[xidx, yidx] >= hist.at[xidx, yidx]:
                continue

            cur_hist.at[xidx, yidx] += 1
            copy_cols.append(idx)

        # Include all the columns in reduced version of the dataframe.
        return rawdf.loc[copy_cols]

    def add_df(self,
               df: pandas.DataFrame,
               legend: str,
               hover_templates: pandas.Series[str] | None = None):
        """
        Add data to the scatter plot.

        Args:
            df: a dataframe containing the data to be plotted.
            legend: The legend (name) for the plotted 'df' data. Scatter plots with multiple sets of
                    data will include a legend indicating which plot points are from which set of
                    data.
            hover_templates: A series (think of it as a list in this context) of plotly-compatible
                             hover text templates, one template for every row in the dataframe. If
                             None, the default hover text will be used.
        """

        # Determine marker size and symbol based on whether the X and Y columns are scalar.
        if self._is_numeric(df, self.xcolname) and self._is_numeric(df, self.ycolname):
            marker_size = 6
            marker_symbol = next(self._markers)
        else:
            marker_size = 30
            marker_symbol = "line-ns"

        # Format datetime columns for human-readable display on axes and hover text.
        for colname, axis in (("xcolname", "xaxis"), ("ycolname", "yaxis")):
            if is_datetime64_any_dtype(df[getattr(self, colname)]):
                self._layout[axis]["tickformat"] = "%H:%M:%S"
                self._layout[axis]["hoverformat"] = "%H:%M:%S"

        # Scale data on the Y-axis to base SI-units if applicable.
        if self.yaxis_baseunit and self.yaxis_unit and self.yaxis_baseunit != self.yaxis_unit:
            ycol: pandas.Series = df[self.ycolname].map(self._scale_yval)
        else:
            ycol = df[self.ycolname]

        # Scale data on the X-axis to base SI-units if applicable.
        if self.xaxis_baseunit and self.xaxis_unit and self.xaxis_baseunit != self.xaxis_unit:
            xcol: pandas.Series = df[self.xcolname].map(self._scale_xval)
        else:
            xcol = df[self.xcolname]

        # Define marker properties.
        marker = {"size": marker_size, "symbol": marker_symbol, "opacity": self.opacity}

        # Create a Plotly Scattergl object and add it to the plot.
        gobj = plotly.graph_objs.Scattergl(x=xcol,
                                           y=ycol,
                                           hovertemplate=hover_templates,
                                           opacity=self.opacity,
                                           marker=marker,
                                           mode="markers",
                                           name=legend)
        self._gobjs.append(gobj)
