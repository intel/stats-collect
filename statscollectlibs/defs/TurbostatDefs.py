# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API to turbostat metrics definitions (AKA 'defs')."""

import re
from statscollectlibs.defs import _STCDefsBase
from statscollectlibs.parsers import TurbostatParser

class _CSTypeBase:
    """
    Turbostat collects information about various types of C-state including, but not limited to,
    requestable, package, and module C-states. This base class provides a common interface for all
    of the C-state type classes.
    """

    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' is an instance of this type of C-state."""
        raise NotImplementedError()

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        raise NotImplementedError()

    def __init__(self, metric):
        """The class constructor. """
        self.metric = metric
        self.cstate = self._get_cs_from_metric(metric)

class ReqCSDefCount(_CSTypeBase):
    """This class represents the 'Requested C-state count' type of C-state."""

    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a requestable C-state."""
        return metric == "POLL" or (metric.startswith("C") and metric[1].isdigit() and
                                    not metric.endswith("%"))

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric

class ReqCSDef(_CSTypeBase):
    """This class represents the 'Requestable C-state' type of C-state."""

    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a requestable C-state."""
        return metric == "POLL%" or (metric.startswith("C") and metric[1].isdigit() and
                                     metric.endswith("%"))

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric[:-1]

class CoreCSDef(_CSTypeBase):
    """This class represents the 'Core C-state' type of C-state."""

    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a core C-state."""
        return metric.startswith("CPU%")

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric[4:]

class ModuleCSDef(_CSTypeBase):
    """This class represents the 'Module C-state' type of C-state."""

    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a module C-state."""
        return metric.startswith("Mod%")

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric[4:]

class PackageCSDef(_CSTypeBase):
    """This class represents the 'Package C-state' type of C-state."""

    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a package C-state."""
        return metric.startswith("Pkg%") or metric.startswith("Pk%")

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric.split("%", 1)[-1]

class UncoreFreqDef:
    """This class represents the 'Uncore Frequency' metric definition."""

    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the uncore frequency of a domain."""

        # 'turbostat' versions older than '2024.04.27' use 'UncMHz' to represent uncore frequency,
        # newer versions use the format 'UMHzX.Y' where 'X' = domain ID and 'Y' = fabric cluster.
        return metric == "UncMHz" or metric.startswith("UMHz")

    def __init__(self, metric):
        """The class constructor. """
        self.metric = metric

class TurbostatDefs(_STCDefsBase.STCDefsBase):
    """This module provides API to turbostat metrics definitions (AKA 'defs')."""

    def _mangle_placeholders(self, placeholders_info):
        """
        Mangle the definitions by substituting placeholders with real values. The arguments are as
        follows.
          * placeholders_info - a list or tuple of dictionaries describing how to mangle the
                                definitions by substituting placeholders with real values.

        The 'placeholders_info' list has the following format.
          [
           { "placeholder"   : placeholder,
             "values"        : list_of_values,
             "casesensitive" : boolean_value},
           ... etc ...
          ]

        Every dictionary in the list provides the following components to the mangler:
          placeholder - the placeholder string that has to be substituted with elements from the
                        'values' list.
          values - list of values to substitute the placeholder with.
          casesensitive - whether to use case-sensitive or case-insensitive matching and
                          substitution. 'True' by default.

        Example.

        The definitions YAML file includes the 'CCx%' metric:

           CCx%
              title: "CCx residence"
              description: "Time in percent spent in Cx core C-state. Matches turbostat CPU%cx."
              unit: "%"

        This metric describes core C-states. Core C-states are platform-dependent, so the real names
        are not known in advance. Therefore, the definitions YAML file uses the 'CCx' placeholder
        instead.

        Suppose the platform has CC1 and CC6 C-states. The 'placeholders_info' list could be the
        following in this case:
          [ { "placeholder" : "Cx",
              "values" : [ "C1", "C6" ],
              "casesensitive" : False, } ]

        The mangler would replace the 'CCx%' placeholder metric definition with the following.

           CC1%
              title: "CC1 residence"
              description: "Time in percent spent in C1 core C-state. Matches turbostat CPU%c1."
              unit: "%"
           CC6%
              title: "CC6 residence"
              description: "Time in percent spent in C6 core C-state. Matches turbostat CPU%c6."
              unit: "%"
        """

        # The sub-keys to look and substitute the placeholders in.
        mangle_subkeys = { "title", "descr", "fsname", "name" }

        for pinfo in placeholders_info:
            values = pinfo["values"]
            phld = pinfo["placeholder"]

            # Whether matching and replacement should be case-sensitive or not.
            # 1. Case-sensitive.
            #   * Match metrics that include the placeholder in the name.
            #   * Replace all placeholders with values in 'values'.
            # 2. Case-insensitive.
            #   * Match metrics that include the placeholder in the name, but accept both lower
            #     and upper cases.
            #   * Replace all placeholders with values in 'values'. But when replacing, if the
            #     original value was in upper case, use upper case, otherwise use lower case
            #     (preserve the case when replacing).
            case_sensitive = pinfo.get("casesensitive", True)

            if case_sensitive:
                regex = re.compile(phld)
            else:
                regex = re.compile(phld, re.IGNORECASE)

            for placeholder_metric in list(self.info):
                if not regex.search(placeholder_metric):
                    continue

                # We found the placeholder metric (e.g., 'CCx%'). Build the 'replacement' dictionary
                # which will replace the 'CCx' sub-dictionary with metric names (e.g., 'CC1' and
                # 'CC6').
                replacement = {}
                for val in values:
                    # pylint: disable=cell-var-from-loop,unnecessary-lambda-assignment
                    if case_sensitive:
                        func = lambda mo: val
                    else:
                        # The replacement function. Will replace with upper-cased or lower-cased
                        # 'val' depending on whether the replaced sub-string starts with a capital
                        # letter.
                        func = lambda mo: val.upper() if mo.group(0)[0].isupper() else val.lower()

                    metric = regex.sub(func, placeholder_metric)
                    replacement[metric] = self.info[placeholder_metric].copy()

                    for subkey, text in replacement[metric].items():
                        if subkey in mangle_subkeys:
                            replacement[metric][subkey] = regex.sub(func, text)

                # Construct new 'self.info' by replacing the placeholder metric with the replacement
                # metrics.
                new_info = {}
                for metric, minfo in self.info.items():
                    if metric != placeholder_metric:
                        new_info[metric] = minfo
                    else:
                        for new_metric, new_minfo in replacement.items():
                            new_info[new_metric] = new_minfo

                self.info = new_info

    def mangle_descriptions(self):
        """Mangle turbostat metric descriptions to describe how they are summarised by turbostat."""

        for metric, mdef in self.info.items():
            method = TurbostatParser.get_aggregation_method(metric)
            if method is not None:
                mdef["descr"] = f"{mdef['descr']} Calculated by finding the {method} of " \
                                f"\"{mdef['name']}\" across the system."

    def __init__(self, categories):
        """
        The class constructor. The arguments are as follows:
         * categories - a dictionary describing turbostat metrics categories.
        """

        super().__init__("turbostat")

        cstates = []
        for metric in categories["hardware"]["core"]:
            if CoreCSDef.check_metric(metric):
                cstates.append(CoreCSDef(metric).cstate)
        for metric in categories["hardware"]["module"]:
            if ModuleCSDef.check_metric(metric):
                cstates.append(ModuleCSDef(metric).cstate)
        for metric in categories["hardware"]["package"]:
            if PackageCSDef.check_metric(metric):
                cstates.append(PackageCSDef(metric).cstate)
        for metric in categories["requested"]["residency"]:
            if ReqCSDef.check_metric(metric):
                cstates.append(ReqCSDef(metric).cstate)

        placeholders = [{"placeholder": "PCx",
                         "values": cstates,
                         "casesensitive" : False},
                        {"placeholder": "Cx",
                         "values": cstates,
                         "casesensitive" : False},
                        {"placeholder": "UncMHz",
                         "values": cstates,
                         "casesensitive" : True},
                        # For package C-states with a name longer than 7 characters, 'turbostat'
                        # shortens the column from 'Pkg%pcX' to 'Pk%pcX'. We should mangle the
                        # metric definitions to account for # this.
                        {"placeholder": "Pkg",
                         "values": ["Pkg", "Pk"],
                         "casesensitive": True}
                        ]

        self._mangle_placeholders(placeholders)
