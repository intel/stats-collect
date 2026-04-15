# Copyright (C) 2023-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Ensure source-tree packages take priority over system-installed versions.

Importing this module inserts the project root and the sibling 'pepc' directory at the front of
'sys.path', so that 'pepclibs' and 'statscollectlibs' are always resolved from the source tree,
not from any system-installed location.
"""

import sys
from pathlib import Path

_prjroot = Path(__file__).parent.parent.resolve()
_pepcroot = _prjroot.parent / "pepc"

if not _pepcroot.is_dir():
    print(f"Error: Sibling 'pepc' source directory not found at '{_pepcroot}'", file=sys.stderr)
    raise SystemExit(1)

sys.path.insert(0, str(_pepcroot))
sys.path.insert(0, str(_prjroot))
