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
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import json
import typing
import dataclasses
from pathlib import Path
from pepclibs.helperlibs import Logging, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from statscollectlibs.helperlibs import FSHelpers
from statscollectlibs.htmlreport import IntroTable
from statscollectlibs.htmlreport.tabs import BuiltTab
from statscollectlibs.htmlreport.tabs.stats._StatsTabBuilder import _StatsTabBuilder
from statscollectlibs.htmlreport.tabs.sysinfo._SysInfoTabBuilder import SysInfoTabBuilder
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollecttools import ToolInfo

if typing.TYPE_CHECKING:
    from typing import TypedDict, Any

    class _JSReportInfo(TypedDict, total=False):
        """
        A dictionary containing information for generating the 'report_info.json' file, which is the
        top level JSON file describing the report as a whole and read by the Javascript code of the
        HTML report.

        Args:
            title: The title of the report.
            descr: A description of the report (no description if not provided).
            toolname: The name of the tool used to generate the report.
            toolver: The version of the tool used to generate the report.
            logpath: The path to the log file from the tool that generated the report (e.g., from
                     'stats-collect report').
            intro_tbl: The path to the introduction table JSON file.
            tab_file: The path to the tabs JSON file (contains information about every tab).
        """

        title: str
        descr: str | None
        toolname: str
        toolver: str
        logpath: Path | None
        intro_tbl: Path | None
        tab_file: Path

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.{ToolInfo.TOOLNAME}.{__name__}")

def get_project_web_assets_envar(prjname):
    """
    Return the name of the environment variable that points to the web assets location of project
    'prjname'.
    """

    name = prjname.replace("-", "_").upper()
    return f"{name}_WEB_ASSETS_PATH"

def find_project_web_assets(prjname, datadir, pman=None, what=None):
    """
    Search for project 'prjname' web assets. The arguments are as follows:
      * prjname - name of the project the web-asset belongs to.
      * datadir - the sub-path of the web-asset in the web-asset project installation base
                  directory.
      * datadir - name of the sub-directory containing the web asset. This method basically
                  searches for 'datadir' in a set of pre-defined paths (see below).
      * pman - the process manager object for the host to find the web-asset on (local host by
               default).
      * what - human-readable description of 'subpath' (or what is searched for), which will be used
               in the error message if an error occurs.

    The web-assets are searched for in the 'datadir' directory (or sub-path) of the following
    directories (and in the following order).
      * in the directory the of the running program.
      * in the directory specified by the '<prjname>_WEB_ASSETS_PATH' environment variable.
      * in '$HOME/.local/share/javascript/<prjname>/', if it exists.
      * in '$HOME/share/javascript/<prjname>/', if it exists.
      * in '$VIRTUAL_ENV/share/javascript/<prjname>/', if the variable is defined and the directory
            it exists.
      * in '/usr/local/share/javascript/<prjname>/', if it exists.
      * in '/usr/share/javascript/<prjname>/', if it exists.
    """

    return next(ProjectFiles.search_project_data("statscollectdata", datadir, pman=pman, what=what,
                                    envars=(get_project_web_assets_envar(prjname),)))
def _copy_assets(outdir: Path):
    """
    Copy necessary web assets to the specified output directory.

    Args:
        outdir: The output directory where the assets will be copied.
    """

    js_assets = [("bundled JavaScript", "main.js"),
                 ("bundled CSS", "main.css"),
                 ("bundled dependency licenses", "main.js.LICENSE.txt")]

    for name, fname in js_assets:
        subpath = f"js/dist/{fname}"
        src_path = ProjectFiles.find_project_data(ToolInfo.TOOLNAME, subpath, what=name)
        dst_path = outdir / "js/dist" / fname
        FSHelpers.copy(src_path, dst_path, exist_ok=True)

    misc_assets = [
        ("root HTML page of the report", "js/index.html",
         outdir / "index.html"),
        ("script to serve report directories", "servedir/serve_directory.py",
         outdir / "serve_directory.py"),
        ("README file for local viewing scripts", "servedir/README.md",
         outdir / "README.md"),
    ]

    for name, src, dst in misc_assets:
        src_path = ProjectFiles.find_project_data(ToolInfo.TOOLNAME, src, what=name)
        FSHelpers.copy(src_path, dst, exist_ok=True)

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

    def __init__(self,
                 lrsts: list[LoadedResult],
                 title: str,
                 outdir: Path,
                 logpath: Path | None = None,
                 descr: str | None = None,
                 toolname: str | None = None,
                 toolver: str | None = None,
                 xmetric: str | None = None):
        """
        Initialize a class instatnce.

        Args:
            lrsts: A list of loaded test result objects to generate the report for.
            outdir: The directory which will contain the report.
            logpath: The path to the log file from the tool that generated the report (e.g., from
                    'stats-collect report').
            title: The title of the report. If not provided, the title is omitted.
            descr: A description of the report. If not provided, the description is omitted.
            toolname: Override the name of the tool used to generate the report. Defaults to
                     'stats-collect'. Should be used with the 'toolver' parameter.
            toolver: Override the version of the tool used to generate the report. Defaults to the
                     current version of 'stats-collect'.
            xmetric: Name of the metric to use for the X-axis of the plots. If not provided, the
                     X-axis will use the time elapsed since the beginning of the measurements.
        """

        if (toolname and not toolver) or (not toolname and toolver):
            raise Error("BUG: One of 'toolname' and 'toolver' was provided. Either both 'toolname' "
                        "and 'toolver' should be provided or neither of the options.")
        if not toolname:
            toolname = ToolInfo.TOOLNAME
        if not toolver:
            toolver = ToolInfo.VERSION

        self._lrsts = lrsts
        self._title = title
        self._outdir = outdir
        self.logpath = logpath
        self._descr = descr
        self._toolname = toolname
        self._toolver = toolver
        self._xmetric = xmetric

        self._data_dir = self._outdir / "report-data"
        self.tabs_dir = self._data_dir / "tabs"

        self._stats_tbldr: _StatsTabBuilder | None = None
        self._sysinfo_tbldr: SysInfoTabBuilder | None = None

        validate_outdir(outdir)

    def _init_tab_builders(self):
        """Initialize tab builders for all test results."""

        collected_stnames = set.union(*[set(lres.res.info["stinfo"]) for lres in self._lrsts])

        sysinfo_tbldr = SysInfoTabBuilder
        for stname in sysinfo_tbldr.stnames:
            if stname in collected_stnames:
                self._sysinfo_tbldr = sysinfo_tbldr(self._lrsts, self.tabs_dir,
                                                    basedir=self._outdir)
                break

        collected_stnames -= {sysinfo_tbldr.name}

        if collected_stnames:
            try:
                self._stats_tbldr = _StatsTabBuilder(self._lrsts, self.tabs_dir,
                                                     basedir=self._outdir, xmetric=self._xmetric)
            except Error as err:
                _LOG.debug_print_stacktrace()
                _LOG.warning("Failed to generate statistics tabs: %s", err)

    def _build_tabs(self) -> list[BuiltTab.BuiltCTab]:
        """
        Build all tabs and return a list of build container tabs (C-tabs). This includes parsing all
        the raw statistic files, generating all the plots, etc.

        At this point the list includes only 2 built C-tabs:
          * The top level "Stats" C-tab, that includes all the statistics.
          * The "Sysinfo" C-tab, that includes the overall system information.

        Returns:
            A list of built C-tabs.
        """

        tabs = []

        self._init_tab_builders()

        if self._stats_tbldr:
            tabs.append(self._stats_tbldr.build_tab())

        if not self._sysinfo_tbldr:
            return tabs

        try:
            sysinfo_tab = self._sysinfo_tbldr.build_tab()
            tabs.append(sysinfo_tab)
        except Error as err:
            _LOG.debug_print_stacktrace()
            _LOG.warning("Failed to build  the'%s' tab: %s", self._sysinfo_tbldr.name, err)

        return tabs

    def generate_report(self,
                        tabs: list[BuiltTab.BuiltCTab] | None = None,
                        intro_tbl: IntroTable.IntroTable | None = None):
        """
        Generate a 'stats-collect' statistics file in the HTML report directory.

        Args:
            tabs: A list of additional container tabs to include in the report.
            intro_tbl: An 'IntroTable' object that will be used for generating the intro table of
                       the report. If not provided, the intro table will be omitted.
        """

        if not tabs:
            tabs = []

        # Make sure the output directory exists.
        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to create directory '{self._data_dir}':\n{errmsg}") from None

        report_info: _JSReportInfo = {"title": self._title, "descr": self._descr,
                                      "toolname": self._toolname, "toolver": self._toolver}

        if self.logpath is not None:
            report_info["logpath"] = self.logpath

        if intro_tbl is not None:
            path = self._data_dir / "intro_tbl.json"
            intro_tbl.generate(path)
            report_info["intro_tbl"] = path.relative_to(self._outdir)

        if self._lrsts:
            tabs += self._build_tabs()

        # Convert Dataclasses to dictionaries so that they are JSON serializable.
        json_tabs = [dataclasses.asdict(tab) for tab in tabs]
        tabs_path = self._data_dir / "tabs.json"
        _dump_json(json_tabs, tabs_path, "tab container")
        report_info["tab_file"] = tabs_path.relative_to(self._outdir)

        rinfo_path = self._data_dir / "report_info.json"
        _dump_json(report_info, rinfo_path, "report information dictionary")

        _copy_assets(self._outdir)

        _LOG.info("Generated report in '%s'.", self._outdir)
