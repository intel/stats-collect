
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide API for deploying Python helpers (non-driver installables and deployables). Refer to the
'DeployBase' module docstring for more information.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
from pepclibs.helperlibs import Logging, ClassHelpers, LocalProcessManager, ProjectFiles
from pepclibs.helperlibs import ToolChecker
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.deploy import DeployHelpersBase

if typing.TYPE_CHECKING:
    from typing import cast
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from statscollectlibs.deploy.DeployBase import InstallableInfoTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class DeployPyHelpers(DeployHelpersBase.DeployHelpersBase):
    """Provides API for deploying Python helpers (non-driver installables and deployables)."""

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
            stmpdir: A temporary directory on the SUT.
            btmpdir: Path to a temporary directory on the "build" host.
            cpman: A process manager object associated with the controller (local host). Defaults to
                   'spman'.
            ctmpdir: Path to a temporary directory on the controller. Defaults to 'stmpdir'.
            btchk: An instance of 'ToolChecker' that can be used for checking the availability of
                   various tools on the "build" host. Will be created if not provided.
            debug: A boolean variable for enabling additional debugging messages.
        """

        what = f"{toolname} Python helpers"
        super().__init__(prjname, toolname, what, spman, bpman, stmpdir, btmpdir, cpman=cpman,
                         ctmpdir=ctmpdir, btchk=btchk, debug=debug)

    def _find_deployable_src(self, deployable: str) -> Path:
        """
        Find and return the path to a Python helper deployable on the local host.

        Args:
            deployable: The name of the Python helper deployable to find.

        Returns:
            The absolute path to the Python helper deployable.
        """

        with LocalProcessManager.LocalProcessManager() as lpman:
            deployable_path = ProjectFiles.find_project_helper(self._prjname, deployable,
                                                               pman=lpman)

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
            pyhelper_path: The path to the Python helper deployable script.

        Returns:
            list[Path]: A list of paths to the dependencies of the Python helper script.
        """

        # All Python helper deployables must implement the '--print-module-paths' option, which
        # prints the dependencies.
        cmd = f"{deployable_path} --print-module-paths"
        with LocalProcessManager.LocalProcessManager() as lpman:
            stdout, _ = lpman.run_verify(cmd)
        return [Path(path) for path in stdout.splitlines()]

    def _create_standalone_deployable(self, deployable_path: Path, outdir: Path):
        """
        Create a standalone version of a Python helper deployable.

        Package the Python helper program along with its dependencies into a single file. Use the
        standard technique:
            * Create a zip archive of the Python helper and all its dependencies.
            * Append the zip archive to an executable file with a Python shebang.

        Args:
            deployable_path: Path to the Python helper deployable script on the local system
                             (controller).
            outdir: Path to the output directory. The standalone version of the Python helper
                    deployable script will be saved in this directory under the
                    "{deployable_path.name}.standalone" name.
        """

        import zipfile # pylint: disable=import-outside-toplevel

        deployable = deployable_path.name

        deps = self._get_deployable_dependencies(deployable_path)

        # Create an empty '__init__.py' file. We will be copy it to the sub-directories of the
        # dependencies.
        init_path = outdir / "__init__.py"
        try:
            with init_path.open("w+"):
                pass
        except OSError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Failed to create file '{init_path}:\n{msg}'") from None

        try:
            # pylint: disable=consider-using-with
            fobj = zipobj = None

            # Start creating the stand-alone version of the deployable: create an empty file and
            # write # python shebang there.
            standalone_path = outdir / f"{deployable}.standalone"
            try:
                fobj = standalone_path.open("bw+")
                fobj.write("#!/usr/bin/python3\n".encode("utf-8"))
            except OSError as err:
                msg = Error(str(err)).indent(2)
                raise Error(f"Failed to create and initialize file '{standalone_path}:\n"
                            f"{msg}") from err

            # Create a zip archive in the 'standalone_path' file. The idea is that this file will
            # start with python shebang, and then include compressed version the script and its
            # dependencies. Python interpreter is smart and can run such zip archives.
            try:
                zipobj = zipfile.ZipFile(fobj, "w", compression=zipfile.ZIP_DEFLATED)
            except Exception as err:
                msg = Error(str(err)).indent(2)
                raise Error(f"Failed to initialize a zip archive from file "
                            f"'{standalone_path}':\n{msg}") from err

            # Make 'zipobj' raises exceptions of type 'Error', so that we do not have to wrap every
            # 'zipobj' operation into 'try/except'.
            wrapped_zipobj = ClassHelpers.WrapExceptions(zipobj)
            if typing.TYPE_CHECKING:
                zipobj = cast(zipfile.ZipFile, wrapped_zipobj)
            else:
                zipobj = wrapped_zipobj

            # Put the deployable to the archive under the '__main__.py' name.
            zipobj.write(deployable_path, arcname="./__main__.py")

            pkgdirs = set()

            for src in deps:
                # Form the destination path. It is just part of the source path staring from the
                # 'statscollectlibs' of 'pepclibs' components.
                components = ("statscollectlibs", "statscollecttools", "pepclibs")
                for component in components:
                    try:
                        idx = src.parts.index(component)
                        break
                    except ValueError:
                        continue
                else:
                    raise Error(f"Python program '{deployable}' has bad dependency '{src}' - "
                                f"the path does not have any of the components: "
                                f"{', '.join(components)}.")

                dst = Path(*src.parts[idx:])
                zipobj.write(src, arcname=dst)

                # Collect all directory paths present in the dependencies. They are all python
                # packages and we'll have to ensure we have the '__init__.py' file in each of the
                # sub-directory.
                pkgdir = dst.parent
                for idx, _ in enumerate(pkgdir.parts):
                    pkgdirs.add(Path(*pkgdir.parts[:idx+1]))

            # Ensure the '__init__.py' file is present in all sub-directories.
            zipped_files = {Path(name) for name in zipobj.namelist()}
            for pkgdir in pkgdirs:
                path = pkgdir / "__init__.py"
                if path not in zipped_files:
                    zipobj.write(init_path, arcname=pkgdir / "__init__.py")
        finally:
            if zipobj:
                zipobj.close()
            if fobj:
                fobj.close()

        # Make the standalone file executable.
        try:
            mode = standalone_path.stat().st_mode | 0o777
            standalone_path.chmod(mode)
        except OSError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Cannot change '{standalone_path}' file mode to {oct(mode)}:\n"
                        f"{msg}") from err

        # And rename to get rid of the '.standalone' suffix.
        final_standalone_path = outdir / deployable
        try:
            # Remove the '.standalone' suffix.
            standalone_path.rename(final_standalone_path)
        except OSError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Cannot rename '{standalone_path}' to "
                        f"'{final_standalone_path}':\n{msg}") from err

    def _prepare(self, insts_info: dict[str, InstallableInfoTypedDict], insts_basedir: Path):
        """
        Build and prepare installables for deployment.

        Args:
            insts_info: The installables information dictionary.
            installs_basedir: Path to the base directory that contains the installables on the
                              controller.
        """

        # Copy Python helpers to the temporary directory on the controller.
        for installable, inst_info in insts_info.items():
            dstdir = self._ctmpdir / installable
            self._cpman.mkdir(dstdir, parents=True)

            for deployable in inst_info["deployables"]:
                srcpath = insts_basedir / deployable
                _LOG.debug("Copying Python deployable %s:\n  '%s' -> '%s'",
                           deployable, srcpath, dstdir)
                self._cpman.rsync(srcpath, dstdir, remotesrc=False, remotedst=False)

        # Build stand-alone version of every Python deployable.
        for installable, inst_info in insts_info.items():
            _LOG.info("Building a stand-alone version of the '%s' installable", installable)
            outdir = self._ctmpdir / installable
            for deployable in inst_info["deployables"]:
                deployable_path = self._find_deployable_src(deployable)
                self._create_standalone_deployable(deployable_path, outdir)
