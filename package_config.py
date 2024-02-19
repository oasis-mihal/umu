import json
import os


class PackageConfig:

    def __init__(self, package_folder, config_filepath):
        if not os.path.exists(config_filepath):
            raise Exception(f"Path for package {config_filepath} does not exist")

        config: dict = None
        try:
            with open(config_filepath, "r") as f:
                config = json.load(f)
        except Exception as e:
            raise Exception(f"Could not load file from filepath {config_filepath}: {e}")

        self._package_folder = package_folder
        self._package_name = config.get("name", "")
        self._headers_dir = config.get("headers_dir", "include")
        self._libs_dir = config.get("libs_dir", "lib")

    @property
    def headers_dir(self):
        return os.path.join(self._package_folder, self._headers_dir)

    @property
    def libs_dir(self):
        return os.path.join(self._package_folder, self._libs_dir)

    @property
    def name(self):
        return self._package_name