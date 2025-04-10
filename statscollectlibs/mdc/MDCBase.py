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
from typing import TypedDict, Literal, Sequence, NoReturn, Any
from pepclibs.helperlibs import YAML, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat

# The maximum MDD keys lenght.
MAX_KEY_LEN = 64
# The maximum string MDD values length.
MAX_VAL_LEN = 2048

class MDTypedDict(TypedDict, total=False):
    """
    The metric definition, describing a single metric.

    Attributes:
        name: Metric name.
        title: Capitalized metric title, short and human-readable.
        descr: A longer metric description.
        type: the type of the key (e.g., "int", "float").
        unit: The unit of the metric (full name, singular, like "second"). This key is optional.
        short_unit: A short form of the unit of measurement (e.g., "s" instead of "second"). This
                    key is optional.
        scope: The scope of the metric (e.g., "package"). This key is optional.
        categories: A list of categories that the metric belongs to. This key is optional.
    """

    name: str
    title: str
    descr: str
    type: str
    unit: str
    short_unit: str
    scope: str
    categories: list[str]

def validate_mdd(mdd: dict[str, MDTypedDict], mdd_src: str | None = None):
    """
        Validate a Metric Definition Dictionary (MDD).

        Args:
            mdd: The Metric Definition Dictionary to validate.
            mdd_src: A string identifying the source of the MDD, used only in exception messages in
                     case of an error.

        Raises:
            ErrorBadFOrmat: If MDD has bad format.
    """

    def _raise(msg: str) -> NoReturn:
        """
        Raise an exception with a formatted message.

        Args:
            msg: The error message to be included in the exception.

        Raises:
            ErrorBadFormat: Always.
        """

        errmsg = f"Invalid MDD: {msg}"
        if mdd_src:
            errmsg += f"\nMDD source is: {mdd_src}"
        raise ErrorBadFormat(errmsg)

    def _check_key_len(key: str, metric: str, what: str | None = None):
        """
        Check if the length of the key exceeds the maximum allowed length.

        Args:
            key: The key to be checked.
            metric: The metric associated with the key.
            what: The name of the key to be used in the error message. If 'None', the default name
                  is "key".

        Raises:
            ErrorBadFormat: If the length of the key exceeds the maximum allowed length.
        """

        if not what:
            what = "Key"
        else:
            what = what.capitalize()

        if len(key) > MAX_KEY_LEN:
            _raise(f"{what} '{key}' in '{metric}' is too long ({len(key)}, while max. is "
                   f"{MAX_KEY_LEN} characters)")

    def _check_val_len(key: str, val: str, metric: str):
        """TODO"""

        if len(val) > MAX_VAL_LEN:
            _raise(f"Value of key '{key}' in '{metric}' is too long ({len(val)}, while max. is "
                   f"{MAX_VAL_LEN} characters)")

    list_keys = ("categories",)
    for metric, md in mdd.items():
        allowed_keys = MDTypedDict.__annotations__
        for key, val in md.items():
            if key not in allowed_keys:
                _raise(f"Unknown key '{key}' for metric '{metric}'")

            if key not in list_keys:
                if not isinstance(val, str):
                    _raise(f"Key '{key}' in '{metric}' is not a string")
                _check_key_len(key, metric)
                _check_val_len(key, val, metric)
                continue

            # The value is a list of strings.
            if not isinstance(val, list):
                _raise(f"Key '{key}' in '{metric}' is not a list")
            for elt in val:
                if not isinstance(elt, str):
                    _raise(f"{key.capitalize()} '{elt}' in '{metric}' is not a string")
                _check_key_len(elt, metric, what=key)
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

        # Metric names may be arranged by the category.
        self.categories: dict[str, Any] = {}

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
            if "name" not in md:
                md["name"] = key

    def _handle_pattern(self, metric: str, md: MDTypedDict) -> MDTypedDict:
        """
        Replace patterns in the metric definition of 'metric'.

        Args:
            metric: Name of the metric to substitute the 'mdd' dictionary contents with.
            md: The metric definition to apply the pattern substitutions to.

        Returns:
            The substituted version of the 'md' metric definition.
        """

        new_md: MDTypedDict = {}

        for pattern in md["patterns"]: # type: ignore[typeddict-item]
            mobj = re.fullmatch(pattern, metric)
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
                # Skip MDs that have patterns but nothing to replace them with, to avoid pattern
                # metrics in the final MDD, because they are presumably useless.
                if "patterns" not in orig_md:
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

        validate_mdd(self.mdd, mdd_src=f"YAML file at '{self.path}'")
