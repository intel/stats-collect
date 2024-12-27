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

def _copy_file(src: Path, dst: Path):
    """Implement the 'copy_file()' function."""

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    except (OSError, shutil.Error) as err:
        errmsg = Error(err).indent(2)
        raise Error(f"failed to copy file '{src}' to '{dst}':\n{errmsg}") from err

def _copy_dir(src: Path, dst: Path):
    """Implement the 'copy_dir()' function."""

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)

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

def move_copy_link(src, dst, action="symlink", exist_ok=False):
    """
    Move, copy. or link the 'src' file or directory to 'dst' depending on 'action'. The arguments
    are as follows.
      * src - the source file or directory path.
      * dst - the destination file or directory path.
      * action - one of 'move', 'copy', or 'symlink', to move 'src' to 'st', copy 'src' to 'dst',
                 or create a 'src' symlink pointing to 'dst'.
      * exist_ok - if the destination file or directory 'dst' already exists, just return if 'True',
                   raise an exception if 'False'.
    """

    exists_err = f"cannot {action} '{src}' to '{dst}', the destination path already exists"
    if dst.exists():
        if exist_ok:
            return
        raise ErrorExists(exists_err)

    # Type cast in shutil.move() can be removed when python is fixed. See
    # https://bugs.python.org/issue32689
    try:
        if action == "move":
            if src.is_dir():
                try:
                    dst.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    if not exist_ok:
                        raise ErrorExists(exists_err) from None
                for item in src.iterdir():
                    shutil.move(str(item), dst)
            else:
                shutil.move(str(src), dst)
        elif action == "copy":
            if not dst.parent.exists():
                dst.parent.mkdir(parents=True)

            if src.is_dir():
                _copy_dir(src, dst)
            else:
                shutil.copyfile(src, dst)
        elif action == "symlink":
            if not dst.is_dir():
                dstdir = dst.parent
            else:
                dstdir = dst

            if not dst.parent.exists():
                dst.parent.mkdir(parents=True)

            os.symlink(os.path.relpath(src.resolve(), dstdir.resolve()), dst)
        else:
            raise Error(f"unrecognized action '{action}'")
    except (OSError, shutil.Error) as err:
        raise Error(f"cannot {action} '{src}' to '{dst}':\n{err}") from err
