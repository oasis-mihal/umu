import os
import platform
import shutil
import zipfile
from pathlib import Path
import wget

import constants
from package_config import PackageConfig


def get_platform():
    if platform.system() == "Windows":
        return "x64"
    else:
        raise NotImplementedError

def get_umu_path() -> str:
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

def get_temp_path() -> str:
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

def get_venv_path() -> str:
    env = os.environ
    venv_path = os.getenv("UMUENV_DIR")
    # Abs path for debugging purposes
    return os.path.abspath(venv_path)

def get_resolved_name(package_name: str, platform: str, version: str) -> str:
    return f"{package_name}_v{version}_{platform}"

def check_for_package(package_name: str, platform: str, version: str):
    package_dir = f"{package_name}_v{version}_{platform}"

    if os.path.exists(os.path.join(get_venv_path(), package_name)):
        print("Package found in venv folder")
        return True

    if os.path.exists(os.path.join(get_umu_path(), package_dir)):
        print("Package exists in umu central folder")
        return True

def get_package_url(package_name, platform: str, version: str) -> str:
    return r"http://localhost:8080/visual-leak-detector"

def install_package_from_server(package_name: str, version: str):
    # TODO: Parameterize this
    force_reinstall = True
    if not force_reinstall and check_for_package(package_name, get_platform(), version):
        return

    # Download the package
    url = get_package_url(package_name, get_platform(), version)
    resolved_name = get_resolved_name(package_name, get_platform(), version)

    download_path = os.path.join(get_temp_path(), resolved_name+".zip")
    wget.download(url, download_path)

    # Un-zip the package to the right directory
    central_path = os.path.join(get_umu_path(), resolved_name)

    if force_reinstall and os.path.exists(central_path):
        shutil.rmtree(central_path)

    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(get_umu_path())

    # shutil.copytree(url, central_path)

    link_package_to_venv(central_path, force_reinstall)

def link_package_to_venv(central_path: str, force_reinstall: bool):
    print(central_path)

    config = PackageConfig(central_path, f"{central_path}.json")

    # Paths are for the specific package
    central_libs_path = config.libs_dir
    venv_libs_path = os.path.join(get_venv_path(), "libs")
    print (venv_libs_path)

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


if __name__ == "__main__":
    install_package_from_server("visual-leak-detector", "1.0.0")



