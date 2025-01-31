# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the capability of populating the IPMI statistics tab.
"""

import logging
import pandas
from pepclibs.helperlibs import Trivial
from statscollectlibs.dfbuilders import _IPMIDFBuilder
from statscollectlibs.htmlreport.tabs import _TabBuilderBase, TabConfig

_LOG = logging.getLogger()

class IPMITabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability of populating the IPMI statistics tab."""

    name = "IPMI"
    stnames = ("ipmi-inband", "ipmi-oob",)

    def get_default_tab_cfg(self):
        """
        Generate the default tab configuration as a 'TabConfig.CTabConfig' instance. The default tab
        configuration will specify container tabs for each of the following categories:
          * "Fan Speed"
          * "Temperature"
          * "Power"

        Each of these container tab configurations contain data tab configurations for each IPMI
        metric which is common to all results. For example, the "Fan Speed" container tab might
        contain several data tabs titled "Fan1", "Fan2" etc. if each raw IPMI statistics file
        contains these measurements. If there were no common IPMI metrics between all of the results
        for a given category, the container tab will not be generated.

        See '_TabBuilderBase.TabBuilderBase' for more information on default tab configurations.
        """

        def _build_ctab_cfg(category, metrics):
            """
            Construct an C-tab (container tab) for category 'category' (e.g., "Power") and for every
            metric in 'metrics', add a D-tab to tha C-tab.
            """

            dtabs = []
            for metric in metrics:
                dtab = self._build_def_dtab_cfg(metric, self._time_metric, self._hover_defs,
                                                title=metric)
                dtabs.append(dtab)

            return TabConfig.CTabConfig(category, dtabs=dtabs)

        ctabs = []

        for category, metrics in self._categories.items():
            ctab = _build_ctab_cfg(category, metrics)
            ctabs.append(ctab)

        return TabConfig.CTabConfig(self.name, ctabs=ctabs)

    def _load_dfs(self, rsts):
        """
        Load dataframes from raw IPMI statistics files in 'rsts'. Return the dataframes dictionary.
        """

        dfbldr = _IPMIDFBuilder.IPMIDFBuilder()

        dfs = {}
        found_stnames = set()
        for res in rsts:
            for stname in self.stnames:
                if stname not in res.info["stinfo"]:
                    continue

                dfs[res.reportid] = res.load_stat(stname, dfbldr)

                self._mdd.update(dfbldr.mdo.mdd)

                for category, cat_metrics in dfbldr.mdo.categories.items():
                    if category not in self._categories:
                        self._categories[category] = []
                    self._categories[category] += cat_metrics

                self._hover_defs[res.reportid] = res.get_label_defs(stname)
                found_stnames.add(stname)
                break

        for category in self._categories:
            self._categories[category] = Trivial.list_dedup(self._categories[category])

        return dfs

    def _message_if_mixed(self, rsts):
        """Check if in-band and out-of-band IPMI statistics are mixed."""

        stinfos = {}

        for res in rsts:
            for stname in self.stnames:
                if stname not in res.info["stinfo"]:
                    continue

                if stname not in stinfos:
                    stinfos[stname] = []

                # Save the path to the raw statistics file.
                path = res.stats_path / res.info["stinfo"][stname]["paths"]["stats"]
                stinfos[stname].append(path)

        if len(stinfos) < 2:
            return

        msg = ""
        for stname, paths in stinfos.items():
            msg += f"\n  * {stname}:"
            for path in paths:
                msg += f"\n    * {path}"

        _LOG.notice("a mix of in-band and out-of-band IPMI statistics detected:%s", msg)

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. The arguments are the same as in '_TabBuilderBase.TabBuilderBase()'
        except for the following.
          * rsts - an iterable collection of 'RORawResult' instances for which data should be
                   included in the built tab.
        """

        self._hover_defs = {}
        self._time_metric = "TimeElapsed"

        # Metric definition dictionary for all metrics in all raw results.
        self._mdd = {}
        # Categories dictionary for all metrics in all results. Keys are the category name, values
        # are list of IPMI metrics belonging to the category.
        self._categories = {}

        self._message_if_mixed(rsts)

        dfs = self._load_dfs(rsts)

        # There will be C-tab for each category, except for the time-stamps.
        del self._categories["Timestamp"]

        super().__init__(dfs, self._mdd, outdir, basedir=basedir)

        # Convert the elapsed time metric to the "datetime" format so that diagrams use a
        # human-readable format.
        for df in self._dfs.values():
            df[self._time_metric] = pandas.to_datetime(df[self._time_metric], unit="s")
