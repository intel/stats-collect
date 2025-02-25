# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
API for generating 'stats-collect' statistics tab in HTML report.

Terminology.
  * assets - static files/directories which are included as part of every HTML report (copied to the
             HTML report output directory). Example: javascript libraries, license files.
"""

import dataclasses
import json
from pathlib import Path
import plotly
from packaging import version
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from statscollectlibs.helperlibs import FSHelpers, ProjectFiles
from statscollectlibs.htmlreport.tabs.stats import _StatsTabBuilder
from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoTabBuilder
from statscollecttools import ToolInfo

_LOG = Logging.getLogger(f"stats-collect.{__name__}")

def reportids_dedup(rsts):
    """
    Deduplicate report IDs by appending '-X' to the duplicates, where 'X' is an integer. The
    arguments are as follows.
      * rsts - an iterable collection of test results objects ('RORawResult') to de-duplicate the
               report IDs for.
    """

    reportids = set()
    for res in rsts:
        reportid = res.reportid
        if reportid in reportids:
            # Try to construct a unique report ID.
            for idx in range(1, 20):
                new_reportid = f"{reportid}-{idx:02}"
                if new_reportid not in reportids:
                    _LOG.warning("duplicate reportid '%s', using '%s' instead",
                                 reportid, new_reportid)
                    res.reportid = new_reportid
                    break
            else:
                raise Error(f"too many duplicate report IDs, e.g., '{reportid}' is problematic")

        reportids.add(res.reportid)

def _copy_assets(outdir):
    """Copy assets to 'outdir'."""

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

def _dump_json(obj, path, descr):
    """
    Dump an object to a file in JSON format.
      * obj - Python object to dump to JSON.
      * path - path to create JSON file at.
      * descr - description of the object being dumped.
    """

    try:
        with open(path, "w", encoding="utf-8") as fobj:
            json.dump(obj, fobj, default=str)
    except Exception as err:
        msg = Error(err).indent(2)
        raise Error(f"could not generate report: failed to JSON dump '{descr}' to '{path}':\n"
                    f"{msg}") from None

def validate_outdir(outdir):
    """
    Check that 'outdir' is suitable to be used as the HTML report output directory. The arguments
    are as follows.
      * outdir - the output directory path to check.
    """

    if outdir.exists():
        if not outdir.is_dir():
            raise Error(f"path '{outdir}' already exists and it is not a directory")

        index_path = outdir / "index.html"
        if index_path.exists():
            raise ErrorExists(f"cannot use path '{outdir}' as the output directory, it already "
                              f"contains '{index_path.name}'")

class HTMLReport:
    """
    Provide API for generating 'stats-collect' statistics tab in HTML report.

    The report generated using this class is customizable. The caller is responsible for optionally
    providing an introduction table, extra tabs, and 'RORawResult' instances to create the 'Stats'
    tab.
    """

    def _init_tab_builders(self, rsts):
        """Initialise tab builders for all raw results in 'rsts'."""

        # Only try and generate the statistics tab if statistics were collected.
        collected_stnames = set.union(*[set(res.info["stinfo"]) for res in rsts])

        sysinfo_tbldr = _SysInfoTabBuilder.SysInfoTabBuilder
        if sysinfo_tbldr.stname in collected_stnames:
            self._sysinfo_tbldr = sysinfo_tbldr(self.tabs_dir, basedir=self._outdir)

        collected_stnames -= {sysinfo_tbldr.name}

        if collected_stnames:
            try:
                self._stats_tbldr = _StatsTabBuilder.StatsTabBuilder(rsts, self.tabs_dir,
                                                                     basedir=self._outdir)
            except Error as err:
                _LOG.debug_print_stacktrace()
                _LOG.warning("failed to generate statistics tabs: %s", err)

    def _generate_tabs(self, rsts, tab_cfgs):
        """Generate statistics and sysinfo tabs."""

        tabs = []

        self._init_tab_builders(rsts)
        if self._stats_tbldr:
            tabs.append(self._stats_tbldr.get_tab(tab_cfgs=tab_cfgs))

        if not self._sysinfo_tbldr:
            return tabs

        try:
            sysinfo_tab = self._sysinfo_tbldr.get_tab(rsts)
            tabs.append(sysinfo_tab)
        except Error as err:
            _LOG.debug_print_stacktrace()
            _LOG.warning("failed to generate '%s' tab: %s", self._sysinfo_tbldr.name, err)

        return tabs

    def get_default_tab_cfgs(self, rsts):
        """
        Get the default tab configuration for all statistics collected in results 'rsts'. The
        arguments are as follows.
          * rsts - an iterable collection of test results objects ('RORawResult') to get default tab
                   configuration for.

        Return all default tab configurations as a dictionary in the format of
        '{stname: 'TabConfig.CTabConfig'}' with an entry for each 'stname' (statistics name).
        """

        self._init_tab_builders(rsts)

        if not self._stats_tbldr:
            return {}

        return self._stats_tbldr.get_default_tab_cfgs()

    def generate_report(self, tabs=None, rsts=None, intro_tbl=None, title=None, descr=None,
                        toolname=None, toolver=None, tab_cfgs=None):
        """
        Generate a 'stats-collect' statistics file in the HTML report directory. The arguments are
        as follows.
          * tabs - a list of additional container tabs which should be included in the report. If,
                   omitted, 'rsts' is required to generate statistics tabs.
          * rsts - a list of 'RORawResult' instances for different results with statistics which
                   should be included in the report.
          * intro_tbl - an '_IntroTable.IntroTable' instance which represents the table which will
                        be included in the report. If one is not provided, it will be omitted from
                        the report.
          * title - the title of the report. If one is not provided, omits the title.
          * descr - a description of the report. If one is not provided, omits the description.
          * toolname - override the name of the tool used to generate the report. Defaults to
                       'stats-collect'. Should be used in conjunction with the 'toolver' parameter.
          * toolver - override the version of the tool used to generate the report. Defaults to the
                      current version of 'stats-collect'. Should be used in conjunction with the
                      'toolname' parameter.
          * tab_cfgs - a dictionary in the format '{stname: TabConfig.TabConfig}', where each tab
                       configuration is used to customize the contents of the 'stname' statistics
                       tab. By default, if an 'stname' is not provided in 'tab_cfgs', then a default
                       tab configuration will be used.
        """

        if not tabs and not rsts:
            raise Error("both 'tabs' and 'rsts' can't be 'None'. One of the two parameters should "
                        "be provided.")

        if (toolname and not toolver) or (not toolname and toolver):
            raise Error("one of 'toolname' and 'toolver' was provided. Either both 'toolname' and "
                        "'toolver' should be provided or neither of the options.")

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
            msg = Error(err).indent(2)
            raise Error(f"failed to create directory '{self._data_dir}':\n{msg}") from None

        # 'report_info' stores data used by the Javascript to generate the main report page
        # including the intro table, the file path of the tabs JSON dump plus the report title and
        # description.
        report_info = {"title": title, "descr": descr, "toolname": toolname, "toolver": toolver}

        if self.logpath is not None:
            report_info["logpath"] = self.logpath

        if intro_tbl is not None:
            intro_tbl_path = self._data_dir / "intro_tbl.json"
            intro_tbl.generate(intro_tbl_path)
            report_info["intro_tbl"] = intro_tbl_path.relative_to(self._outdir)

        if rsts:
            reportids_dedup(rsts)
            tabs += self._generate_tabs(rsts, tab_cfgs)

        # Convert Dataclasses to dictionaries so that they are JSON serializable.
        json_tabs = [dataclasses.asdict(tab) for tab in tabs]
        tabs_path = self._data_dir / "tabs.json"
        _dump_json(json_tabs, tabs_path, "tab container")
        report_info["tab_file"] = tabs_path.relative_to(self._outdir)

        rinfo_path = self._data_dir / "report_info.json"
        _dump_json(report_info, rinfo_path, "report information dictionary")

        _copy_assets(self._outdir)

        _LOG.info("Generated report in '%s'.", self._outdir)

    def _check_plotly_ver(self):
        """Warn if plotly version is too old."""

        plotly_ver = plotly.__version__
        preferred_ver = "5.18.0"
        if version.parse(plotly_ver) < version.parse(preferred_ver):
            _LOG.warning("generating a report with 'plotly v%s' can cause time stamps in plots to "
                         "appear as 'undefined', upgrade the 'plotly' package to 'v%s' or higher "
                         "to resolve this issue", plotly_ver, preferred_ver)

    def __init__(self, outdir, logpath=None):
        """
        The class constructor. The arguments are as follows.
          * outdir - the directory which will contain the report.
          * logpath - the path to the report generation log file.
        """

        self._outdir = Path(outdir)
        self._data_dir = self._outdir / "report-data"
        self.tabs_dir = self._data_dir / "tabs"

        self.logpath = logpath

        self._stats_tbldr = None
        self._sysinfo_tbldr = None

        self._check_plotly_ver()
        validate_outdir(outdir)
