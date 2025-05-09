# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "deploy" 'stats-collect' command implementation.
"""

from statscollecttools import _Common, ToolInfo
from statscollectlibs.deploy import _Deploy

def deploy_command(args, deploy_info):
    """Implements the 'deploy' command."""

    with _Common.get_pman(args) as pman:
        with _Deploy.Deploy(ToolInfo.TOOLNAME, deploy_info, pman, args.tmpdir_path,
                            args.keep_tmpdir, args.debug) as depl:
            depl.deploy()
