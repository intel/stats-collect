# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide API for populating the "cpufreq" data tab of the "SysInfo" container tab.
"""

from pathlib import Path
from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoDTabBuilderBase

_FILE_PREVIEWS: list[_SysInfoDTabBuilderBase.FilePreviewInfoDict] = [
    {
        "title": "cpufreq",
        "path": Path("sysinfo/sys-cpufreq.after.raw.txt"),
    },
]

class CPUFreqDTabBuilder(_SysInfoDTabBuilderBase.SysInfoDTabBuilderBase):
    """
    Provide API for populating the "cpufreq" data tab of the "SysInfo" container tab.
    """

    def __init__(self, outdir: Path, stats_paths: dict[str, Path], basedir: Path | None = None):
        """
        The class constructor.

        Args:
            outdir: The output directory path (where the D-tab files should be placed).
            stats_paths: A dictionary mapping report IDs to raw statistics directory paths.
            basedir: The report base directory directory path, defaults to 'outdir'.
        """

        super().__init__("cpufreq", outdir, _FILE_PREVIEWS, stats_paths, basedir=basedir)
