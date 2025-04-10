# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""Provide a class for generating Plotly histograms."""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from typing import TypedDict
import pandas
import plotly
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport import _Plot

class XBinsTypedDict(TypedDict, total=False):
    """
    The typed dictionary for histogram bin configuration.

    Attributes:
        start: The starting value for the bins.
        end: The end value for the bins.
        size: The size of each bin.
    """

    start: int | float
    end: int | float
    size: int | float

class Histogram(_Plot.Plot):
    """Provide functionality for generating Plotly histograms."""

    def __init__(self,
                 xcolname: str,
                 outpath: Path,
                 xaxis_label: str | None = None,
                 xaxis_unit: str | None = None,
                 opacity: float | None = None,
                 xbins: XBinsTypedDict | None = None,
                 cumulative: bool = False):
        """
        Initialize a Histogram instance.

        Args:
            xcolname: Name of the dataframe column to be plotted in the X-axis of the histogram.
            outpath: Path to save the resulting plot HTML file.
            xaxis_label: Label (title) for the X-axis. Defaults to 'xcolname' if not provided.
            xaxis_unit: Unit of measurement for the X-axis.
            opacity: Opacity of the plotly trace. Overrides the project default if specified.
            xbins: Dictionary defining histogram bins, passed directly to the plotly Histogram
                   constructor.
            cumulative: If 'True', the histogram will be cumulative (displaying percentiles on the
                        Y-axis instead of counts).
        """

        self.xbins = xbins
        self.cumulative = cumulative

        if cumulative:
            ycolname = "Percentile"
            yaxis_unit = "%"
        else:
            ycolname = "Count"
            yaxis_unit = None

        super().__init__(xcolname, ycolname, outpath, xaxis_label=xaxis_label,
                         xaxis_unit=xaxis_unit, yaxis_unit=yaxis_unit, opacity=opacity)

    def add_df(self,
               df: pandas.DataFrame,
               legend: str,
               hover_templates: pandas.Series[str] | None = None):
        """
        Add data to the histogram.

        Args:
            df: a dataframe containing the data to be plotted.
            legend: The legend (name) for the plotted 'df' data. Histograms with multiple sets of
                    data will include a legend indicating which plot points are from which set of
                    data.
            hover_templates: A series (think of it as a list in this context) of plotly-compatible
                             hover text templates, one template for every row in the dataframe. If
                             None, the default hover text will be used.
        """

        # Scale data on the X-axis to base SI-units if applicable.
        if self.xaxis_baseunit and self.xaxis_unit:
            xcol: pandas.Series = df[self.xcolname].map(self._scale_xval)
        else:
            xcol = df[self.xcolname]

        try:
            if self.cumulative:
                gobj = plotly.graph_objs.Histogram(x=xcol, name=legend, xbins=self.xbins,
                                                   cumulative={"enabled": True}, histnorm="percent",
                                                   opacity=self.opacity)
            else:
                gobj = plotly.graph_objs.Histogram(x=xcol, name=legend, xbins=self.xbins,
                                                   opacity=self.opacity,
                                                   hovertemplate=hover_templates)
        except Exception as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Failed to create histogram 'count-vs-{self.xcolname}':\n{msg}") from err

        self._gobjs.append(gobj)
