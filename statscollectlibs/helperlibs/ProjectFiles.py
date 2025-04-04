# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""This module is a collection of miscellaneous functions that interact with project paths."""

# pylint: disable=wildcard-import,unused-wildcard-import
from pepclibs.helperlibs.ProjectFiles import *

def get_project_web_assets_envar(prjname):
    """
    Return the name of the environment variable that points to the web assets location of project
    'prjname'.
    """

    name = prjname.replace("-", "_").upper()
    return f"{name}_WEB_ASSETS_PATH"

def find_project_web_assets(prjname, datadir, pman=None, what=None):
    """
    Search for project 'prjname' web assets. The arguments are as follows:
      * prjname - name of the project the web-asset belongs to.
      * datadir - the sub-path of the web-asset in the web-asset project installation base
                  directory.
      * datadir - name of the sub-directory containing the web asset. This method basically
                  searches for 'datadir' in a set of pre-defined paths (see below).
      * pman - the process manager object for the host to find the web-asset on (local host by
               default).
      * what - human-readable description of 'subpath' (or what is searched for), which will be used
               in the error message if an error occurs.

    The web-assets are searched for in the 'datadir' directory (or sub-path) of the following
    directories (and in the following order).
      * in the directory the of the running program.
      * in the directory specified by the '<prjname>_WEB_ASSETS_PATH' environment variable.
      * in '$HOME/.local/share/javascript/<prjname>/', if it exists.
      * in '$HOME/share/javascript/<prjname>/', if it exists.
      * in '$VIRTUAL_ENV/share/javascript/<prjname>/', if the variable is defined and the directory
            it exists.
      * in '/usr/local/share/javascript/<prjname>/', if it exists.
      * in '/usr/share/javascript/<prjname>/', if it exists.
    """

    return next(search_project_data(f"javascript/{prjname}", datadir, pman=pman, what=what,
                                    envars=(get_project_web_assets_envar(prjname),)))
