import json
import os
import pathlib
import platform
import shutil
import urllib.parse
import zipfile
from distutils import dir_util
from pathlib import Path
from typing import Tuple

import constants
import handy_functions
from constants import Operators
from package_config import PackageConfig, Version
from version_code import VersionCode

class InstallManager():
    def get_platform(self):
        if platform.system() == "Windows":
            return "x64"
        else:
            raise NotImplementedError

    def get_umu_path(self) -> str:
        path = None

        if platform.system() == "Windows":
            path = os.path.join(os.getenv('LOCALAPPDATA'), "umu", "umu_modules")
        else:
            raise NotImplementedError

        if not path:
            raise RuntimeError("No data folder found")

        if not os.path.exists(path):
            os.makedirs(path)

        return path

    def get_temp_path(self) -> str:
        path = None

        if platform.system() == "Windows":
            path = os.path.join(os.getenv('TEMP'), "umu", "downloads")
        else:
            raise NotImplementedError

        if not path:
            raise RuntimeError("No data folder found")

        if not os.path.exists(path):
            os.makedirs(path)

        return path

    def get_venv_path(self) -> str:
        env = os.environ
        venv_path = os.getenv("UMUENV_DIR")
        # Abs path for debugging purposes
        return os.path.abspath(venv_path)

    def get_resolved_name(self, package_name: str, platform: str, version: str) -> str:
        return f"{package_name}_v{version}_{platform}"

    def check_for_package(self, package_name: str, platform: str, version: str):
        package_dir = f"{package_name}_v{version}_{platform}"

        if os.path.exists(os.path.join(self.get_venv_path(), package_name)):
            print("Package found in venv folder")
            return True

        if os.path.exists(os.path.join(self.get_umu_path(), package_dir)):
            print("Package exists in umu central folder")
            return True

    def get_config_url(self, package_name, platform: str, version: str) -> str:
        url = r"http://localhost:8080/package/?"
        params = dict(
            name=package_name
        )
        return f"{url}{urllib.parse.urlencode(params)}"
        #r"http://localhost:8080/package/?name=visual-leak-detector&hvisual-leak-detector-config"


    def install_package_from_server(self, package_name: str, operator: constants.Operators, version_code: VersionCode):
        # TODO: Parameterize this
        force_reinstall = True
        if not force_reinstall and self.check_for_package(package_name, self.get_platform(), version_code):
            return

        # Download the config file
        config_url = self.get_config_url(package_name, self.get_platform(), version_code)
        config_download_path = os.path.join(self.get_umu_path(), f"{package_name}.json")
        if force_reinstall and os.path.exists(config_download_path):
            os.remove(config_download_path)
        handy_functions.download_url(config_url, config_download_path)

        config: PackageConfig = PackageConfig(config_download_path)
        new_version_code, version = config.get_version(operator, version_code)

        if version is None:
            all_versions_str = "\n".join([str(x) for x in config.all_versions])
            raise RuntimeError(f"No version found matching '{package_name}{operator}{version_code}'"
                               f" from available packages:\n{all_versions_str}")
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
        central_path = os.path.join(self.get_umu_path(), resolved_name)

        if force_reinstall and os.path.exists(central_path):
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
        self.link_package_to_venv(config, central_path, version, force_reinstall)
        print(f"\tSuccessfully installed {config.name} version={version_code}")

    def link_package_to_venv(self, config: PackageConfig, central_path: str, version: Version, force_reinstall: bool):
        # Paths are for the specific package
        central_libs_path = os.path.join(central_path, version.get_libs_dir(self.get_platform()))

        # Link libs dir
        venv_libs_path = os.path.join(self.get_venv_path(), "libs")

        root, dirs, files = next(os.walk(central_libs_path))
        # TODO: Ignore dirs for now
        for file in files:
            filepath = os.path.join(root, file)
            linked_file_path = os.path.join(venv_libs_path, file)
            if force_reinstall and os.path.exists(linked_file_path):
                os.remove(linked_file_path)

            # TODO: Symlinks require administrator permission
            # I'd rather use hard links, but they don't work between drives
            try:
                os.link(filepath, linked_file_path)
            except:
                os.symlink(filepath, linked_file_path)

        # Link include dirs
        central_headers_path = os.path.join(central_path, version.get_headers_dir(self.get_platform()))
        venv_include_path = os.path.join(self.get_venv_path(), "include", config.name)

        if force_reinstall and os.path.exists(venv_include_path):
            os.rmdir(venv_include_path)

        try:
            os.link(central_headers_path, venv_include_path)
        except:
            os.symlink(central_headers_path, venv_include_path, target_is_directory=True)

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
        if len(split_args) != 2:
            raise RuntimeError("command could not be parsed")

        package_name = split_args[0]
        if not operator_found:
            raise RuntimeError(f"operator is not a valid umu operator.")
        try:
            version_code = VersionCode(split_args[1])
        except Exception as e:
            raise RuntimeError(f"'{split_args[1]}' is not a valid semantic version code")

        return package_name, operator, version_code


    def install_from_requirements(self, requirements_file):
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
            self.install_package_from_server(package_name, operator, version_code)

    def install_single(self, cmd):
        package_name, operator, version_code = self.parse_command(cmd)
        self.install_package_from_server(package_name, operator, version_code)



if __name__ == "__main__":
    install_mgr = InstallManager()
    install_mgr.install_from_requirements("test_proj/requirements.umu")
    # install_mgr.install_package_from_server("visual-leak-detector", constants.Operators.EXACT, VersionCode("1.0.0"))



