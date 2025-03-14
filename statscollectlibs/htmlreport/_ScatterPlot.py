# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the functionality for producing plotly scatter plots."""

import itertools
import numpy
import pandas
import plotly
from pandas.core.dtypes.common import is_datetime64_any_dtype
from pepclibs.helperlibs import Logging, Human
from statscollectlibs.htmlreport import _Plot

# List of diagram markers that we use in scatter plots.
_SCATTERPLOT_MARKERS = ["circle", "square", "diamond", "cross", "triangle-up", "pentagon"]

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class ScatterPlot(_Plot.Plot):
    """This class provides the functionality to generate plotly scatter plots."""

    def reduce_df_density(self, rawdf, reportid):
        """
        Reduce the density of a 'pandas.DataFrame' object. The arguments are as follows.
          * rawdf - the raw wult data 'pandas.DataFrame' object to reduce.
          * reportid - the ReportID corresponding to the dataframe.

        The problem: the raw data dataframe may be large (say, 10000000 datapoint), resulting in a
        large plotly scatter plot (gigabytes in size), and the web browser simply refuses to display
        it.

        Observation: there are many "uninteresting" datapoints per one "interesting" datapoint (an
        outlier) in the raw results dataframe.

        Solution:
        1. Split the scatter plot on NxN squares, where N is the bins count.
        2. Calculate how many datapoints each square contains (the 2D histogram).
        3. If a square has few datapoints, these are outliers, we leave them alone. "Few" is defined
           by the "low threshold" value.
        4. The for the squares containing many datapoints, we do the reduction. We basically drop
           the datapoints and leave maximum "high threshold" amount of datapoints. And we try to
           scale the amount of datapoints left proportionally to the original value between the
           values of ("low threshold", "high threshold").
        """

        def _map_non_numeric(colname):
            """
            In order to reduce density for a non-numeric column, we need to map that column to
            unique numbers, find datapoints to keep, and then reduce the 'pandas.DataFrame'. This
            function does exactly that - maps a non-numeric column 'colname' to unique numbers and
            returns the corresponding pandas series object.
            """

            if not self._is_scalar_col(df, colname):
                num_rmap = {name: idx for idx, name in enumerate(df[colname].unique())}
                return df[colname].map(num_rmap)

            return df[colname]

        lo_thresh = 20
        hi_thresh = 200
        bins_cnt = 100

        _LOG.info("Reducing density for report ID '%s', diagram '%s vs %s'",
                  reportid, self.yaxis_label, self.xaxis_label)

        # Create a new 'pandas.DataFrame' with just the X- and Y-columns, which we'll be reducing.
        # It should be a bit more optimal than reducing the bigger original 'pandas.DataFrame'.
        df = rawdf[[self.xcolname, self.ycolname]]

        xdata = _map_non_numeric(self.xcolname)
        ydata = _map_non_numeric(self.ycolname)

        # Crete a histogram for the columns in question.
        hist, xbins, ybins = numpy.histogram2d(xdata, ydata, bins_cnt)
        # Turn the histogram into a 'pandas.DataFrame'.
        hist = pandas.DataFrame(hist, dtype=int)

        hist_max = hist.max().max()
        if hist_max <= lo_thresh:
            _LOG.debug("cancel density reduction: max frequency for '%s vs %s' is %d, but scaling "
                       "threshold is %d", self.yaxis_label, self.xaxis_label, hist_max, lo_thresh)
            return rawdf

        # The histogram scaling factor.
        factor = hi_thresh / hist_max

        # Scale the histogram down. Do not change the buckets with few datapoints (< lo_thresh),
        # scale down all the other buckets so that they would have maximum 'hi_thresh' datapoints.
        hist = hist.map(lambda f: max(int(f * factor), lo_thresh) if f > lo_thresh else f)

        # Create a copy of the histogram, but populate it with zeroes.
        cur_hist = pandas.DataFrame(0, columns=hist.columns, index=hist.index)

        # Calculate bin indexes for all the X and Y values in the 'pandas.DataFrame'.
        xindeces = numpy.digitize(xdata, xbins[:-1])
        yindeces = numpy.digitize(ydata, ybins[:-1])

        # This is how many datapoints we are going to have in the reduced 'pandas.DataFrame'.
        reduced_datapoints_cnt = hist.values.sum()
        _LOG.debug("reduced datapoints count is %d", reduced_datapoints_cnt)

        # Here we'll store 'df' indexes of the rows that will be included into the resulting
        # reduced 'pandas.DataFrame'.
        copy_cols = []

        for idx in range(0, len(df)):
            xidx = xindeces[idx] - 1
            yidx = yindeces[idx] - 1

            if cur_hist.at[xidx, yidx] >= hist.at[xidx, yidx]:
                continue

            cur_hist.at[xidx, yidx] += 1
            copy_cols.append(idx)

        # Include all the columns in reduced version of the 'pandas.DataFrame'.
        return rawdf.loc[copy_cols]

    def add_df(self, df, name, hover_template=None):
        """
        Add a 'pandas.DataFrame' of data to the scatter plot.
         * df - 'pandas.DataFrame' containing the data to be plotted.
         * name - the legend name (scatter plots with multiple sets of data will include a legend
                  indicating which plot points are from which set of data).
         * hover_template - a 'plotly'-compatible hover text template for each datapoint.
        """

        # Non-numeric columns will have only few unique values, e.g. 'ReqState' might have
        # "C1", "C1E" and "C6". Using dotted markers for such data will have 3 thin lines
        # which is hard to see. Improve it by using line markers to turn lines into wider
        # "bars".
        if self._is_scalar_col(df, self.xcolname) and self._is_scalar_col(df, self.ycolname):
            marker_size = 4
            marker_symbol = next(self._markers)
        else:
            marker_size = 30
            marker_symbol = "line-ns"

        # If the data passed is an instance of 'datetime' then it should be formatted in a
        # human-readable way on the axes and hover text.
        for colname, axis in (("xcolname", "xaxis"), ("ycolname", "yaxis")):
            if is_datetime64_any_dtype(df[getattr(self, colname)]):
                self._layout[axis]["tickformat"] = "%H:%M:%S"
                self._layout[axis]["hoverformat"] = "%H:%M:%S"

        # If data on x/y axis can be scaled to a base SI-unit, do it to let 'plotly' handle SI-unit
        # prefixes for every datapoint.
        if self.yaxis_baseunit and self.yaxis_unit:
            ycol = Human.scale_si_val(df[self.ycolname], self.yaxis_unit)
        else:
            ycol = df[self.ycolname]

        if self.xaxis_baseunit and self.xaxis_unit:
            xcol = Human.scale_si_val(df[self.xcolname], self.xaxis_unit)
        else:
            xcol = df[self.xcolname]

        marker = {"size" : marker_size, "symbol" : marker_symbol, "opacity" : self.opacity}
        gobj = plotly.graph_objs.Scattergl(x=xcol, y=ycol, hovertemplate=hover_template,
                                           opacity=self.opacity, marker=marker, mode="markers",
                                           name=name)
        self._gobjs.append(gobj)

    def __init__(self, xcolname, ycolname, outpath, xaxis_label=None, yaxis_label=None,
                 xaxis_unit=None, yaxis_unit=None, opacity=None):
        """
        The class constructor. The arguments are as follows.
         * xcolname - same as in '_Plot.__init__()'.
         * ycolname - same as in '_Plot.__init__()'.
         * outpath - same as in '_Plot.__init__()'.
         * xaxis_label - same as in '_Plot.__init__()'.
         * yaxis_label - same as in '_Plot.__init__()'.
         * xaxis_unit - same as in '_Plot.__init__()'.
         * yaxis_unit - same as in '_Plot.__init__()'.
         * opacity - same as in '_Plot.__init__()'.
        """

        super().__init__(xcolname, ycolname, outpath, xaxis_label=xaxis_label,
                         yaxis_label=yaxis_label, xaxis_unit=xaxis_unit, yaxis_unit=yaxis_unit,
                         opacity=opacity)

        self._markers = itertools.cycle(_SCATTERPLOT_MARKERS)
