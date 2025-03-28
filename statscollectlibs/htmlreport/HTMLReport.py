# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
API for generating 'stats-collect' statistics tab in HTML report.

Terminology.
  * assets - static files/directories which are included as part of every HTML report (copied to the
             HTML report output directory). Example: javascript libraries, license files.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import dataclasses
import json
from pathlib import Path
from typing import Any
import plotly # type: ignore[import-untyped]
from packaging import version
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from statscollectlibs.helperlibs import FSHelpers, ProjectFiles
from statscollectlibs.htmlreport import _IntroTable
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.htmlreport.tabs.stats import _StatsTabBuilder
from statscollectlibs.htmlreport.tabs.TabConfig import CTabConfig
from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoTabBuilder
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollecttools import ToolInfo

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

def _copy_assets(outdir: Path):
    """
    Copy necessary assets to the specified output directory.

    Args:
        outdir: The output directory where the assets will be copied.
    """

    # This list defines the assets which should be copied into the output directory. Items in the
    # list are tuples in the format: (asset_description, path_to_asset, path_of_copied_asset).
    js_assets = [
        ("bundled JavaScript", "js/dist/main.js", outdir / "js/dist/main.js"),
        ("bundled CSS", "js/dist/main.css", outdir / "js/dist/main.css"),
        ("bundled dependency licenses", "js/dist/main.js.LICENSE.txt",
         outdir / "js/dist/main.js.LICENSE.txt"),
    ]

    for asset in js_assets:
        asset_path = ProjectFiles.find_project_web_assets("stats-collect", asset[1], what=asset[0])
        FSHelpers.copy(asset_path, asset[2], exist_ok=True)

    misc_assets = [
        ("root HTML page of the report.", "js/index.html", outdir / "index.html"),
        ("script to serve report directories.", "misc/servedir/serve_directory.py",
         outdir / "serve_directory.py"),
        ("README file for local viewing scripts", "misc/servedir/README.md",
         outdir / "README.md"),
    ]

    for asset in misc_assets:
        asset_path = ProjectFiles.find_project_data("stats-collect", asset[1], what=asset[0])
        FSHelpers.copy(asset_path, asset[2], exist_ok=True)

def _dump_json(obj: Any, path: Path, descr: str):
    """
    Dump a dictionary to a file in JSON format.

    Args:
        obj: An object to dump to JSON.
        path: Path to create JSON file at.
        descr: Description of the object being dumped.
    """

    try:
        with open(path, "w", encoding="utf-8") as fobj:
            json.dump(obj, fobj, default=str)
    except Exception as err:
        errmsg = Error(str(err)).indent(2)
        raise Error(f"Could not generate report: failed to JSON dump '{descr}' to '{path}':\n"
                    f"{errmsg}") from None

def _check_plotly_ver():
    """Warn if plotly version is too old."""

    plotly_ver = plotly.__version__
    preferred_ver = "5.18.0"
    if version.parse(plotly_ver) < version.parse(preferred_ver):
        _LOG.warning("Generating a report with 'plotly v%s' can cause time stamps in plots to "
                     "appear as 'undefined', upgrade the 'plotly' package to 'v%s' or higher "
                     "to resolve this issue", plotly_ver, preferred_ver)

def validate_outdir(outdir: Path):
    """
    Validate that 'outdir' is suitable to be used as the HTML report output directory.

    Args:
        outdir: The output directory path to check.

    Raises:
        ErrorExists: If 'outdir' contains an HTML report.
    """

    if outdir.exists():
        if not outdir.is_dir():
            raise Error(f"Path '{outdir}' already exists and it is not a directory")

        index_path = outdir / "index.html"
        if index_path.exists():
            raise ErrorExists(f"Cannot use path '{outdir}' as the output directory, it already "
                              f"contains '{index_path.name}'")

class HTMLReport:
    """
    Provide API for generating 'stats-collect' statistics tab in HTML report.

    The report generated using this class is customizable. The caller is responsible for optionally
    providing an introduction table, extra tabs, and 'RORawResult' instances to create the 'Stats'
    tab.
    """

    def __init__(self, outdir: Path, logpath: Path | None = None):
        """
        Initialize a class instatnce.

        Args:
            outdir: The directory which will contain the report.
            logpath: The path to the report generation log file.
        """

        self._outdir = Path(outdir)
        self._data_dir = self._outdir / "report-data"
        self.tabs_dir = self._data_dir / "tabs"

        self.logpath = logpath

        self._stats_tbldr: _StatsTabBuilder.StatsTabBuilder | None = None
        self._sysinfo_tbldr: _SysInfoTabBuilder.SysInfoTabBuilder | None = None

        _check_plotly_ver()
        validate_outdir(outdir)

    def _init_tab_builders(self, lrsts: list[LoadedResult]):
        """
        Initialize tab builders for all results in 'lrsts'.

        Args:
            lrsts: List of loaded result objects to initialize the tab builders for.
        """

        # Only try and generate the statistics tab if statistics were collected.
        collected_stnames = set.union(*[set(lres.res.info["stinfo"]) for lres in lrsts])

        sysinfo_tbldr = _SysInfoTabBuilder.SysInfoTabBuilder
        if sysinfo_tbldr.stname in collected_stnames:
            self._sysinfo_tbldr = sysinfo_tbldr(self.tabs_dir, basedir=self._outdir)

        collected_stnames -= {sysinfo_tbldr.name}

        if collected_stnames:
            try:
                self._stats_tbldr = _StatsTabBuilder.StatsTabBuilder(lrsts, self.tabs_dir,
                                                                     basedir=self._outdir)
            except Error as err:
                _LOG.debug_print_stacktrace()
                _LOG.warning("Failed to generate statistics tabs: %s", err)

    def _generate_tabs(self,
                       lrsts: list[LoadedResult],
                       tab_cfgs: dict[str, CTabConfig] | None) -> list[_Tabs.CTabDC]:
        """
        Generate statistics and system information tabs.

        Args:
            rrsts: List of loaded test result objects to generate the tabs for.
            tab_cfgs: A dictionary in the format '{stname: CTabConfig}', where each tab
                      configuration customizes the contents of the 'stname' statistics tab. If an
                      'stname' is not provided in 'tab_cfgs', the default tab configuration will be
                      used.

        Returns:
            list: A list of generated tabs.
        """

        tabs = []

        self._init_tab_builders(lrsts)

        if self._stats_tbldr:
            tabs.append(self._stats_tbldr.get_tab(tab_cfgs=tab_cfgs))

        if not self._sysinfo_tbldr:
            return tabs

        try:
            sysinfo_tab = self._sysinfo_tbldr.get_tab(lrsts)
            tabs.append(sysinfo_tab)
        except Error as err:
            _LOG.debug_print_stacktrace()
            _LOG.warning("Failed to generate '%s' tab: %s", self._sysinfo_tbldr.name, err)

        return tabs

    def get_default_tab_cfgs(self, lrsts: list[LoadedResult]) -> dict[str, CTabConfig]:
        """
        Get the default tab configuration for all statistics in 'lrsts'.

        Args:get_default_tab_cfgs
            lrsts: List of loaded test result objects to get the default tabs configurations for.

        Returns:
            A dictionary containing default tab configurations in the format
            '{stname: CTabConfig}' with an entry for each 'stname' (statistics name).
        """

        self._init_tab_builders(lrsts)

        if not self._stats_tbldr:
            return {}

        return self._stats_tbldr.get_default_tab_cfgs()

    def generate_report(self,
                        tabs: list[_Tabs.CTabDC] | None = None,
                        lrsts: list[LoadedResult] | None = None,
                        intro_tbl: _IntroTable.IntroTable | None = None,
                        title: str | None = None,
                        descr: str | None = None,
                        toolname: str | None = None,
                        toolver: str | None = None,
                        tab_cfgs: dict[str, CTabConfig] | None = None):
        """
        Generate a 'stats-collect' statistics file in the HTML report directory.

        Args:
            tabs: A list of additional container tabs to include in the report.
            lrsts: A list of loaded test result objects to generate the report for.
            intro_tbl: An instance representing the table to include in the report. If not provided,
                       it will be omitted from the report.
            title: The title of the report. If not provided, the title is omitted.
            descr: A description of the report. If not provided, the description is omitted.
            toolname: Override the name of the tool used to generate the report. Defaults to
                     'stats-collect'. Should be used with the 'toolver' parameter.
            toolver: Override the version of the tool used to generate the report. Defaults to the
                     current version of 'stats-collect'.
            tab_cfgs: A dictionary in the format '{stname: CTabConfig}', where each tab
                      configuration customizes the contents of the 'stname' statistics tab.
                      If an 'stname' is not provided in 'tab_cfgs', the default tab configuration
                      will be used.
        """

        if not tabs and not lrsts:
            raise Error("BUG: Both 'tabs' and 'lrsts' can't be 'None'. One of the two parameters "
                        "should be provided.")

        if (toolname and not toolver) or (not toolname and toolver):
            raise Error("BUG: One of 'toolname' and 'toolver' was provided. Either both 'toolname' "
                        "and 'toolver' should be provided or neither of the options.")

        if not toolname:
            toolname = ToolInfo.TOOLNAME

        if not toolver:
            toolver = ToolInfo.VERSION

        if not tabs:
            tabs = []

        # Make sure the output directory exists.
        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to create directory '{self._data_dir}':\n{errmsg}") from None

        # 'report_info' stores data used by the Javascript to generate the main report page
        # including the intro table, the file path of the tabs JSON dump plus the report title and
        # description.
        report_info: dict[str, str | Path | None] = {"title": title,
                                                     "descr": descr,
                                                     "toolname": toolname,
                                                     "toolver": toolver}

        if self.logpath is not None:
            report_info["logpath"] = self.logpath

        if intro_tbl is not None:
            intro_tbl_path = self._data_dir / "intro_tbl.json"
            intro_tbl.generate(intro_tbl_path)
            report_info["intro_tbl"] = intro_tbl_path.relative_to(self._outdir)

        if lrsts:
            tabs += self._generate_tabs(lrsts, tab_cfgs)

        # Convert Dataclasses to dictionaries so that they are JSON serializable.
        json_tabs = [dataclasses.asdict(tab) for tab in tabs]
        tabs_path = self._data_dir / "tabs.json"
        _dump_json(json_tabs, tabs_path, "tab container")
        report_info["tab_file"] = tabs_path.relative_to(self._outdir)

        rinfo_path = self._data_dir / "report_info.json"
        _dump_json(report_info, rinfo_path, "report information dictionary")

        _copy_assets(self._outdir)

        _LOG.info("Generated report in '%s'.", self._outdir)
