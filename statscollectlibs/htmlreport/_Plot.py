# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the common defaults and logic for producing plotly diagrams."""

import plotly
from pandas.core.dtypes.common import is_numeric_dtype, is_datetime64_any_dtype
from pepclibs.helperlibs import Logging, Human, Trivial
from pepclibs.helperlibs.Exceptions import Error

# Default plotly diagram layout configuration.

_FONTFMT = {"family" : "Arial, sans-serif",
            "size"   : 18,
            "color"  : "black"}

_AXIS = {"hoverformat" : ".3s",
         "showline"  : True,
         "showgrid"  : True,
         "ticks"     : "outside",
         "tickwidth" : 1,
         "tickformat" : ".3s",
         "showticklabels" : True,
         "linewidth" : 1,
         "linecolor" : "black",
         "zeroline" : True,
         "zerolinewidth" : 1,
         "zerolinecolor" : "black"}

_LEGEND = {"font"    : {"size" : 14},
           "bgcolor" : "#E2E2E2",
           "borderwidth" : 2,
           "bordercolor" : "#FFFFFF",
           "orientation": "h",
           "xanchor": "right",
           "yanchor": "bottom",
           "x": 1,
           "y": 1}

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class Plot:
    """This class provides the common defaults and logic for producing plotly diagrams."""

    def _create_hover_template_col(self, row, hover_mds, df):
        """
        Helper function for 'create_hover_template()'. Returns the hover template for a given 'row'
        of a 'pandas.DataFrame'.
        """

        templ = "(%{x}, %{y})<br>"

        # Decimal places to provide in formatted hover text.
        decp = 2

        for hover_md in hover_mds:
            colname = hover_md["colname"]
            if colname not in df.columns:
                continue

            # Metrics on the X-axis and Y-axis will be included at the beginning of the hovertext.
            if (hover_md["title"] == self.xaxis_label) or (hover_md["title"] == self.yaxis_label):
                continue

            short_unit = hover_md.get("short_unit")
            if not Trivial.is_num(row[colname]):
                val = row[colname]
            elif short_unit == "%":
                val = f"{row[colname]:.{decp}f}"
            else:
                val = Human.num2si(row[colname], unit=short_unit, decp=decp)

            templ += f"{hover_md['name']}: {val}<br>"

        return templ

    def create_hover_template(self, hover_mds, df):
        """
        Create and return a 'plotly'-compatible hover template for the 'pandas.DataFrame' 'df'.
        Arguments are as follows:
         * hover_mds - a list of metric definition dictionaries to include in the hover template.
         * df - the 'pandas.DataFrame' which contains the datapoints to label.
        """

        _LOG.debug("Preparing hover text for '%s vs %s'", self.ycolname, self.xcolname)

        hovertemplate = df.apply(self._create_hover_template_col, axis=1,
                                 args=(hover_mds, df))
        return hovertemplate

    @staticmethod
    def _is_scalar_col(df, colname):
        """
        Returns 'True' if column 'colname' in 'pandas.DataFrame' 'df' consists of scalar data,
        otherwise returns 'False'.  Helper for child classes to dictate styling based on whether a
        column is scalar or not.
        """

        # Date-time data is used in time-series and therefore as scalar data.
        if is_datetime64_any_dtype(df[colname]):
            return True

        # Pandas 'is_numeric_dtype' function returns 'True' if the column datatype is numeric or a
        # boolean. This function returns the same as the pandas function unless the datatype is a
        # boolean, in which case it returns False.
        return is_numeric_dtype(df[colname]) and df[colname].dtype != 'bool'

    def add_df(self, df, legend, hover_template=None):
        """
        Add a dataframe of data to the plot.

        Args:
            df: a dataframe containing the data to be plotted.
            legend: The legend (name) for the plotted 'df' data. Scatter plots with multiple sets of
                    data will include a legend indicating which plot points are from which set of
                    data.
            hover_template: A plotly-compatible hover text template for the datapoints.
        """

        raise NotImplementedError()

    def generate(self):
        """
        Generates a plotly diagram based on the data in all instances of 'pandas.DataFrame' saved
        with 'self.add_df()'. Then saves it to a file at the output path 'self.outpath'.
        """

        try:
            fig = plotly.graph_objs.Figure(data=self._gobjs, layout=self._layout)
            if hasattr(fig, "update_layout") and fig.update_layout:
                # In plotly version 4 the default theme has changed. The old theme is called
                # 'plotly_white'. Use it to maintain consistent look for plotly v3 and v4.
                fig.update_layout(template="plotly_white")

            _LOG.info("Generating plot: %s vs %s.", self.yaxis_label, self.xaxis_label)
            plotly.offline.plot(fig, filename=str(self.outpath), auto_open=False,
                                config={"showLink" : False})
        except Exception as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create the '{self.outpath}' diagram:\n{msg}") from err

    def _configure_layout(self):
        """
        Creates and returns a plotly layout configuration using the parameters provided to the
        constructor.
        """

        xaxis = {**_AXIS,
                 "ticksuffix": self.xaxis_baseunit if self.xaxis_baseunit else self.xaxis_unit,
                 "title": {"text": self.xaxis_label, "font": _FONTFMT}}

        # The default axis configuration uses an SI prefix for units (e.g. ms, ks, etc.).  For units
        # which do not support SI prefixes (such as '%'), just round the value to 3 significant
        # figures and do not include an SI prefix.
        if not self.xaxis_baseunit:
            fmt = ".3r"
            xaxis["tickformat"] = fmt
            xaxis["hoverformat"] = fmt

        yaxis = {**_AXIS,
                 "ticksuffix": self.yaxis_baseunit if self.yaxis_baseunit else self.yaxis_unit,
                 "title": {"text": self.yaxis_label, "font": _FONTFMT}}

        # See comment above regarding SI prefixes. Here we do the same but for the Y-axis.
        if not self.yaxis_baseunit:
            fmt = ".3r"
            yaxis["tickformat"] = fmt
            yaxis["hoverformat"] = fmt

        layout = {"showlegend"  : True,
                  "hovermode"   : "closest",
                  "xaxis"   : xaxis,
                  "yaxis"   : yaxis,
                  "barmode" : "overlay",
                  "bargap"  : 0,
                  "legend"  : _LEGEND}
        return layout

    def __init__(self, xcolname, ycolname, outpath, xaxis_label=None, yaxis_label=None,
                 xaxis_unit=None, yaxis_unit=None, opacity=None):
        """
        The class constructor. The arguments are as follows.
         * xcolname - name of the column to use as the X-axis.
         * ycolname - name of the column to use as the Y-axis.
         * outpath - desired filepath of resultant plot HTML.
         * xaxis_label - label which describes the data plotted on the X-axis.
         * yaxis_label - label which describes the data plotted on the Y-axis.
         * xaxis_unit - the unit provided will be appended as a suffix to datapoints and along the
                        X-axis.
         * yaxis_unit - same as 'xaxis_unit', but for Y-axis.
         * opacity - opacity of the plotly trace, will be passed directly to plotly. Can be
                     used for overriding the project default value.
        """

        self.xcolname = xcolname
        self.ycolname = ycolname
        self.outpath = outpath

        self._formats = {}

        # 'gobjs' contains plotly "Graph Objects". This attribute stores the data from each
        # 'self.add_df()' call. Then the data is aggregated for the final diagram during the
        # 'self.generate()' stage.
        self._gobjs = []

        self.xaxis_label = xaxis_label if xaxis_label else xcolname
        self.yaxis_label = yaxis_label if yaxis_label else ycolname
        self.xaxis_unit = xaxis_unit if xaxis_unit else ""
        self.yaxis_unit = yaxis_unit if yaxis_unit else ""
        _, xaxis_baseunit = Human.separate_si_prefix(self.xaxis_unit)
        self.xaxis_baseunit = xaxis_baseunit if xaxis_baseunit in Human.SUPPORTED_UNITS else None
        _, yaxis_baseunit = Human.separate_si_prefix(self.yaxis_unit)
        self.yaxis_baseunit = yaxis_baseunit if yaxis_baseunit in Human.SUPPORTED_UNITS else None
        self.opacity = opacity if opacity else 0.8

        self._layout = self._configure_layout()
