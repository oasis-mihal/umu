class VersionCode:
    def __init__(self, version_str: str):
        try:
            splits = version_str.split('.')
            if len(splits) != 3:
                raise RuntimeError('Not a valid version code')
            self._major = int(splits[0])
            self._minor = int(splits[1])
            self._patch = int(splits[2])
        except Exception as e:
            raise RuntimeError('Not a valid version code')

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    @property
    def patch(self) -> int:
        return self._patch

    def is_same_patch(self, other: "VersionCode") -> bool:
        if self.major != other.major:
            return False
        if self.minor != other.minor:
            return False
        return True

    def __eq__(self, other: "VersionCode") -> bool:
        if self.major != other.major:
            return False
        if self.minor != other.minor:
            return False
        if self.patch != other.patch:
            return False
        return True

    def __gt__(self, other: "VersionCode") -> bool:
        if self.major > other.minor:
            return True
        if self.minor > other.minor:
            return True
        if self.patch > other.patch:
            return True
        return False

    def __lt__(self, other: "VersionCode") -> bool:
        if self.major < other.minor:
            return True
        if self.minor < other.minor:
            return True
        if self.patch < other.patch:
            return True
        return False

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"



