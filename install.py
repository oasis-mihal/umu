import json
import os
import pathlib
import platform
import ctypes
import shutil
import urllib.parse
import zipfile
from distutils import dir_util
from pathlib import Path
from typing import Tuple

import constants
import handy_functions
from VenvData import VenvData, PackageData
from constants import Operators
from package_config import PackageConfig, Version
from version_code import VersionCode

class InstallManager:
    def __init__(self, venv_data: VenvData):
        self._venv_data = venv_data

    def get_platform(self):
        if self.is_windows:
            return "x64"
        else:
            raise NotImplementedError

    def get_umu_path(self) -> Path:
        path = None

        if self.is_windows:
            path = os.path.join(os.getenv('LOCALAPPDATA'), "umu", "umu_modules")
        else:
            raise NotImplementedError

        if not path:
            raise RuntimeError("No data folder found")

        if not os.path.exists(path):
            os.makedirs(path)

        return Path(path)

    @property
    def is_windows(self) -> bool:
        return platform.system() == "Windows"

    def get_temp_path(self) -> str:
        path = None

        if self.is_windows:
            path = os.path.join(os.getenv('TEMP'), "umu", "downloads")
        else:
            raise NotImplementedError

        if not path:
            raise RuntimeError("No data folder found")

        if not os.path.exists(path):
            os.makedirs(path)

        return path

    def get_venv_path(self) -> Path:
        env = os.environ
        venv_path = os.getenv("UMUENV_DIR")
        # Abs path for debugging purposes
        return Path(os.path.abspath(venv_path))

    def get_resolved_name(self, package_name: str, platform: str, version: str) -> str:
        return f"{package_name}_v{version}_{platform}"

    def check_for_package(self, package_name: str, platform: str, version: str):
        package_dir = f"{package_name}_v{version}_{platform}"

        if os.path.exists(os.path.join(self.get_venv_path().as_posix(), package_name)):
            print("Package found in venv folder")
            return True

        if os.path.exists(os.path.join(self.get_umu_path().as_posix(), package_dir)):
            print("Package exists in umu central folder")
            return True

    def get_config_url(self, package_name, platform: str, version: str) -> str:
        url = r"http://localhost:8080/package/?"
        params = dict(
            name=package_name
        )
        return f"{url}{urllib.parse.urlencode(params)}"
        #r"http://localhost:8080/package/?name=visual-leak-detector&hvisual-leak-detector-config"

    def get_modules_path(self, resolved_name) -> Path:
        umuenv_path = self.get_venv_path()
        umu_path = self.get_umu_path()

        # Determine if we're on the same drive, otherwise we need a satellite directory
        if umuenv_path.drive != umu_path.drive:
            # We can't hardlink between these two, return a satellite directory on this drive E:\\.umu\\
            satellite_dir = f"{umuenv_path.drive}{os.path.sep}.umu"
            if not os.path.exists(satellite_dir):
                os.makedirs(satellite_dir)
                if self.is_windows:
                    FILE_ATTRIBUTE_HIDDEN = 0x02
                    ret = ctypes.windll.kernel32.SetFileAttributesW(satellite_dir, FILE_ATTRIBUTE_HIDDEN)
            return Path(os.path.join(satellite_dir, "modules", resolved_name))
        else:
            return umu_path.joinpath(resolved_name)

    def install_package_from_server(self, package_name: str, operator: constants.Operators, version_code: VersionCode,
                                    force_reinstall=False):
        # TODO: Don't redownload, just link the package
        #if not force_reinstall and self.check_for_package(package_name, self.get_platform(), version_code):
            # TODO: Set a flag here and copy to the new directory
        #    return

        # Download the config file
        config_url = self.get_config_url(package_name, self.get_platform(), version_code)
        config_download_path = os.path.join(self.get_umu_path().as_posix(), f"{package_name}.json")
        if force_reinstall and os.path.exists(config_download_path):
            os.remove(config_download_path)
        handy_functions.download_url(config_url, config_download_path)

        config: PackageConfig = PackageConfig(config_download_path)
        new_version_code, version = config.get_version(operator, version_code)

        if version is None:
            all_versions_str = "\n".join([str(x) for x in config.all_versions])
            raise RuntimeError(f"No version found matching '{package_name}{operator}{version_code}'"
                               f" from available packages:\n{all_versions_str}")

        # Check if we already meet the requirements
        do_install = False
        installed_package = self._venv_data.packages.get(package_name)
        if installed_package is not None:
            installed_version_code = installed_package.version_code
            if force_reinstall:
                do_install = True
            elif operator == Operators.EXACT and installed_version_code != version_code:
                do_install = True
            elif operator == Operators.GREATER_EQ and installed_version_code < version_code:
                do_install = True
            elif operator == Operators.LESS_EQ and installed_version_code > version_code:
                do_install = True
            else:
                print(f"Package requirements already satisfied: {str(installed_package)}")
                return True
        else:
            do_install = True

        version_code = new_version_code

        # Download the package
        print(f"Downloading package {config.name} version={version_code}")
        url = version.get_asset_url(self.get_platform())#get_package_url(package_name, get_platform(), version_code)

        resolved_name = self.get_resolved_name(package_name, self.get_platform(), version_code)
        zip_download_path = os.path.join(self.get_temp_path(), resolved_name+".zip")
        r_file, r_html = handy_functions.download_url(url, zip_download_path, show_progress=True)

        if not os.path.exists(zip_download_path):
            raise RuntimeError("Failed to download packages")

        # Un-zip the package to the right directory
        print(f"\tExtracting package")

        central_path = self.get_modules_path(resolved_name).as_posix()

        if os.path.exists(central_path):
            # TODO: Warn about this if other projects are hardlinked to this file
            shutil.rmtree(central_path)

        core = None
        with zipfile.ZipFile(zip_download_path, 'r') as zip_ref:
            zipinfos = zip_ref.infolist()

            for zipinfo in zipinfos:
                if core is None:
                    path = pathlib.Path(zipinfo.filename)
                    if len(path.parts) > 0:
                        core = path.parts[0]
                zip_ref.extract(zipinfo, central_path)

        # Zip file is done extracting, but we might have to updir the whole thing
        # if someone zipped it wrong
        # if version.get_is_zipped_folder(self.get_platform()) and core is not None:
        # TODO: Maybe there's a triple zip??
        if core is not None:
            dir_util.copy_tree(os.path.join(central_path, core), central_path,)
            shutil.rmtree(os.path.join(central_path, core))


        # shutil.copytree(url, central_path)

        print(f"\tMaking links")
        self.link_package_to_venv(config, central_path, version)
        print(f"\tSuccessfully installed {config.name} version={version_code}")

    def link_package_to_venv(self, config: PackageConfig, central_path: str, version: Version):
        # Paths are for the specific package
        central_libs_path = os.path.join(central_path, version.get_libs_dir(self.get_platform()))

        # Link libs dir
        venv_libs_path = os.path.join(self.get_venv_path().as_posix(), "libs")

        root, dirs, files = next(os.walk(central_libs_path))

        package_data = PackageData(config.name, version.version_code, files)
        self._venv_data.add_package(package_data)
        # TODO: Ignore dirs for now
        for file in files:
            filepath = os.path.join(root, file)
            linked_file_path = os.path.join(venv_libs_path, file)
            if os.path.exists(linked_file_path):
                os.remove(linked_file_path)

            # TODO: Symlinks require administrator permission
            # I'd rather use hard links, but they don't work between drives
            # Idea, create a satellite directory on the current drive and copy
            # the required files. Then keep track of the hard links to this satellite
            # It's gonna do weird stuff when deleted, make sure to deal with the recycle bin issue
            #try:
            os.link(filepath, linked_file_path)
            #except:
            #    os.symlink(filepath, linked_file_path)

        # Link include dirs
        central_headers_path = os.path.join(central_path, version.get_headers_dir(self.get_platform()))
        venv_include_path = os.path.join(self.get_venv_path().as_posix(), "include", config.name)

        if os.path.exists(venv_include_path):
            os.rmdir(venv_include_path)

        # try:
        # fsutil hardlink list MyFileName.txt
        if self.is_windows:
            import _winapi
            _winapi.CreateJunction(central_headers_path, venv_include_path)
        else:
            os.link(central_headers_path, venv_include_path)
        #except:
        #    os.symlink(central_headers_path, venv_include_path, target_is_directory=True)

    def parse_command(self, cmd: str) -> Tuple[str, Operators, VersionCode]:
        operator_found = False
        for op in Operators.ALL:
            if cmd.find(op) >= 0:
                if operator_found:
                    # TODO: Give line errors
                    raise RuntimeError("More than one operator found")
                operator = op
                split_args = cmd.split(op)
                operator_found = True

        # Only the package name was specifed
        if not operator_found:
            package_name = cmd
            version_code = VersionCode("0.0.0")
            operator = Operators.GREATER_EQ
        # Package name and version were specified
        elif operator_found and len(split_args) == 2:
            package_name = split_args[0]
            try:
                version_code = VersionCode(split_args[1])
            except Exception as e:
                raise RuntimeError(f"'{split_args[1]}' is not a valid semantic version code")
        else:
            raise RuntimeError("command could not be parsed")

        return package_name, operator, version_code


    def install_from_requirements(self, requirements_file):
        try:
            with open(requirements_file, "r") as f:
                lines = f.readlines()
        except:
            print(f"Could not read file {requirements_file}")
            return

        line: str
        for line_num, line in enumerate(lines):
            line = line.strip()
            # Comment, continue
            if line.startswith("#"):
                continue
            try:
                package_name, operator, version_code = self.parse_command(line)
            except Exception as e:
                raise RuntimeError(f"Error on line {line_num} of file {requirements_file}: {e}")
            self.install_package_from_server(package_name, operator, version_code)

    def install_single(self, cmd, args):
        package_name, operator, version_code = self.parse_command(cmd)
        force_reinstall = args.force_reinstall
        self.install_package_from_server(package_name, operator, version_code, force_reinstall)

    def uninstall_single(self, cmd):
        package_name, operator, version_code = self.parse_command(cmd)
        self.uninstall_package(package_name, operator, version_code)

    def uninstall_from_requirements(self, requirements_file):
        try:
            with open(requirements_file, "r") as f:
                lines = f.readlines()
        except:
            print(f"Could not read file {requirements_file}")
            return

        line: str
        for line in lines:
            line = line.strip()
            # Comment, continue
            if line.startswith("#"):
                continue
            package_name, operator, version_code = self.parse_command(line)
            self.uninstall_package(package_name, operator, version_code)

    def uninstall_package(self, package_name: str, operator: Operators, version_code: VersionCode):
        package_data = self._venv_data.packages.get(package_name, None)
        if package_data is None:
            print(f"Skipping package {package_name} as it is not installed")
            return False

       # Unlink libs dir
        venv_libs_path = os.path.join(self.get_venv_path().as_posix(), "libs")

        # TODO: Ignore dirs for now
        for file in package_data.installed_lib_paths:

            linked_file_path = os.path.join(venv_libs_path, file)
            if os.path.exists(linked_file_path):
                os.remove(linked_file_path)

        # Unlink include dir
        venv_include_path = os.path.join(self.get_venv_path().as_posix(), "include", package_data.name)

        if os.path.exists(venv_include_path):
            os.rmdir(venv_include_path)

        # Remove the package from the config
        self._venv_data.remove_package(package_data.name)

if __name__ == "__main__":
    install_mgr = InstallManager()
    install_mgr.install_from_requirements("test_proj/requirements.umu")
    # install_mgr.install_package_from_server("visual-leak-detector", constants.Operators.EXACT, VersionCode("1.0.0"))



