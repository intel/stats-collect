# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""Provide a base class for Plotly diagrams used in HTML reports."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
import pandas
import plotly
from pandas.core.dtypes.common import is_numeric_dtype, is_datetime64_any_dtype
from pepclibs.helperlibs import Logging, Human, Trivial
from pepclibs.helperlibs.Exceptions import Error

if typing.TYPE_CHECKING:
    from typing import Union, Any, Sequence
    from statscollectlibs.mdc.MDCBase import MDTypedDict

    class CDTypedDict(MDTypedDict, total=False):
        """
        The column definition for a dataframe column. It is same as the metrics definition
        'MDTypedDict', but describes a dataframe column, like "CPU0-PkgPower".

        Attributes:
            colname: Column name the definition describes.
            sname: Column scope, for example "System" or "CPU0".
        """

        colname: str
        sname: str

    _PlotlyGraphObjectType = Union[plotly.graph_objs.Scatter, plotly.graph_objs.Histogram]

# Default plotly diagram layout configuration.
_FONTFMT = {"family": "Arial, sans-serif",
            "size": 18,
            "color": "black"}
_AXIS = {"hoverformat": ".3s",
         "showline": True,
         "showgrid": True,
         "ticks": "outside",
         "tickwidth": 1,
         "tickformat": ".3s",
         "showticklabels": True,
         "linewidth": 1,
         "linecolor": "black",
         "zeroline": True,
         "zerolinewidth": 1,
         "zerolinecolor": "black"}
_LEGEND = {"font": {"size" : 14},
           "bgcolor": "#E2E2E2",
           "borderwidth": 2,
           "bordercolor": "#FFFFFF",
           "orientation": "h",
           "xanchor": "right",
           "yanchor": "bottom",
           "x": 1,
           "y": 1}

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class Plot:
    """Base class for Plotly diagrams used in HTML reports."""

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

        self.xcolname = xcolname
        self.ycolname = ycolname
        self.outpath = outpath

        # '_gobjs' contains plotly "Graph Objects". This attribute holds the data for each
        # 'self.add_df()' call. Then the data is aggregated for the final diagram during the
        # 'self.generate()' stage.
        self._gobjs: list[_PlotlyGraphObjectType] = []

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

    def _scale_xval(self, val: int | float) -> int | float:
        """
        Scale an X-axis value to a base SI-unit.

        Args:
            val: the value to scale.

        Returns:
            The scaled value.
        """

        return Human.scale_si_val(val, self.xaxis_unit)

    def _scale_yval(self, val: int | float) -> int | float:
        """
        Scale n Y-axis value to a base SI-unit.

        Args:
            val: the value to scale.

        Returns:
            The scaled value.
        """

        return Human.scale_si_val(val, self.yaxis_unit)

    def add_df(self,
               df: pandas.DataFrame,
               legend: str,
               hover_templates: pandas.Series[str] | None = None):
        """
        Add data to the plot.

        Args:
            df: a dataframe containing the data to be plotted.
            legend: The legend (name) for the plotted data.
            hover_templates: A series (think of it as a list in this context) of plotly-compatible
                             hover text templates, one template for every row in the dataframe. If
                             None, the default hover text will be used.

        Raises:
            NotImplementedError: This is not provided by the subclass.
        """

        raise NotImplementedError()

    def _create_hover_template(self,
                               row: pandas.Series,
                               hover_cds: list[CDTypedDict]) -> str:
        """
        Create a hover template string for a dataframe row. Called by the 'df.apply()' method.

        Args:
            row: The dataframe row to create the template for.
            hover_cds: A dictionary of column definitions for the columns to include in the hover
                       template.

        Returns:
            A Plotly-compatible hover template string for the given row.
        """

        template = "(%{x}, %{y})<br>"

        # Decimal places to provide in formatted hover text.
        decp = 2

        for hover_cd in hover_cds:
            colname = hover_cd["colname"]

            # Skip X-axis and Y-axis columns, which are already included in the hover template.
            if hover_cd["title"] == self.xaxis_label or hover_cd["title"] == self.yaxis_label:
                continue

            short_unit = hover_cd.get("short_unit")
            if not Trivial.is_num(row[colname]):
                # If the value is not numeric, use it as-is.
                val = row[colname]
            elif short_unit == "%":
                # Format percentage values with the specified decimal places.
                val = f"{row[colname]:.{decp}f}"
            else:
                val = Human.num2si(row[colname], unit=short_unit, decp=decp)

            template += f"{hover_cd['name']}: {val}<br>"

        return template

    def create_hover_templates(self,
                               hover_cds: Sequence[CDTypedDict],
                               df: pandas.DataFrame) -> pandas.Series[str]:
        """
        Create and return a list of Plotly-compatible hover template strings.

        Args:
            hover_cds: A list of column definitions for the columns to include in the hover
                       template.
            df: The dataframe that includes all columns in 'hover_cds'.

        Returns:
            A series (think about it as a list in this context) of hover text column templates, one
            for every row in 'df'.

        Example:
            Suppose 'hover_cds' contains the definitions for the 'PkgWatt' and 'Busy%" metrics. And
            the 'df' dataframe includes 2 rows with the following values:
                Row 0: PkgWatt = 50.0, Busy% = 0.5, TimeElapsed = 1000, OtherMetric = 0.1
                Row 1: PkgWatt = 60.0, Busy% = 9.0, TimeElapsed = 2000, OtherMetric = 2.2

            The resulting hover templates series will look like this:
                ["(%{x}, %{y})<br>PkgWatt: 50.0<br>Busy%: 0.5<br>",
                 "(%{x}, %{y})<br>PkgWatt: 60.0<br>Busy%: 9.0<br>"]
        """

        _LOG.debug("Preparing hover text for '%s vs %s'", self.ycolname, self.xcolname)

        new_hover_cds: list[CDTypedDict] = []

        for hover_cd in hover_cds:
            colname = hover_cd["colname"]
            if colname not in df.columns:
                # Skip columns not present in the dataframe.
                continue

            # Exclude metrics with constant values from the hover text for optimization.
            # Check for this by comparing the column data points ti the first column data point.
            sample = df[colname].iloc[0]
            if all(dp == sample for dp in df[colname]):
                continue

            new_hover_cds.append(hover_cd)

        # Apply '_create_hover_template' to each row of the dataframe.
        return df.apply(self._create_hover_template, axis=1, args=(new_hover_cds,))

    @staticmethod
    def _is_numeric(df: pandas.DataFrame, colname: str) -> bool:
        """
        Determine if a column in a dataframe contains only numeric data.

        Args:
            df: The dataframe to check.
            colname: The column name to check.

        Returns:
            True if the column consists only of scalar data (e.g., numbers, or datetime), False
            otherwise.
        """

        # Treat datetime columns as numeric.
        if is_datetime64_any_dtype(df[colname]):
            return True

        # Check if the column contains numeric data, excluding boolean types.
        return is_numeric_dtype(df[colname]) and df[colname].dtype != 'bool'

    def generate(self):
        """
        Generate all the configured Plotly diagrams and save them in 'self.outpath'.
        """

        try:
            fig = plotly.graph_objs.Figure(data=self._gobjs, layout=self._layout)
            fig.update_layout(template="plotly_white")

            _LOG.info("Generating plot: %s vs %s.", self.yaxis_label, self.xaxis_label)

            plotly.offline.plot(fig, filename=str(self.outpath), auto_open=False,
                                config={"showLink": False})
        except Exception as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Failed to create the '{self.outpath}' diagram:\n{msg}") from err

    def _configure_layout(self) -> dict[str, Any]:
        """
        Create and return a Plotly dagram layout configuration based on the parameters provided to
        the constructor.
        """

        xaxis = {**_AXIS,
                 "ticksuffix": self.xaxis_baseunit if self.xaxis_baseunit else self.xaxis_unit,
                 "title": {"text": self.xaxis_label, "font": _FONTFMT}}

        # The default axis configuration uses an SI prefix for units (e.g. ms, ks, etc.). For units
        # which do not support SI prefixes (such as '%'), format the value with 3 significant digits
        # figures and do not include an SI prefix.
        if not self.xaxis_baseunit:
            fmt = ".3r"
            xaxis["tickformat"] = fmt
            xaxis["hoverformat"] = fmt

        yaxis = {**_AXIS,
                 "ticksuffix": self.yaxis_baseunit if self.yaxis_baseunit else self.yaxis_unit,
                 "title": {"text": self.yaxis_label, "font": _FONTFMT}}

        # Similar to the X-axis, handle units that do not support SI prefixes for the Y-axis.
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
