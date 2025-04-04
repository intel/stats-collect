# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Misc. helper functions related to file-system operations.
"""

import os
import shutil
from pathlib import Path
from pepclibs.helperlibs.Exceptions import ErrorExists

# pylint: disable=wildcard-import,unused-wildcard-import
from pepclibs.helperlibs.FSHelpers import *

def _mkdir(path: Path):
    """Create a directory."""

    try:
        path.mkdir(parents=True, exist_ok=True)
    except (OSError, shutil.Error) as err:
        errmsg = Error(err).indent(2)
        raise Error(f"failed to create directory '{path}':\n{errmsg}") from err

def _copy_file(src: Path, dst: Path):
    """Implement the 'copy_file()' function."""

    _mkdir(dst.parent)

    try:
        shutil.copyfile(src, dst)
    except (OSError, shutil.Error) as err:
        errmsg = Error(err).indent(2)
        raise Error(f"failed to copy file '{src}' to '{dst}':\n{errmsg}") from err

def _copy_dir(src: Path, dst: Path):
    """Implement the 'copy_dir()' function."""

    _mkdir(dst.parent)

    try:
        if dst.resolve() in src.resolve().parents:
            raise Error(f"cannot recursively copy '{src}' to '{dst}': the destination is a "
                        f"sub-path of the source")

        shutil.copytree(src, dst, copy_function=shutil.copy)
    except (OSError, shutil.Error) as err:
        errmsg = Error(err).indent(2)
        raise Error(f"failed to copy directory '{src}' to '{dst}':\n{errmsg}") from err

def copy(src: Path, dst: Path, exist_ok: bool=False, is_dir: bool=None):
    """
    Copy 'src' directory to 'dst'. The arguments are as follows.
      * src - the source directory path.
      * dst - the destination directory path.
      * exist_ok - if the destination directory 'dst' already exists, just return if 'True',
                   raise an exception if 'False'.
      * is_dir - if 'src' is a directory, passing 'True' avoids a file type check.
    """

    try:
        exists = dst.exists()
    except OSError as err:
        errmsg = Error(err).indent(2)
        raise Error(f"failed to check if directory '{dst}' exists:\n{errmsg}") from err

    if exists:
        if exist_ok:
            return
        raise ErrorExists(f"cannot copy directory '{src}' to '{dst}': the destination path already "
                          f"exists")

    if is_dir is None:
        try:
            is_dir = src.is_dir()
        except OSError as err:
            errmsg = Error(err).indent(2)
            raise Error(f"failed to check if '{src}' is a directory:\n{errmsg}") from err

    if is_dir:
        _copy_dir(src, dst)
    else:
        _copy_file(src, dst)

def symlink(linkpath: Path, target: Path, exist_ok: bool=False, relative: bool=False):
    """
    Create a symbolic link at path 'symlink' pointing to path 'target'. The arguments are as
    follows.
      * linkpath - path to the symbolic link to create.
      * target - path the symbolic link should point to.
      * exist_ok - if 'symlink' already exists, just return if 'True', raise an exception if
                   'False'.
      * relative - if 'False', use 'target' as-is, otherwise transform 'target' to a path relative
                   to 'symlink'.
    """

    try:
        exists = linkpath.exists()
    except OSError as err:
        errmsg = Error(err).indent(2)
        raise Error(f"failed to check if directory '{linkpath}' exists:\n{errmsg}") from err

    if exists:
        if exist_ok:
            return
        raise ErrorExists(f"cannot create symbolic link '{linkpath}': already exists")

    if relative:
        try:
            exists = target.exists()
        except OSError as err:
            errmsg = Error(err).indent(2)
            raise Error(f"failed to check if '{target}' exists:\n{errmsg}") from err

        resolved = {}
        for var in ("target", "linkpath"):
            try:
                resolved[var] = locals()[var].resolve()
            except OSError as err:
                errmsg = Error(err).indent(2)
                raise Error(f"failed to resolve path '{locals()[var]}':\n{errmsg}") from err

        try:
            # Use 'os.path.relpath()' instead of 'Path.relative_to()' because the latter when the
            # target is not in the subpath of base.
            target = os.path.relpath(resolved["target"], start=resolved["linkpath"].parent)
        except OSError as err:
            errmsg = Error(err).indent(2)
            raise Error(f"failed to construct path of '{target}' relative to '{linkpath}':\n"
                        f"{errmsg}") from err

    _mkdir(linkpath.parent)

    try:
        os.symlink(target, linkpath)
    except OSError as err:
        errmsg = Error(err).indent(2)
        raise Error(f"failed create a symlink '{linkpath}' -> '{target}':\n{errmsg}") from err
