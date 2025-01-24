# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the base class for metrics definition classes.

Terminology:
    Metrics definition class: A subclass of 'MDCBase'.
    Metrics definition object: An instance of a 'MDCBase' subclass.
    Metrics definition dictionary: the 'mdd' attribute of a metrics definition object, containing
                                   metric names as keys and metric information as values. Typically
                                   populated from a metrics definition YAML file.
    Metric definition: A dictionary describing a single metric. The metrics definition dictionary
                       consists of multiple metric definitions.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import re
from pathlib import Path
from typing import TypedDict, Literal, Sequence
from pepclibs.helperlibs import YAML, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error

class MDTypedDict(TypedDict, total=False):
    """
    The metric definition dictionary, describing a single metric.

    Attributes:
        name: Metric name.
        title: Capitalized metric title, short and human-readable.
        descr: A longer metric description.
        unit: The unit of the metric (full name, singular, like "second"). This key is optional.
        short_unit: A short form of the unit of measurement (e.g., "s" instead of "second"). This
                   key is optional.
        scope: The scope of the metric (e.g., "package"). This key is optional.
        categories: A list of categories that the metric belongs to. This key is optional.
    """

    name: str
    title: str
    descr: str
    unit: str
    short_unit: str
    scope: str
    categories: list[str]

class MDCBase:
    """Provide the base class for metrics definition classes."""

    def __init__(self, prjname: str, yaml_path: Path, mdd: dict[str, MDTypedDict] | None = None):
        """
        The class constructor.

        Args:
            prjname: Name of the project the metrics definition YAML file belongs to.
            yaml_path: Path of metrics definition YAML files relative to the project directory.
            mdd: The metrics definition dictionary to use instead of loading it from the YAML file.
        """

        self.path = None
        self.mdd: dict[str, MDTypedDict] = {}

        if mdd:
            self.mdd = mdd
            return

        if yaml_path and mdd:
            raise Error("BUG: 'yaml_path' and 'mdd' are mutually exclusive")

        # TODO: a hack to silence mypy "literal-required" warnings. It might have been fixed in
        # newer mypy versions so that the 'tuple' type is fine to use. Refer to
        # https://github.com/python/mypy/issues/7178
        self._mangle_subkeys: Sequence[Literal["title", "descr"]] = ("title", "descr")

        what = f"the '{yaml_path}' metrics definition file"
        self.path = ProjectFiles.find_project_data(prjname, yaml_path, what=what)
        self.mdd = YAML.load(self.path)

        # The YAML files may not have the "name" key, add it.
        for key, md in self.mdd.items():
            md["name"] = key

    def _handle_pattern(self, metric: str, md: MDTypedDict) -> MDTypedDict:
        """
        Replace patterns in the metric definition of 'metric'.

        Args:
            metric: Name of the metric to substitute the 'mdd' dictionary contents with.
            md: The metric definition to apply the pattern substitutions to.

        Returns:
            The substituted version of the 'md' dictionary.
        """

        new_md: MDTypedDict = {}

        for pattern in md["patterns"]: # type: ignore[typeddict-item]
            mobj = re.match(pattern, metric)
            if not mobj:
                continue

            new_md = md.copy()
            del new_md["patterns"] # type: ignore[typeddict-item]

            for idx, grp in enumerate(mobj.groups()):
                for skey in self._mangle_subkeys:
                    text = new_md[skey]
                    for grp_patt, grp_repl in (("{GROUPS[%d]}" % idx, grp.upper()),
                                               ("{groups[%d]}" % idx, grp)):
                        text = text.replace(grp_patt, grp_repl)
                    new_md[skey] = text
            break

        return new_md

    def _handle_patterns(self, metrics: list[str]):
        """
        Replace patterns in the MDD ('self.mdd') with actual metric names from 'metrics'.

        Args:
            metrics: A list of metric names to use for substituting the patterns in the definitions
                     dictionary.
        """

        # Current MDD has "pattern" metric keys, such as "Cx", instead of "C1". And these "pattern"
        # metrics definition dictionary includes the "patterns" key, which is a list of regular
        # expressions that can be used to substitute the "pattern" metric key with the actual
        # metric.
        #
        # The 'replacements' dictionary will store the actual metric definitions (already
        # substituted).
        replacements: dict[str, dict[str, MDTypedDict]] = {}

        # Build the list of actual metrics that will be used for pattern substitutions, skipping the
        # metrics that are already defined in the MDD.
        actual_metrics: list[str] = []
        for actual_metric in metrics:
            if actual_metric in self.mdd:
                continue
            actual_metrics.append(actual_metric)

        for orig_metric, orig_md in self.mdd.items():
            if "patterns" not in orig_md:
                # Nothing to mangle for this metric.
                continue

            for new_metric in actual_metrics:
                new_md = self._handle_pattern(new_metric, orig_md)
                if not new_md:
                    continue

                if orig_metric not in replacements:
                    replacements[orig_metric] = {}

                new_md["name"] = new_metric
                replacements[orig_metric][new_metric] = new_md

        new_mdd = {}
        for orig_metric, orig_md in self.mdd.items():
            if orig_metric not in replacements:
                new_mdd[orig_metric] = orig_md
                continue
            for new_metric, new_md in replacements[orig_metric].items():
                new_mdd[new_metric] = new_md

        self.mdd = new_mdd

    def _drop_missing_metrics(self, metrics: list[str]):
        """
        Ensure the MDD includes only metrics from 'metrics'. Drop any metric that is not in
        'metrics' from the MDD.

        Args:
            metrics: List of metric names to keep in the MDD.
        """

        keep_metrics = set(metrics)
        for metric in list(self.mdd):
            if metric not in keep_metrics:
                del self.mdd[metric]

    def mangle(self, metrics: list[str], drop_missing: bool = True):
        """
        Mangle the metrics definition dictionary. The mangling is related to the "patterns" key in
        the metrics definition YAML files. The idea is that one YAML file metric may correspond to
        multiple "versions" of the metric. For example, there may be the "Cx" metric in the YAML
        file, and it corresponds to "C1", "C2", and "C3" actual metrics. The "patterns" mechanism is
        about turning "Cx" into "C1", "C2" and "C3" in the metrics definitions dictionary. Note, the
        actual metrics list is platform-specific. For example, one platform may have only "C1", and
        another platform may have "C1", "C2", and "C3".

        Args:
            metrics: List of metric names to use for substituting the pattern in the metric
                     definition dictionary.
            drop_missing: If 'True', keep only metrics in 'metrics' in the MDD, and drop all other
                          metrics from the MDD. If 'False', keep all metrics.
        """

        self._handle_patterns(metrics)
        if drop_missing:
            self._drop_missing_metrics(metrics)
