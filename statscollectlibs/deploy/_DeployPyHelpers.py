
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide API for deploying Python helpers (non-driver installables and deployables). Refer to the
'DeployBase' module docstring for more information.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import stat
import typing
from pathlib import Path
from pepclibs.helperlibs import Logging, LocalProcessManager, ProjectFiles
from pepclibs.helperlibs import ToolChecker
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.deploy import DeployHelpersBase

if typing.TYPE_CHECKING:
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from statscollectlibs.deploy.DeployBase import InstallableInfoTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class DeployPyHelpers(DeployHelpersBase.DeployHelpersBase):
    """
    Provide API for deploying Python helpers (non-driver installables and deployables).

    Notes:
        - Dependencies are discovered via the '--print-module-paths' option rather than
          'PythonPrjInstaller', which pip-installs the project into a venv from a local source
          directory or a git URL. That approach requires the project sources, but helpers may be
          deployed when stats-collect is installed from a package (no sources available). The
          '--print-module-paths' option works in both cases: it queries the already-running
          interpreter for its module paths.
    """

    def __init__(self,
                 prjname: str,
                 toolname: str,
                 spman: ProcessManagerType,
                 bpman: ProcessManagerType,
                 stmpdir: Path,
                 btmpdir: Path,
                 cpman: ProcessManagerType | None = None,
                 ctmpdir: Path | None = None,
                 btchk: ToolChecker.ToolChecker | None = None,
                 debug: bool = False):
        """
        Initialize a class instance.

        Args:
            prjname: Name of the project the Python helpers and 'toolname' belong to.
            toolname: Name of the tool the Python helpers belong to.
            spman: A process manager object associated with the SUT (System Under Test).
            bpman: A process manager object associated with the "build" host (the host which should
                   be used for creating the standalone versions of the Python helpers).
            stmpdir: Path to a temporary directory on the SUT.
            btmpdir: Path to a temporary directory on the "build" host.
            cpman: A process manager object associated with the controller (local host). Defaults to
                   'spman'.
            ctmpdir: Path to a temporary directory on the controller. Defaults to 'stmpdir'.
            btchk: For checking the availability of various tools on the "build" host. Created
                   if not provided.
            debug: If 'True', be more verbose.
        """

        what = f"{toolname} Python helpers"
        super().__init__(prjname, toolname, what, spman, bpman, stmpdir, btmpdir, cpman=cpman,
                         ctmpdir=ctmpdir, btchk=btchk, debug=debug)

    def _find_deployable_src(self, deployable: str, subdir: str = "") -> Path:
        """
        Find and return the path to a Python helper deployable on the local host.

        Args:
            deployable: The name of the Python helper deployable to find.
            subdir: Optional sub-directory under the project helpers search roots where the
                    deployable resides. By default, the deployable is located directly under the
                    search root.

        Returns:
            The absolute path to the Python helper deployable.
        """

        with LocalProcessManager.LocalProcessManager() as lpman:
            deployable_path = ProjectFiles.find_project_helper(self._prjname, deployable,
                                                               tpath=subdir, pman=lpman)

            deployable_path = lpman.abspath(deployable_path)

            if not lpman.is_exe(deployable_path):
                raise Error(f"Path '{deployable_path}' exists, but it is not an executable file")

        return deployable_path

    @staticmethod
    def _get_deployable_dependencies(deployable_path: Path) -> list[Path]:
        """
        Find and return the dependencies of a Python helper deployable script. Execute the given
        Python helper script with the '--print-module-paths' option to retrieve its dependencies.

        Args:
            deployable_path: The path to the Python helper deployable script.

        Returns:
            A list of paths to the dependencies of the Python helper script.
        """

        # All Python helper deployables must implement the '--print-module-paths' option.
        cmd = f"{deployable_path} --print-module-paths"
        with LocalProcessManager.LocalProcessManager() as lpman:
            stdout, _ = lpman.run_verify_join(cmd)
        return [Path(path) for path in stdout.splitlines()]

    @staticmethod
    def _get_relative_path(src: Path) -> Path:
        """
        Return the path of a Python source file relative to its package root.

        Walk up from 'src' until a directory without an '__init__.py' is found. That directory is
        the package root. The returned path is used as the entry path inside the zipapp archive,
        so it preserves the importable package structure.

        Args:
            src: Absolute path to a Python source file.

        Returns:
            Path to 'src' relative to its package root.

        Example:
            src     = Path("/home/user/git/pepc/pepclibs/helperlibs/Logging.py")
            result  = Path("pepclibs/helperlibs/Logging.py")
        """

        pkg_dir = src.parent
        while (pkg_dir / "__init__.py").exists():
            pkg_dir = pkg_dir.parent
        return src.relative_to(pkg_dir)

    def _create_standalone_deployable(self, deployable_path: Path, outdir: Path):
        """
        Create a standalone zipapp version of a Python helper deployable.

        Package the Python helper program along with its dependencies into a single executable
        file: write a Python shebang line, followed by a zip containing '__main__.py' (the
        deployable script) and all its dependencies.

        Args:
            deployable_path: Path to the Python helper deployable script on the local system
                             (controller).
            outdir: Path to the output directory. The standalone file is saved here under the
                    deployable's name.
        """

        import zipfile # pylint: disable=import-outside-toplevel

        deployable = deployable_path.name
        deps = self._get_deployable_dependencies(deployable_path)

        # Create an empty '__init__.py' file. We will copy it to the subdirectories of the
        # dependencies.
        init_path = outdir / "__init__.py"
        try:
            with init_path.open("w"):
                pass
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to create file '{init_path}':\n{errmsg}") from err

        standalone_path = outdir / deployable
        try:
            with standalone_path.open("wb") as fobj:
                fobj.write(b"#!/usr/bin/python3\n")
                with zipfile.ZipFile(fobj, "w", compression=zipfile.ZIP_DEFLATED) as zipobj:
                    zipobj.write(deployable_path, arcname="./__main__.py")
                    pkgdirs: set[Path] = set()
                    for src in deps:
                        # Add the dependency using its package-relative path, so it is importable
                        # at runtime.
                        dst = self._get_relative_path(src)
                        zipobj.write(src, arcname=dst)
                        pkgdir = dst.parent
                        for idx, _ in enumerate(pkgdir.parts):
                            pkgdirs.add(Path(*pkgdir.parts[:idx+1]))
                    # Ensure the '__init__.py' file is present in all subdirectories.
                    zipped_files = {Path(name) for name in zipobj.namelist()}
                    for pkgdir in pkgdirs:
                        path = pkgdir / "__init__.py"
                        if path not in zipped_files:
                            zipobj.write(init_path, arcname=pkgdir / "__init__.py")
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Failed to create standalone '{standalone_path}':\n{errmsg}") from err

        try:
            mode = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
            standalone_path.chmod(mode)
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"Cannot make '{standalone_path}' executable:\n{errmsg}") from err

    def _prepare(self, insts_info: dict[str, InstallableInfoTypedDict], insts_basedir: Path):
        """
        Build and prepare installables for deployment.

        Args:
            insts_info: The installables information dictionary.
            insts_basedir: Path to the base directory that contains the installables on the
                          controller.
        """

        # Build stand-alone version of every Python deployable.
        for installable, inst_info in insts_info.items():
            _LOG.info("Building a stand-alone version of the '%s' installable", installable)
            outdir = self._ctmpdir / installable
            self._cpman.mkdir(outdir, parents=True)
            for deployable in inst_info["deployables"]:
                deployable_path = self._find_deployable_src(deployable,
                                                            subdir=inst_info.get("subdir", ""))
                self._create_standalone_deployable(deployable_path, outdir)
