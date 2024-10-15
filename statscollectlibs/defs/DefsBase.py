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

import re
from pathlib import Path
from pepclibs.helperlibs import YAML, ProjectFiles

def get_fsname(metric):
    """Given a metric, returns a file-system and URL safe name."""

    # If 'metric' contains "%", we maintain the meaning by replacing with "Percent".
    metric = metric.replace("%", "Percent")

    # Filter out any remaining non-alphanumeric characters.
    metric = "".join([c for c in metric if c.isalnum()])
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

    def _expand_metric_patterns(self, metrics):
        """
        Replace the pattern in metrics definitions. The arguments are as follows.
         * metrics - a collection of metric names to use for substituting the patterns in the
                     definitions dictionary.
        """

        replacements = {}

        # pylint: disable=too-many-nested-blocks
        for key, val in self.info.items():
            if not "patterns" in val:
                # Nothing to mangle.
                continue

            replacement = {}
            for metric in metrics:
                if metric in self.info:
                    # Skip metrics that are explicitly defined.
                    continue

                for pattern in val["patterns"]:
                    mobj = re.match(pattern, metric)
                    if not mobj:
                        continue

                    replacement[metric] = self.info[key].copy()
                    del replacement[metric]["patterns"]

                    for idx, grp in enumerate(mobj.groups()):
                        for skey in self._mangle_subkeys:
                            text = replacement[metric][skey]
                            for grp_patt, grp_repl in (("{GROUPS[%d]}" % idx, grp.upper()),
                                                       ("{groups[%d]}" % idx, grp)):
                                text = text.replace(grp_patt, grp_repl)
                            replacement[metric][skey] = text
                    break

                if replacement:
                    replacements[key] = replacement

        new_info = {}
        for key, val in self.info.items():
            if key not in replacements:
                new_info[key] = val
                continue
            for new_key, new_val in replacements[key].items():
                new_info[new_key] = new_val

        self.info = new_info

        # Remove unnecessary metric definitions.
        metrics_set = set(metrics)
        for key in list(self.info):
            if key in metrics_set:
                continue

            # Some metrics were renamed. For example turbostat column "Time_Of_Day_Seconds" is named
            # "Time" in the metrics definition dictionary.
            original_name = self.info[key].get("original_name")
            if original_name in metrics_set:
                continue

            del self.info[key]

    def _add_subkeys(self):
        """Add some more sub-keys to the metrics definition dictionary."""

        for key, val in self.info.items():
            val["name"] = key
            val["fsname"] = get_fsname(key)

    def mangle(self, metrics=None):
        """
        Mangle the definitions dictionary and replace the pattern metrics. The arguments are as
        follows.
         * metrics - a collection of metric names to use for substituting the pattern in the
                     definitions (e.g., substitute 'CCx' with 'CC1', 'CC1E', etc).
        """

        if metrics:
            self._expand_metric_patterns(metrics)
        self._add_subkeys()

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

        self._mangle_subkeys = ["title", "descr"]

        self.path = ProjectFiles.find_project_data(prjname, Path(defsdir) / f"{toolname}.yml",
                                                   what=f"{toolname} definitions file")
        self.info = YAML.load(self.path)
