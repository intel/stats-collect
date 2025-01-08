# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2024-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
SPECjbb2015 controller log parser.
"""

import re
import time
import datetime
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat
from statscollectlibs.parsers import _ParserBase

# The SPECjbb2015 time-stamp regular expression. Examples of the time-stamp:
# * <Fri Dec 20 08:34:58 PST 2024>
# * <Tue Aug 15 20:01:03 EEST 2017>
_TS = r"\<(([^\W\d_]{3} [^\W\d_]{3} \d{2} \d{2}:\d{2}:\d{2}) ([^\W\d_]{3,4}) (\d{4}))\>"

# All sorts of timezone names and their offset in seconds, to parse SPECjbb2015 time-stamps.
_TIMEZONES = {"A": 3600, "ACDT": 37800, "ACST": 34200, "ACT": 28800, "ADT": -10800, "AEDT": 39600,
              "AEST": 36000, "AFT": 16200, "AKDT": -28800, "AKST": -32400, "ALMT": 21600,
              "AMST": 18000, "AMT": 14400, "ANAST": 43200, "ANAT": 43200, "AQTT": 18000,
              "ART": -10800, "AST": -14400, "AWDT": 32400, "AWST": 28800, "AZOT": -3600,
              "AZST": 18000, "AZT": 14400, "B": 7200, "BDT": 28800, "BIOT": 21600, "BNT": 28800,
              "BOT": -14400, "BRST": -7200, "BRT": -10800, "BTT": 21600, "C": 10800, "CAST": 28800,
              "CAT": 7200, "CCT": 23400, "CDT": -18000, "CEDT": 7200, "CEST": 7200, "CET": 3600,
              "CIST": -28800, "CKT": -36000, "CLST": -10800, "CLT": -14400, "COST": -14400,
              "COT": -18000, "CST": -21600, "CVT": -3600, "CXT": 25200, "ChST": 36000, "D": 14400,
              "DAVT": 25200, "DFT": 3600, "E": 18000, "EASST": -18000, "EAST": -21600, "EAT": 10800,
              "ECT": -18000, "EDT": -14400, "EEDT": 10800, "EEST": 10800, "EET": 7200, "EGST": 0,
              "EGT": -3600, "EST": -18000, "ET": -18000, "F": 21600, "FJST": 46800, "FJT": 43200,
              "FKST": -10800, "FKT": -14400, "FNT": -7200, "G": 25200, "GALT": -21600,
              "GAMT": -32400, "GET": 14400, "GFT": -10800, "GILT": 43200, "GIT": -32400, "GMT": 0,
              "GST": 14400, "GYT": -14400, "H": 28800, "HAA": -10800, "HAC": -18000, "HADT": -32400,
              "HAE": -14400, "HAP": -25200, "HAR": -21600, "HAST": -36000, "HAT": -9000,
              "HAY": -28800, "HKT": 28800, "HLV": -16200, "HMT": 18000, "HNA": -14400,
              "HNC": -21600, "HNE": -18000, "HNP": -28800, "HNR": -25200, "HNT": -12600,
              "HNY": -32400, "HOVT": 25200, "HST": -36000, "I": 32400, "ICT": 25200, "IDT": 10800,
              "IOT": 21600, "IRDT": 16200, "IRKST": 32400, "IRKT": 28800, "IRST": 12600,
              "JST": 32400, "K": 36000, "KGT": 21600, "KRAST": 28800, "KRAT": 25200, "KST": 32400,
              "KUYT": 14400, "L": 39600, "LHDT": 39600, "LHST": 37800, "M": 43200, "MAGST": 43200,
              "MAGT": 39600, "MART": -34200, "MAWT": 18000, "MDT": -21600, "MHT": 43200,
              "MIT": -34200, "MMT": 23400, "MSD": 14400, "MST": -25200, "MUT": 14400, "MVT": 18000,
              "MYT": 28800, "N": -3600, "NCT": 39600, "NDT": -9000, "NFT": 41400, "NOVST": 25200,
              "NOVT": 21600, "NPT": 20700, "NST": -12600, "NT": -12600, "NUT": -39600,
              "NZDT": 46800, "NZST": 43200, "O": -7200, "OMSST": 25200, "OMST": 21600, "P": -10800,
              "PDT": -25200, "PET": -18000, "PETST": 43200, "PETT": 43200, "PGT": 36000,
              "PHT": 28800, "PKT": 18000, "PMDT": -7200, "PMST": -10800, "PONT": 39600,
              "PST": -28800, "PT": -28800, "PWT": 32400, "PYST": -10800, "PYT": -14400, "Q": -14400,
              "R": -18000, "RET": 14400, "S": -21600, "SAMT": 14400, "SAST": 7200, "SBT": 39600,
              "SCT": 14400, "SGT": 28800, "SLT": 19800, "SRT": -10800, "SST": -39600, "T": -25200,
              "TAHT": -36000, "TFT": 18000, "THA": 25200, "TJT": 18000, "TKT": -36000, "TLT": 32400,
              "TMT": 18000, "TVT": 43200, "U": -28800, "ULAT": 28800, "UTC": 0, "UYST": -7200,
              "UYT": -10800, "UZT": 18000, "V": -32400, "VET": -16200, "VLAST": 39600,
              "VLAT": 36000, "VUT": 39600, "W": -36000, "WAST": 7200, "WAT": 3600, "WDT": 32400,
              "WEDT": 3600, "WEST": 3600, "WET": 0, "WFT": 43200, "WGST": -7200, "WGT": -10800,
              "WIB": 25200, "WIT": 32400, "WITA": 28800, "WST": 28800, "WT": 0, "X": -39600,
              "Y": -43200, "YAKST": 36000, "YAKT": 32400, "YAPT": 36000, "YEKST": 21600,
              "YEKT": 18000, "Z": 0}

class SPECjbb2015CtrlLogParser(_ParserBase.ParserBase):
    """Provide API for parsing the SPECjbb2015 controller log."""

    def probe(self):
        """
        Return 'True' if the data does look like SPECjbb2015 controller log, raise 'ErrorBadFormat'
        otherwise.
        """

        if self._probe_status is not None:
            if self._probe_status is True:
                return True
            raise self._probe_status

        # The beginning of the controller log.
        log_start_regex = re.compile("^" + _TS + " org.spec.jbb.ic: Init IC$")

        for line in self._lines:
            if re.match(log_start_regex, line):
                self._probe_status = True
                return True

            self._lines_probed += 1
            if self._lines_probed > 1024:
                break

        self._probe_status = ErrorBadFormat("not SPECjbb2015 controller log")
        raise self._probe_status

    def _find_hbir(self):
        """
        Keep parsing SPECjbb2015 controller log until the HBIR value pattern is met. Return HBIR.
        """

        # The measured HBIR value regular expression. Line example:
        # <Fri Dec 20 08:39:37 PST 2024> org.spec.jbb.controller: high-bound for max-jOPS is
        # measured to be 80627
        hbir_regex = re.compile("^" + _TS + r" org.spec.jbb.controller: high-bound for max-jOPS is "
                                            r"measured to be (\d+)$")

        for line in self._lines:
            match = re.match(hbir_regex, line)
            if not match:
                continue

            return Trivial.str_to_int(match[5], what="HBIR")

        raise ErrorBadFormat("HBIR value was not found in SPECjbb2015 controller log")

    def _process_rt_line(self, match, info, start):
        """
        Process regex match object for an RT-curve log line. Return 'True' if more RT-curve lines
        are expected, otherwise return 'False'.
        """

        # Remove the time-zone part from the time-stamp, because 'strptime()' does not support
        # SPECjbb log time-zone formats.
        ts = match[2] + " " + match[4]
        # The time-stamp format without time-zone.
        ts_format = "%a %b %d %H:%M:%S %Y"
        # Parse the time-stamp, make it be UTC time, and then time in the original time-zone.
        ts = datetime.datetime.strptime(ts, ts_format)
        ts = ts.replace(tzinfo=datetime.timezone.utc)
        ts = ts.timestamp() - _TIMEZONES[match[3]]

        if "rt_curve" not in info:
            info["rt_curve"] = {"levels": {}}

        levels = info["rt_curve"]["levels"]

        if start:
            self._pcnt = Trivial.str_to_int(match[6], what="Load level percent")
            if self._pcnt not in levels:
                levels[self._pcnt] = {}
            if "first_level" not in info["rt_curve"]:
                info["rt_curve"]["first_level"] = self._pcnt

        level = levels[self._pcnt]

        if start:
            level["ts"] = int(ts)
        else:
            status = match[7]
            if status != "OK":
                del levels[self._pcnt]
                return False

            info["rt_curve"]["last_level"] = self._pcnt
            level["status"] = status
            level["ir"] = Trivial.str_to_int(match[5], what=f"Load level {self._pcnt}% IR")
            info["max_jops"] = level["ir"]

        return True

    def _next(self):
        """Yield a dictionary containing SPECjbb2015 information."""

        self.probe()

        info = {}

        try:
            info["hbir"] = self._find_hbir()
        except StopIteration:
            raise Error("failed to find HBIR value") from None

        # The regular expression for matching the beginning of an RT curve period. Example:
        # <Tue Aug 15 20:01:03 EEST 2017> org.spec.jbb.controller: RT curve for IR = 1448 (86%*hbIR)
        start_regex = r"^" + _TS + \
                      r" org.spec.jbb.controller: RT curve for IR = (\d+) \( ?(\d+)%\*hbIR\)$"

        # The regular expression for matching the ending of an RT curve period. Example:
        # <Tue Aug 15 20:01:03 EEST 2017> org.spec.jbb.controller: RT_CURVE: IR = 139804 finished,
        # steady status = [OK] (rIR:aIR:PR = 29520:29427:29360) (tPR = 437064)
        end_regex = r"^" + _TS + r" org.spec.jbb.controller: RT_CURVE: IR = (\d+) " \
                                 r"finished, (steady|settle) status = \[(.+)\].*$"


        for line in self._lines:
            match = re.match(start_regex, line)
            if match:
                self._process_rt_line(match, info, True)
            match = re.match(end_regex, line)
            if match:
                if not self._process_rt_line(match, info, False):
                    break

        yield info

    def __init__(self, path=None, lines=None):
        """
        The class constructor. Arguments are as follows.
          * path - same as in ParserBase.__init__().
          * lines - same as in ParserBase.__init__().
        """

        self._lines_probed = 0
        self._probe_status = None
        self._pcnt = None

        super().__init__(path, lines)
