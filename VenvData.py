import json
from typing import List, Dict

import handy_functions
from constants import CPPVersion
from version_code import VersionCode


class VenvData:
    def __init__(self, venv_path: str):
        self._venv_path = venv_path

        data_json = None
        with open(venv_path, "r") as f:
            data_json = json.load(f)

        cpp_version_s = data_json.get("cpp_version", None)
        self._cpp_version: CPPVersion = handy_functions.str_to_cpp_version(cpp_version_s)

        self._packages = dict()
        for package_name, package_dict in data_json.get("packages", dict()).items():
            self._packages[package_name] = PackageData.from_config(package_name, package_dict)

    def add_package(self, package_data: "PackageData"):
        self._packages[package_data.name] = package_data

        # Save immediately
        data = dict(cpp_version=self.cpp_version, packages={k:v.to_dict() for k, v in self.packages.items()})
        with open(self._venv_path, "w+") as f:
            json.dump(data, f, indent=4)

    def remove_package(self, package_name: str):
        self._packages.pop(package_name)

        # Save immediately
        data = dict(cpp_version=self.cpp_version, packages={k: v.to_dict() for k, v in self.packages.items()})
        with open(self._venv_path, "w+") as f:
            json.dump(data, f, indent=4)

    @property
    def cpp_version(self) -> CPPVersion:
        return self._cpp_version

    @property
    def packages(self) -> Dict[str, "PackageData"]:
        return self._packages

    @property
    def package_names(self) -> List[str]:
        return self._packages.keys()



class PackageData:
    def __init__(self, name: str, version_code: VersionCode, installed_lib_paths: List[str]):
        self._name = name
        self._version_code = version_code
        self._installed_lib_paths = installed_lib_paths

    @classmethod
    def from_config(cls, name: str, config: dict) -> "PackageData":
        version_s = config.get("version_code", None)
        version_code = VersionCode(version_s)
        installed_lib_paths = config.get("installed_libs", None)
        return cls(name, version_code, installed_lib_paths)

    @property
    def name(self) -> str:
        return self._name
    @property
    def version_code(self) -> VersionCode:
        return self._version_code

    @property
    def installed_lib_paths(self) -> List[str]:
        return self._installed_lib_paths

    def __str__(self):
        return f"{self.name}=={self.version_code}"

    def to_dict(self) -> dict:
        return dict(name=self.name, version_code=str(self._version_code), installed_libs=self._installed_lib_paths)







