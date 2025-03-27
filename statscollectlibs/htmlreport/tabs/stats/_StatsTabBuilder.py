# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""Provide the API to generate a 'Stats' container tab."""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from typing import Union, Type
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorBadFormat
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.htmlreport.tabs.stats import _TurbostatTabBuilder, _InterruptsTabBuilder
from statscollectlibs.htmlreport.tabs.stats import _ACPowerTabBuilder, _IPMITabBuilder
from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoTabBuilder
from statscollectlibs.htmlreport.tabs.TabConfig import CTabConfig
from statscollectlibs.result.LoadedResult import LoadedResult

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

_TabBuilderClassType = Union[Type[_TurbostatTabBuilder.TurbostatTabBuilder],
                             Type[_InterruptsTabBuilder.InterruptsTabBuilder],
                             Type[_ACPowerTabBuilder.ACPowerTabBuilder],
                             Type[_IPMITabBuilder.IPMITabBuilder]]

_TabBuilderType = Union[_TurbostatTabBuilder.TurbostatTabBuilder,
                        _InterruptsTabBuilder.InterruptsTabBuilder,
                        _ACPowerTabBuilder.ACPowerTabBuilder,
                        _IPMITabBuilder.IPMITabBuilder]
class StatsTabBuilder:
    """Provide the API to generate a 'Stats' container tab."""

    name = "Stats"

    def __init__(self,
                 lrsts: list[LoadedResult],
                 outdir: Path,
                 basedir: Path | None = None,
                 xmetric: str | None = None):
        """
        Initialize a class instance.

        Args:
            lrsts: list of loaded test result objects to generate the statistics tabs for.
            outdir: The output directory path to store that tabs data in.
            basedir: The base directory path (the 'outdir' should be a sub-path of 'basedir').
            xmetric: Name of the metric to use for the X-axis of the plots. If not provided, the
                     X-axis will use the time elapsed since the beginning of the measurements.
        """

        self._lrsts = lrsts
        self._outdir = outdir
        self._basedir = basedir if basedir else outdir
        self._xmetric = xmetric

        self._tbldrs: dict[str, _TabBuilderType] = {}

        self._init_tab_bldrs()

    def get_default_tab_cfgs(self) -> dict[str, CTabConfig]:
        """
        Get the default statistics tabs configuration.

        Returns:
            A dictionary containing the default tab configurations for all statistics in the format
            '{stname: CTabConfig}'.
        """

        return {stname: tbldr.get_default_tab_cfg() for stname, tbldr in self._tbldrs.items()}

    def get_tab(self, tab_cfgs: dict[str, CTabConfig] | None = None) -> _Tabs.CTabDC:
        """
        Generate and return the the statistics container tab (the top-level "Stats" tab in the HTML
        report).

        Args:
            tab_cfgs: A dictionary of tab configurations, where the key is the statistics collector
                      name and the value is the configuration for that tab.

        Returns:
            _Tabs.CTabDC: The generated statistics container tab.
        """

        if tab_cfgs is None:
            tab_cfgs = {}

        tabs = []
        for stname, tbldr in self._tbldrs.items():
            _LOG.info("Generating '%s' tab.", tbldr.name)
            try:
                tab_cfg = tab_cfgs.get(stname)
                tabs.append(tbldr.get_tab(tab_cfg=tab_cfg))
            except Error as err:
                _LOG.debug_print_stacktrace()
                _LOG.warning("Failed to generate '%s' tab: %s", tbldr.name, err)
                continue

        if not tabs:
            _LOG.warning("All statistics tabs were skipped")

        return _Tabs.CTabDC(self.name, tabs)

    def _init_tab_bldrs(self):
        """Initialise tab builder objects."""

        classes_list: list[_TabBuilderClassType] = [_TurbostatTabBuilder.TurbostatTabBuilder,
                                                    _InterruptsTabBuilder.InterruptsTabBuilder,
                                                    _IPMITabBuilder.IPMITabBuilder,
                                                    _ACPowerTabBuilder.ACPowerTabBuilder]

        classes_dict: dict[str, _TabBuilderClassType] = {}

        for a_class in classes_list:
            assert a_class.stnames
            for stname in a_class.stnames:
                classes_dict[stname] = a_class

        collected_stnames = set.union(*[set(lres.res.info["stinfo"]) for lres in self._lrsts])
        supported_stnames = set(stname for stname in collected_stnames if stname in classes_dict)

        # The "sysinfo" tab is processes separately. TODO: can it be processed similar way?
        sysinfo_stnames = set(_SysInfoTabBuilder.SysInfoTabBuilder.stnames)

        missing_tab_builders = collected_stnames - supported_stnames - sysinfo_stnames
        if missing_tab_builders:
            _LOG.warning("The following statistics are not supported for HTML reports: %s",
                         ", ".join(missing_tab_builders))

        if not supported_stnames:
            raise ErrorNotFound("No supported statistics found")

        _LOG.info("Generating tabs for the following statistics: %s", ", ".join(supported_stnames))

        stats_dir = self._outdir / self.name

        _initialized_classes: dict[_TabBuilderClassType, str] = {}

        for stname, tab_builder_class in classes_dict.items():
            if stname not in supported_stnames:
                continue

            if tab_builder_class in _initialized_classes:
                same_class_stname =  _initialized_classes[tab_builder_class]
                self._tbldrs[stname] = self._tbldrs[same_class_stname]
                continue

            try:
                self._tbldrs[stname] = tab_builder_class(self._lrsts, stats_dir,
                                                         basedir=self._basedir,
                                                         xmetric=self._xmetric)
                _initialized_classes[tab_builder_class] = stname
            except ErrorNotFound as err:
                _LOG.info("Skipping '%s' tab as '%s' statistics not found for all reports.",
                          tab_builder_class.name, tab_builder_class.name)
                _LOG.debug(err)
                continue
            except ErrorBadFormat as err:
                _LOG.warning("Skipping '%s' tab as '%s' statistics has bad format:\n%s",
                             tab_builder_class.name, tab_builder_class.name, err.indent(2))
                continue
