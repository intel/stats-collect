# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Report ID is a string identifying a test report. It usually contains something descriptive and
human-readable. This module contains helper function for dealing with a report IDs.
"""

import re
import time
from pepclibs.helperlibs.Exceptions import Error

MAX_REPORTID_LEN = 128
# The special characters allowed in the report ID. The author of this code avoided using characters
# that are unsafe for URLs.
SPECIAL_CHARS = "-.,_:"

def get_charset_descr(special_chars=None):
    """
    Return a string describing the allowable report ID characters. The arguments are as follows.
      * special_chars - a string containing the special characters allowed in the report ID. By
                        default, alphanumeric characters and characters in 'SPECIAL_CHARS' are
                        allowed, and this argument makes it possible to override the characters in
                        'SPECIAL_CHARS'.
    """
    if special_chars is None:
        special_chars = SPECIAL_CHARS

    chars_list = [f"'{char}'" for char in special_chars]
    chars = ", ".join(chars_list[:-1])
    chars += f", and {chars_list[-1]}"
    return f"ASCII alphanumeric, {chars}"

def format_reportid(prefix=None, separator="-", reportid=None, strftime="%Y%m%d-%H%M%S",
                    append=None, special_chars=None):
    """
    Format and return a report ID. The arguments are as follows.
      * prefix - the report ID prefix.
      * separator - the report ID components (AKA monikers) separator.
      * reportid - the report ID string to extend and return.
      * strftime - in case the 'reportid' argument is 'None', the current date and time is used, and
                   this argument defines the pattern (will be passed to 'time.strftime()').
      * append - a string to append to the report ID.
      * special_chars - a string containing the special characters allowed in the report ID. By
                        default, alphanumeric characters and characters in 'SPECIAL_CHARS' are
                        allowed, and this argument makes it possible to override the characters in
                        'SPECIAL_CHARS'.
    """

    if not reportid:
        reportid = time.strftime(strftime)

    result = ""
    if prefix:
        result += prefix.rstrip(separator)
        if not reportid.startswith(separator):
            result += separator

    result += reportid

    if append:
        if not reportid.endswith(separator):
            result += separator
        result += append.lstrip(separator)

    return validate_reportid(result, special_chars=special_chars)

def validate_reportid(reportid, special_chars=None):
    """
    Validate a report ID string. The arguments are as follows.
      * reportid - the report ID string to validate.
      * special_chars - a string containing the special characters allowed in the report ID. By
                        default, alphanumeric characters and characters in 'SPECIAL_CHARS' are
                        allowed, and this argument makes it possible to override the characters in
                        'SPECIAL_CHARS'.
    """

    if len(reportid) > MAX_REPORTID_LEN:
        raise Error(f"too long run ID ({len(reportid)} characters), the maximum allowed length is "
                    f"{MAX_REPORTID_LEN} characters")

    if special_chars is None:
        special_chars = SPECIAL_CHARS

    chars = SPECIAL_CHARS
    if not re.match(rf"^[A-Za-z0-9{chars}]+$", reportid):
        charset_descr = get_charset_descr()
        raise Error(f"bad report ID '{reportid}'\n"
                    f"Please, use only the following characters: {charset_descr}")

    return reportid
