# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the base class for metrics definitions (AKA 'defs').
"""

from pathlib import Path
from pepclibs.helperlibs import YAML, ProjectFiles

def get_fsname(metric):
    """Given a metric, returns a file-system and URL safe name."""

    # If 'metric' contains "%", we maintain the meaning by replacing with "Percent".
    metric = metric.replace("%", "Percent")

    # Filter out any remaining non-alphanumeric characters.
    metric = ''.join([c for c in metric if c.isalnum()])
    return metric

def is_mdef(dct):
    """Returns 'True' if 'dct' is a metric definition dictionary. Else, returns 'False'."""

    try:
        # Try and access the required fields for a metric definition dictionary.
        _ = dct["name"]
        _ = dct["title"]
        _ = dct["descr"]
        return True
    except TypeError:
        return False
    except KeyError:
        return False

class DefsBase:
    """The base class for metrics definitions (AKA 'defs')."""

    def _mangle_basic(self):
        """Mangle the initially loaded 'self.info' dictionary."""

        for key, val in self.info.items():
            val["name"] = key
            val["fsname"] = get_fsname(key)

    def __init__(self, prjname, toolname, defsdir=None):
        """
        The class constructor. The arguments are as follows.
          * prjname - name of the project the definitions and 'toolname' belong to.
          * toolname - name of the tool to load the definitions for.
          * defsdir - path of directory containing definition files, defaults to "defs".
        """

        self.toolname = toolname

        if defsdir is None:
            defsdir = "defs"

        self._populate_cstate_keys = ["title", "descr", "name", "fsname"]

        self.path = ProjectFiles.find_project_data(prjname, Path(defsdir) / f"{toolname}.yml",
                                                   what=f"{toolname} definitions file")
        self.info = YAML.load(self.path)
        self._mangle_basic()
