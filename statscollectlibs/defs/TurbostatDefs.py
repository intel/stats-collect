# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API to turbostat metrics definitions (AKA 'defs')."""

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

class PackageCSDef(_CSTypeBase):
    """This class represents the 'Package C-state' type of C-state."""

    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a package C-state."""
        return metric.startswith("Pkg%") or metric.startswith("Pk%")

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric.split("%", 1)[-1]

class ModuleCSDef(_CSTypeBase):
    """This class represents the 'Module C-state' type of C-state."""

    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a module C-state."""
        return metric.startswith("Mod%")

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric[4:]

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

    def mangle_descriptions(self):
        """Mangle turbostat metric descriptions to describe how they are summarised by turbostat."""

        for metric, mdef in self.info.items():
            method = TurbostatParser.get_aggregation_method(metric)
            if method is not None:
                mdef["descr"] = f"{mdef['descr']} Calculated by finding the {method} of " \
                                f"\"{mdef['name']}\" across the system."

    def __init__(self, cstates, uncfreq_defs=None):
        """
        The class constructor. Arguments are as follows:
         * cstates - a list of C-states parsed from raw turbostat statistic files.
         * uncfreq_defs - a list of 'UncoreFreqDef' instances representing uncore frequency metrics
                          from raw turbostat statistic files.
        """

        uncfreq_defs = [] if uncfreq_defs is None else [udef.metric for udef in uncfreq_defs]

        super().__init__("turbostat")

        # The "POLL" state has its own definition so does not need to be mangled into the template
        # C-state definitions.
        if "POLL" in cstates:
            cstates.remove("POLL")

        placeholders = [{"placeholder": "PCx", "values": cstates, "casesensitive" : False},
                        {"placeholder": "Cx", "values": cstates, "casesensitive" : False},
                        {"placeholder": "UncMHz", "values": uncfreq_defs, "casesensitive" : True}]
        # For package C-states with a name longer than 7 characters, 'turbostat' shortens the
        # column from 'Pkg%pcX' to 'Pk%pcX'. We should mangle the metric definitions to account for
        # this.
        placeholders.append({"placeholder": "Pkg", "values": ["Pkg", "Pk"], "casesensitive" : True})
        self._mangle_placeholders(placeholders)
