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
  * metrics definition dictionary - the 'mdd' attribute of a metrics definition object, has metric
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

    def _handle_pattern(self, metric, mdd):
        """
        Replace patterns in definition dictionary of a metric. The arguments are as follows.
         * metric - name of the metric to substitute the 'mdd' dictionary contents with.
         * mdd - the metric definition dictionary to apply the pattern substitutions to.

        Return the substituted version of the 'mdd' dictionary.
        """

        new_mdd = None

        for pattern in mdd["patterns"]:
            mobj = re.match(pattern, metric)
            if not mobj:
                continue

            new_mdd = mdd.copy()
            del new_mdd["patterns"]

            for idx, grp in enumerate(mobj.groups()):
                for skey in self._mangle_subkeys:
                    text = new_mdd[skey]
                    for grp_patt, grp_repl in (("{GROUPS[%d]}" % idx, grp.upper()),
                                               ("{groups[%d]}" % idx, grp)):
                        text = text.replace(grp_patt, grp_repl)
                    new_mdd[skey] = text
            break

        return new_mdd

    def _handle_patterns(self, metrics):
        """
        Replace patterns in the definitions dictionary. The arguments are as follows.
         * metrics - a collection of metric names to use for substituting the patterns in the
                     definitions dictionary.
        """

        # Parts of the definitions dictionary ('self.mdd') will be replaced with the contents of
        # this dictionary.
        replacements = {}

        for key, val in self.mdd.items():
            if not "patterns" in val:
                # Nothing to mangle.
                continue

            for metric in metrics:
                if metric in self.mdd:
                    # Skip metrics that are explicitly defined.
                    continue

                new_val = self._handle_pattern(metric, val)
                if new_val:
                    if key not in replacements:
                        replacements[key] = {}
                    replacements[key][metric] = new_val

        new_mdd = {}
        for key, val in self.mdd.items():
            if key not in replacements:
                new_mdd[key] = val
                continue
            for new_key, new_val in replacements[key].items():
                new_mdd[new_key] = new_val

        self.mdd = new_mdd

    def _drop_missing_metrics(self, metrics):
        """
        Leave 'metrics' metrics in the MDD (metrics definitions dictionary), and drop any other
        metrics.
        """

        keep_metrics = set(list(metrics))
        for metric in list(self.mdd):
            if metric not in keep_metrics:
                del self.mdd[metric]

    def _add_subkeys(self):
        """Add some more sub-keys to the metrics definition dictionary."""

        for key, val in self.mdd.items():
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
            self._drop_missing_metrics(metrics)

        self._add_subkeys()

    def __init__(self, prjname, toolname, defsdir=None, mdd=None):
        """
        The class constructor. The arguments are as follows.
          * prjname - name of the project the metrics definition YAML file belongs to.
          * toolname - name of the tool or workload the metrics definition YAML file belong to.
          * defsdir - path of directory containing metrics definition YAML files, defaults to
                      "defs".
          * mdd - the metrics definition dictionary to use instead of loading it from the YAML
                  file.
        """

        self.toolname = toolname
        self.path = None

        if mdd:
            self.mdd = mdd
            return

        if defsdir and mdd:
            raise Error("BUG: 'defsdir' and 'mdd' are mutually exclusive")

        if defsdir is None:
            defsdir = "defs"

        self._mangle_subkeys = ["title", "descr"]

        self.path = ProjectFiles.find_project_data(prjname, Path(defsdir) / f"{toolname}.yml",
                                                   what=f"{toolname} definitions file")
        self.mdd = YAML.load(self.path)
