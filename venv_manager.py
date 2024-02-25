import json
import os
import subprocess
from typing import List

import handy_functions
from constants import CPPVersion


class VenvManager:

    def __init__(self):
        path = os.getcwd()
        self._umuenv_dir = os.path.join(path, "umuenv")

    def create(self, cpp_version_s: str):
        if os.path.exists(self._umuenv_dir):
            print(f"umuenv already exists at path: {self._umuenv_dir}")
            return False

        try:
            cpp_version: CPPVersion = handy_functions.str_to_cpp_version(cpp_version_s)
        except ValueError as e:
            print(f"{e}")
            return False

        os.mkdir(self._umuenv_dir)
        os.mkdir(os.path.join(self._umuenv_dir, "include"))
        os.mkdir(os.path.join(self._umuenv_dir, "libs"))
        os.mkdir(self.data_dir_path)

        # TODO: Port this to linux
        self.write_activate_bat()
        self.write_data_json(cpp_version)

        return True

    def write_data_json(self, cpp_version: CPPVersion):
        contents = dict(cpp_version=cpp_version, packages={})
        with open(self.data_file_path, "w+") as f:
            json.dump(contents, f, indent=4)

    def write_activate_bat(self):
        """
        Writes the activate file for windows
        """
        contents: List[str] = [
            "@echo off",
            "REM Add a prompt the cmd line",
            "set PROMPT=(umuenv)$P$G",
            "\n",
            "REM Set venv dir to umuenv",
            "pushd %~dp0",
            "set UMUENV_DIR=%CD%",
            "popd",
            "\n",
            "set UMU_HEADERS=%UMUENV_DIR%\include",
            "set UMU_LIBS=%UMUENV_DIR%\libs",
        ]
        with open(os.path.join(self._umuenv_dir, "activate.bat"), "w+") as f:
            f.writelines("\n".join(contents))

    @property
    def data_dir_path(self) -> str:
        return os.path.join(self._umuenv_dir, "data")

    @property
    def data_file_path(self):
        return os.path.join(self.data_dir_path, "data.json")