# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the "Totals" turbostat level 2 tab.

Please, refer to '_TurbostatL2TabBuilderBase' for more information about level 2 tabs.
"""

from statscollectlibs.dfbuilders import TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs.stats.turbostat import _TurbostatL2TabBuilderBase

class TotalsL2TabBuilder(_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase):
    """This class provides the capability of populating the "Totals" turbostat level 2 tab."""

    name = "Totals"

    def _get_default_tab_cfg(self, metrics, smry_funcs):
        """
        Extends '_get_default_tab_cfg()' from the parent class to add tabs specifically for this
        level 2 turbostat tab as they are not added by 'super()._get_default_tab_cfg()'. Arguments
        are the same as 'super()._get_default_tab_cfg()'.
        """

        cfg = super()._get_default_tab_cfg(metrics, smry_funcs)

        # Add package & module C-states.
        for scope in ("module", "package",):
            hw_pkg_cs = [m for m in self._cstates["hardware"][scope] if m.metric in metrics]
            for csdef in hw_pkg_cs:
                dtab_cfg = self._build_def_dtab_cfg(csdef.metric, self._time_metric, smry_funcs,
                                                    self._hover_defs)
                self._hw_cs_tab.dtabs.append(dtab_cfg)

        return cfg

    def get_tab(self, tab_cfg=None):
        """
        Extends 'super.get_tab()' to populate the descriptions with details on how metrics are
        summarised by turbostat.
        """

        self._defs.mangle_descriptions()
        return super().get_tab(tab_cfg)

    def __init__(self, rsts, outdir, basedir):
        """
        The class constructor. Adding a "totals" turbostat level 2 tab will create a "Totals"
        sub-directory and store data tabs inside it for metrics stored in the raw turbostat
        statistics file.

        Arguments are the same as in '_TabBuilderBase.TabBuilderBase()' except for the following:
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
        """

        dfs = {}
        hover_defs = {}
        for res in rsts:
            if "turbostat" not in res.info["stinfo"]:
                continue

            dfs[res.reportid] = res.load_stat("turbostat", TurbostatDFBuilder.TotalsDFBuilder(),
                                              "turbostat.raw.txt")

            hover_defs[res.reportid] = res.get_label_defs("turbostat")

        super().__init__(dfs, outdir / self.name, basedir, hover_defs)

        # Add non-CPU specific power metrics to the "Temperature/Power" tab.
        self._tp_metrics += ["PkgWatt", "GFXWatt", "RAMWatt", "PkgTmp"]

        # Add uncore frequency tabs to the "Frequency" C-tab. Some versions of 'tubostat' display
        # uncore frequencies in descending order of domain ID, e.g. "UMHz3.0 UMHz2.0 UMHz1.0".
        # So sort them into ascending order so that they are more intuitive.
        self._freq_metrics += sorted(udef.metric for udef in self._uncfreq_defs)
