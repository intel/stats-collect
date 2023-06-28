#!/usr/bin/python3
#
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""The standard python packaging script."""

import re
import os
from pathlib import Path
from setuptools import setup, find_packages

_TOOLNAMES = ["stats-collect"]

def get_version(filename):
    """Fetch the project version number."""

    with open(filename, "r", encoding="utf-8") as fobj:
        for line in fobj:
            matchobj = re.match(r'^VERSION = "(\d+.\d+.\d+)"$', line)
            if matchobj:
                return matchobj.group(1)
    return None

def get_data_files(installdir, subdir, exclude=None):
    """
    When the task is to include all files in the 'subdir' directory to the package and install them
    under the 'installdir' directory, this function can be used to generate the list of files
    suitable for the 'data_files' setup parameter.
    """

    files_dict = {}
    for root, _, files in os.walk(subdir):
        for fname in files:
            fname = Path(f"{root}/{fname}")

            if exclude and str(fname) in exclude:
                continue

            key = str(Path(installdir) / fname.relative_to(subdir).parent)
            if key not in files_dict:
                files_dict[key] = []
            files_dict[key].append(str(fname))

    return list(files_dict.items())

# Python helpers get installed as scripts. We exclude these scripts from being installed as data.
_PYTHON_HELPERS = ["helpers/stc-agent/stc-agent", "helpers/stc-agent/ipmi-helper"]

setup(
    name="stats-collect",
    description="Statistics Collection Tool",
    author="Artem Bityutskiy",
    author_email="artem.bityutskiy@linux.intel.com",
    python_requires=">=3.7",
    version=get_version("statscollecttools/ToolInfo.py"),
    data_files=get_data_files("share/man/man1", "docs/man1") + \
               get_data_files("share/stats-collect/helpers/stc-agent", "helpers/stc-agent",
                              exclude=_PYTHON_HELPERS) + \
               get_data_files("share/stats-collect/defs/statscollect", "defs/statscollect") + \
               get_data_files("share/javascript/stats-collect/js/dist", "js/dist") + \
               get_data_files("share/stats-collect/misc/servedir", "misc/servedir") + \
               [("share/stats-collect/js", ["js/index.html"])],
    scripts=_TOOLNAMES + _PYTHON_HELPERS,
    packages=find_packages(),
    install_requires=["pepc>=1.4.25", "plotly>=4", "numpy", "pandas", "pyyaml", "colorama"],
    long_description="""This package provides stats-collect - a Linux command-line tool which
                        collects and visualizes system statistics and telemetry.""",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research"
        "Topic :: System :: Hardware",
        "Topic :: System :: Operating System Kernels :: Linux",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 4 - Beta",
    ],
)
