# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide API for populating the "pepc info" sub-tab of the "SysInfo" container tab.
"""

from pathlib import Path
from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoTabBuilderBase

_FILES = {
    "pepc cstates info": "sysinfo/pepc_cstates.raw.txt",
    "pepc pstates info": "sysinfo/pepc_pstates.raw.txt",
    "pepc aspm info": "sysinfo/pepc_aspm.raw.txt",
    "pepc topology info": "sysinfo/pepc_topology.raw.txt",
    "pepc power info": "sysinfo/pepc_power.raw.txt"
}

class PepcTabBuilder(_SysInfoTabBuilderBase.SysInfoTabBuilderBase):
    """
    Provide API for populating the "pepc info" sub-tab of the "SysInfo" container tab.
    """

    def __init__(self, outdir: Path, stats_paths: dict[str, Path], basedir: Path | None = None):
        """
        The class constructor.

        Args:
            outdir: The output directory path (where the sub-tab files should be placed).
            stats_paths: A dictionary mapping report IDs to raw statistics directory paths.
            basedir: The report base directory directory path, defaults to 'outdir'.
        """

        super().__init__("pepc", outdir, _FILES, stats_paths, basedir=basedir)
