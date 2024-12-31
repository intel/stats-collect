# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the base class for metrics definition classes.

Terminology.
  * metrics definition class - an 'MDCBase' sub-class.
  * metrics definition object - an object of a 'MDCBase' sub-class.
  * metrics definition dictionary - the 'info' attribute of a metrics definition object, has metric
                                    names as keys and metric information as values. Typically
                                    populated form a metrics definition YAML file.
  * metric definition - a dictionary describing a single metric. The metrics definition dictionary
                        consists of metric definitions.
"""

import re
from pathlib import Path
from pepclibs.helperlibs import YAML, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error

def get_fsname(metric):
    """
    Return a file-system and URL-safe name for a metric. The arguments are as follows.
      * metric - name of the metric to return an FS and URL-safe name for.
    """

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

class MDCBase:
    """Provide the base class for metrics definition classes."""

    def _handle_pattern(self, metric, info):
        """
        Replace patterns in definition dictionary of a metric. The arguments are as follows.
         * metric - name of the metric to substitute the 'info' dictionary contents with.
         * info - the metric definition dictionary to apply the pattern substitutions to.

        Return the substituted version of the 'info' dictionary.
        """

        new_info = None

        for pattern in info["patterns"]:
            mobj = re.match(pattern, metric)
            if not mobj:
                continue

            new_info = info.copy()
            del new_info["patterns"]

            for idx, grp in enumerate(mobj.groups()):
                for skey in self._mangle_subkeys:
                    text = new_info[skey]
                    for grp_patt, grp_repl in (("{GROUPS[%d]}" % idx, grp.upper()),
                                               ("{groups[%d]}" % idx, grp)):
                        text = text.replace(grp_patt, grp_repl)
                    new_info[skey] = text
            break

        return new_info

    def _handle_patterns(self, metrics):
        """
        Replace patterns in the definitions dictionary. The arguments are as follows.
         * metrics - a collection of metric names to use for substituting the patterns in the
                     definitions dictionary.
        """

        # Parts of the definitions dictionary ('self.info') will be replaced with the contents of
        # this dictionary.
        replacements = {}

        for key, val in self.info.items():
            if not "patterns" in val:
                # Nothing to mangle.
                continue

            for metric in metrics:
                if metric in self.info:
                    # Skip metrics that are explicitly defined.
                    continue

                new_val = self._handle_pattern(metric, val)
                if new_val:
                    if key not in replacements:
                        replacements[key] = {}
                    replacements[key][metric] = new_val

        new_info = {}
        for key, val in self.info.items():
            if key not in replacements:
                new_info[key] = val
                continue
            for new_key, new_val in replacements[key].items():
                new_info[new_key] = new_val

        self.info = new_info

    def _add_subkeys(self):
        """Add some more sub-keys to the metrics definition dictionary."""

        for key, val in self.info.items():
            val["name"] = key
            val["fsname"] = get_fsname(key)

    def mangle(self, metrics=None):
        """
        Mangle the metrics definition dictionary and replace the pattern metrics. The arguments are
        as follows.
         * metrics - a collection of metric names to use for substituting the pattern in the
                     metric definition dictionary (e.g., substitute 'CCx' with 'CC1', 'CC1E', etc).
        """

        if metrics:
            self._handle_patterns(metrics)
        self._add_subkeys()

    def __init__(self, prjname, toolname, defsdir=None, info=None):
        """
        The class constructor. The arguments are as follows.
          * prjname - name of the project the metrics definition YAML file belongs to.
          * toolname - name of the tool or workload the metrics definition YAML file belong to.
          * defsdir - path of directory containing metrics definition YAML files, defaults to
                     "defs".
          * info - the metrics definition dictionary to use instead of loading it from the YAML
                   file.
        """

        self.toolname = toolname
        self.path = None

        if info:
            self.info = info
            return

        if defsdir and info:
            raise Error("BUG: 'defsdir' and 'info' are mutually exclusive")

        if defsdir is None:
            defsdir = "defs"

        self._mangle_subkeys = ["title", "descr"]

        self.path = ProjectFiles.find_project_data(prjname, Path(defsdir) / f"{toolname}.yml",
                                                   what=f"{toolname} definitions file")
        self.info = YAML.load(self.path)
