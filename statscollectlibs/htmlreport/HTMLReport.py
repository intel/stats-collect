# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the API for generating HTML reports."""

import contextlib
import dataclasses
import logging
import json
from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorExists
from pepclibs.helperlibs import LocalProcessManager
from statscollectlibs.helperlibs import FSHelpers, ProjectFiles
from statscollectlibs.htmlreport.tabs.stats import _StatsTabBuilder
from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoTabBuilder
from statscollecttools import ToolInfo

_LOG = logging.getLogger()

def reportids_dedup(rsts):
    """
    Deduplicate report IDs for 'rsts' by appending '-X' to the duplicate report IDs where 'X' is an
    integer which increments for each duplicate result ID. Modifies the result objects in-place.
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

def copy_dir(srcdir, dstpath):
    """
    Helper function for '_copy_raw_data()'. Copy the 'srcdir' to 'dstpath' and set permissions
    accordingly.
    """

    try:
        FSHelpers.copy_dir(srcdir, dstpath, exist_ok=True, ignore=["html-report"])
        FSHelpers.set_default_perm(dstpath)

        # This block of code helps on SELinux-enabled systems when the output directory
        # ('self.outdir') is exposed via HTTP. In this case, the output directory should
        # have the right SELinux attributes (e.g., 'httpd_user_content_t' in Fedora 35).
        # The raw wult data that we just copied does not have the SELinux attribute, and
        # won't be accessible via HTTPs. Run 'restorecon' tool to fix up the SELinux
        # attributes.
        with LocalProcessManager.LocalProcessManager() as lpman:
            with contextlib.suppress(ErrorNotFound):
                lpman.run_verify(f"restorecon -R {dstpath}")
    except Error as err:
        msg = Error(err).indent(2)
        raise Error(f"failed to copy raw data to report directory:\n{msg}") from None

def _copy_assets(outdir):
    """
    This is a helper function for 'generate_report()' which copies assets to 'outdir'.

    "Assets" refers to all of the static files which are included as part of every report.
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
        FSHelpers.move_copy_link(asset_path, asset[2], "copy", exist_ok=True)

    misc_assets = [
        ("root HTML page of the report.", "js/index.html", outdir / "index.html"),
        ("script to serve report directories.", "misc/servedir/serve_directory.py",
            outdir / "serve_directory.py"),
        ("README file for local viewing scripts", "misc/servedir/README.md",
            outdir / "README.md"),
    ]

    for asset in misc_assets:
        asset_path = ProjectFiles.find_project_data("stats-collect", asset[1], what=asset[0])
        FSHelpers.move_copy_link(asset_path, asset[2], "copy", exist_ok=True)

def _dump_json(obj, path, descr):
    """
    Helper function wrapping 'json.dump' operation with a standardised error message so that the
    error messages are consistent. Arguments are as follows:
        * obj - Python object to dump to JSON.
        * path - path to create JSON file at.
        * descr - description of object being dumped.
    """

    try:
        with open(path, "w", encoding="utf-8") as fobj:
            json.dump(obj, fobj, default=str)
    except Exception as err:
        msg = Error(err).indent(2)
        raise Error(f"could not generate report: failed to JSON dump '{descr}' to '{path}':\n"
                    f"{msg}") from None

def validate_outdir(outdir):
    """If directory 'outdir' exists and it already has valid data, raise an ErrorExists."""

    if outdir.exists():
        if not outdir.is_dir():
            raise Error(f"path '{outdir}' already exists and it is not a directory")

        index_path = outdir / "index.html"
        if index_path.exists():
            raise ErrorExists(f"cannot use path '{outdir}' as the output directory, it already "
                              f"contains '{index_path.name}'")

class HTMLReport:
    """
    This class provides the API for generating HTML reports.

    The reports generated using this class are highly customisable. The caller
    is responsible for optionally providing an introduction table, extra tabs,
    and 'RORawResult' instances to create the 'Stats' tab.

    The class has only one public method which is used to generate the HTML
    report in the 'outdir' provided to the class constructor. The arguments
    provided to the method determine the contents of the generated report.
       * 'generate_report()'
    """

    @property
    def tabs_dir(self):
        """
        The 'tabs' report directory. Can be used to place tab data inside the relevant directory.
        """
        return self._tabs_dir

    def _generate_tabs(self, rsts):
        """Helper function for 'generate_report()'. Generates statistics and sysinfo tabs."""

        tabs = []
        sysinfo_tab_bldr = _SysInfoTabBuilder.SysInfoTabBuilder

        # Only try and generate the statistics tab if statistics were collected.
        collected_stnames = set.union(*[set(res.info["stinfo"]) for res in rsts])
        collected_stnames -= {sysinfo_tab_bldr.stname}
        if collected_stnames:
            try:
                stats_tab_bldr = _StatsTabBuilder.StatsTabBuilder(self._tabs_dir,
                                                                  basedir=self._outdir)
                tabs.append(stats_tab_bldr.get_tab(rsts))
            except Error as err:
                _LOG.warning("Failed to generate statistics tabs: %s", err)

        if not any(sysinfo_tab_bldr.stname in res.info["stinfo"] for res in rsts):
            return tabs

        try:
            tab_bldr = sysinfo_tab_bldr(self._tabs_dir, basedir=self._outdir)
            sysinfo_tab = tab_bldr.get_tab(rsts)
            tabs.append(sysinfo_tab)
        except Error as err:
            _LOG.warning("Failed to generate '%s' tab: %s", sysinfo_tab_bldr.name, err)

        return tabs

    def generate_report(self, tabs=None, rsts=None, intro_tbl=None, title=None, descr=None,
                        toolname=None, toolver=None):
        """
        Generate an HTML report in 'outdir' (provided to the class constructor). Customise the
        contents of the report using the function parameters. Arguments are as follows:
         * tabs - a list of additional container tabs which should be included in the report. If,
                  omitted, 'stats_paths' is required to generate statistics tabs.
         * rsts - a list of 'RORawResult' instances for different results with statistics which
                  should be included in the report.
         * intro_tbl - an '_IntroTable.IntroTable' instance which represents the table which will be
                       included in the report. If one is not provided, it will be omitted from the
                       report.
         * title - the title of the report. If one is not provided, omits the title.
         * descr - a description of the report. If one is not provided, omits the description.
         * toolname - override the name of the tool used to generate the report. Defaults to
                      'stats-collect'. Should be used in conjunction with the 'toolver' parameter.
         * toolver - override the version of the tool used to generate the report. Defaults to the
                     current version of 'stats-collect'. Should be used in conjunction with the
                     'toolname' parameter.
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
        report_info = {"title": title, "descr": descr,
                       "toolname": toolname, "toolver": toolver}

        if intro_tbl is not None:
            intro_tbl_path = self._data_dir / "intro_tbl.json"
            intro_tbl.generate(intro_tbl_path)
            report_info["intro_tbl"] = intro_tbl_path.relative_to(self._outdir)

        if rsts:
            reportids_dedup(rsts)
            tabs += self._generate_tabs(rsts)

        # Convert Dataclasses to dictionaries so that they are JSON serialisable.
        json_tabs = [dataclasses.asdict(tab) for tab in tabs]
        tabs_path = self._data_dir / "tabs.json"
        _dump_json(json_tabs, tabs_path, "tab container")
        report_info["tab_file"] = tabs_path.relative_to(self._outdir)

        rinfo_path = self._data_dir / "report_info.json"
        _dump_json(report_info, rinfo_path, "report information dictionary")

        _copy_assets(self._outdir)

        FSHelpers.set_default_perm(self._outdir)

        _LOG.info("Generated report in '%s'.", self._outdir)

    def __init__(self, outdir):
        """
        The class constructor. The arguments are as follows:
         * outdir - the directory which will contain the report.
        """

        self._outdir = Path(outdir)
        self._data_dir = self._outdir / "report-data"
        self._tabs_dir = self._data_dir / "tabs"
        validate_outdir(outdir)
