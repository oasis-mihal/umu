import json
import os
from typing import Tuple

from constants import Operators
from version_code import VersionCode


class Version:
    def __init__(self, version_code: VersionCode, config: dict):
        self._asset_url = config.get("asset_url", "")
        self._headers_dir = config.get("headers_dir", "include")
        self._libs_dir = config.get("libs_dir", "lib")
        self._is_zipped_folder = config.get("is_zipped_folder", False)
        self._platform_overrides = dict()
        self._version_code = version_code

        platforms = config.get("platforms", dict())
        for platform_name, platform_config in platforms.items():
            self._platform_overrides[platform_name] = PlatformOverride(platform_config)

    def get_asset_url(self, platform):
        platform_override: PlatformOverride = self._platform_overrides.get(platform, None)
        # Package is unsupported on this platform
        if platform_override is None:
            return None
        # Override the result if it is set per platform
        return platform_override.asset_url if platform_override.asset_url is not None else self._asset_url

    def get_headers_dir(self, platform):
        platform_override: PlatformOverride = self._platform_overrides.get(platform, None)
        # Package is unsupported on this platform
        if platform_override is None:
            return None
        # Override the result if it is set per platform
        return platform_override.headers_dir if platform_override.headers_dir is not None else self._headers_dir

    def get_libs_dir(self, platform):
        platform_override: PlatformOverride = self._platform_overrides.get(platform, None)
        # Package is unsupported on this platform
        if platform_override is None:
            return None
        # Override the result if it is set per platform
        return platform_override.libs_dir if platform_override.libs_dir is not None else self._libs_dir

    def get_is_zipped_folder(self, platform):
        platform_override: PlatformOverride = self._platform_overrides.get(platform, None)
        # Package is unsupported on this platform
        if platform_override is None:
            return None
        # Override the result if it is set per platform
        return platform_override.is_zipped_folder if platform_override.is_zipped_folder is not None else self._is_zipped_folder

    @property
    def version_code(self):
        return self._version_code

class PlatformOverride:
    def __init__(self, config: dict):
        self._asset_url = config.get("asset_url", None)
        self._headers_dir = config.get("headers_dir", None)
        self._libs_dir = config.get("libs_dir", None)
        self._is_zipped_folder = config.get("is_zipped_folder", None)

    @property
    def asset_url(self):
        return self._asset_url

    @property
    def headers_dir(self):
        return self._headers_dir

    @property
    def libs_dir(self):
        return self._libs_dir

    @property
    def is_zipped_folder(self):
        return self._is_zipped_folder

class PackageConfig:

    def __init__(self, config_filepath):
        if not os.path.exists(config_filepath):
            raise Exception(f"Path for package {config_filepath} does not exist")

        config: dict = None
        try:
            with open(config_filepath, "r") as f:
                config = json.load(f)
        except Exception as e:
            raise Exception(f"Could not load file from filepath {config_filepath}: {e}")

        # self._package_folder = package_folder
        self._package_name = config.get("name", "")
        self._pretty_name = config.get("pretty_name", self._package_name)
        self._versions = dict()

        versions = config.get("versions", dict())

        for version_number, version in versions.items():
            version_code = VersionCode(version_number)
            self._versions[version_code] = Version(version_code, version)

        self._versions = dict(sorted(self._versions.items()))

    # Operator can be
    # == version must be the exact version
    # ~= version must match the 1.0.x (check this Myka)
    # >= version must be greater than this version
    # <= version must be less than this version
    def get_version(self, operator, version_code: VersionCode) -> Tuple[VersionCode, Version]:
        if operator not in Operators.ALL:
            raise RuntimeError(f"Operator {operator} does not exist")

        if operator == Operators.EXACT:
            return version_code, self._versions[version_code]
        else:
            for key_version_code, version in self._versions.items():
                if operator == Operators.PATCH:
                    if key_version_code.is_same_patch(version_code):
                        return key_version_code, version
                elif operator == Operators.GREATER_EQ:
                    if key_version_code >= version_code:
                        return key_version_code, version
                elif operator == Operators.LESS_EQ:
                    if key_version_code <= version_code:
                        return key_version_code, version

        return None, None

    @property
    def all_versions(self):
        return self._versions.keys()

    @property
    def name(self):
        return self._package_name