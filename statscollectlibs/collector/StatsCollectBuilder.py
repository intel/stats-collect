# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for building an instance of 'StatsCollect'."""

import contextlib
from pepclibs.helperlibs import Logging, Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.collector import StatsCollect
from statscollectlibs.deploylibs import DeployBase
from statscollectlibs.rawresultlibs import WORawResult

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

DEFAULT_STNAMES = ("turbostat", "sysinfo")

class StatsCollectBuilder(ClassHelpers.SimpleCloseContext):
    """This class provides the API for building an instance of 'StatsCollect'."""

    def parse_stnames(self, stnames):
        """
        Parse the statistics names string 'stnames'. Arguments are as follows:
         * stnames - a string containing a comma-separated list of statistic names. The "!" symbol
                     at the beginning of a statistics name means that this statistics should not be
                     collected. There are two special keywords which can be used:
                        1. "all": include all discovered statistics.
                        2. "default": include only the default set of statistics.

        This method parses statistics names into the following class properties: 'include',
        'exclude', 'discover'.
        """

        for stname in Trivial.split_csv_line(stnames):
            if stname in ("", "none"):
                continue

            if stname == "all":
                self.discover = "all"
            elif stname == "default":
                self.discover = DEFAULT_STNAMES
            elif stname.startswith("!"):
                # The "!" prefix indicates that the statistics must not be collected.
                stname = stname[1:]
                self.exclude.add(stname)
            else:
                self.include.add(stname)

        bogus = self.include & self.exclude
        if bogus:
            bogus = ", ".join(bogus)
            raise Error(f"cannot simultaneously include and exclude the following statistics: "
                        f"{bogus}")

        StatsCollect.check_stnames(self.include)
        StatsCollect.check_stnames(self.exclude)

    def parse_intervals(self, intervals):
        """
        Parse a string containing statistics collectors' intervals. The arguments are as follows:
        * intervals - a comma-separated list of "stname:interval" entries, where 'stname' is the
                      statistics name, and 'interval' is the desired collection interval in seconds.

        This method parses statistics collectors' intervals into the 'intervals' class property.
        """

        for entry in Trivial.split_csv_line(intervals):
            split = Trivial.split_csv_line(entry, sep=":")
            if len(split) != 2:
                raise Error(f"bad intervals entry '{entry}', should be 'stname:interval', where "
                            f"'stname' is the statistics name and 'interval' is a floating point "
                            f"interval for collecting the 'stname' statistics.")
            stname, interval = split # pylint: disable=unbalanced-tuple-unpacking
            StatsCollect.check_stname(stname)

            if not Trivial.is_float(interval):
                raise Error(f"bad interval value '{interval}' for the '{stname}' statistics: "
                            f"should be a positive floating point or integer number")

            self.intervals[stname] = float(interval)

    def build_stcoll(self, pman, res, local_outdir=None, remote_outdir=None, local_path=None,
                     remote_path=None):
        """
        Build and return an instance of 'StatsCollect' based on the statistics named in the class
        properties 'discover', 'include', 'exclude' and 'intervals'. Arguments are the same as
        'StatsCollect.StatsCollect.__init__()', except for:
         * local_path - path to the 'stc-agent' program on the local system. By default, this method
                        will search for 'stc-agent' on the local system.
         * remote_path - path to the 'stc-agent' program on the remote system. By default, this
                         method will search for 'stc-agent' on the remote system.
        """

        stcoll = StatsCollect.StatsCollect(pman, res, local_outdir=local_outdir,
                                           remote_outdir=remote_outdir)
        stcoll.set_info_logging(True)

        if self.discover:
            stcoll.set_enabled_stats(self.discover)
            stcoll.set_disabled_stats(self.exclude)
        else:
            stcoll.set_disabled_stats("all")
            stcoll.set_enabled_stats(self.include)

        if "acpower" in stcoll.get_enabled_stats():
            # Assume that power meter is configured to match the SUT name.
            if pman.is_remote:
                devnode = pman.hostname
            else:
                devnode = "default"

            with contextlib.suppress(Error):
                stcoll.set_prop("acpower", "devnode", devnode)

        # Configure the 'stc-agent' program path.
        local_needed, remote_needed = stcoll.is_stcagent_needed()
        if local_needed and not local_path:
            local_path = DeployBase.get_installed_helper_path("stats-collect", "stats-collect",
                                                              "stc-agent")
        if remote_needed and not remote_path:
            remote_path = DeployBase.get_installed_helper_path("stats-collect", "stats-collect",
                                                               "stc-agent", pman=pman)

        stcoll.set_stcagent_path(local_path=local_path, remote_path=remote_path)

        stcoll.set_intervals(self.intervals)

        if self.discover:
            stcoll.set_enabled_stats(self.discover)
            stcoll.set_disabled_stats(self.exclude)

            discovered = stcoll.discover()

            # Make sure that all the required statistics are actually available.
            not_found = self.include - (discovered & self.include)
            if not_found:
                not_found = ", ".join(not_found)
                raise Error(f"the following statistics cannot be collected: {not_found}")

            stcoll.set_disabled_stats("all")
            stcoll.set_enabled_stats(discovered)
        else:
            stcoll.set_disabled_stats("all")
            stcoll.set_enabled_stats(self.include)

        stcoll.configure()

        if not stcoll.get_enabled_stats():
            _LOG.info("No statistics will be collected")
            stcoll.close()
            return None

        return stcoll

    def build_stcoll_nores(self, pman, reportid, cpus=None, cmd=None, local_outdir=None,
                           remote_outdir=None, local_path=None, remote_path=None):
        """
        Same as 'build_stcoll()', but does not require the caller creating a 'WORawResult' object.
        The arguments are the same as in 'build_stcoll()', except for 'reportid', 'cpus', and
        'cmd', which are the same as in 'StatsCollect.StatsCollect.__init__()'.
        """

        self._res = WORawResult.WORawResult(reportid, local_outdir, cmd=cmd, cpus=cpus)
        return self.build_stcoll(pman, self._res, local_outdir=local_outdir,
                                 remote_outdir=remote_outdir, local_path=local_path,
                                 remote_path=remote_path)

    def __init__(self):
        """Class constructor."""

        self._res = None

        # Statistic names that should try to be discovered. Statistic names in 'exclude' will not
        # try to be discovered.
        self.discover = set()
        # Statistics names that should be collected.
        self.include = set()
        # Statistics names that should not be collected.
        self.exclude = set()
        # Statistics collection intervals. Maps statistic names to collection intervals which are in
        # seconds.
        self.intervals = {}

    def close(self):
        """Close the statistics collector."""
        ClassHelpers.close(self, close_attrs=("_res", ))
