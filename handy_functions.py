import urllib.request
from tqdm import tqdm

from constants import CPPVersion


def split(delimiters, string, maxsplit=0):
    import re
    regex_pattern = '|'.join(map(re.escape, delimiters))
    return re.split(regex_pattern, string, maxsplit)

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b*bsize - self.n)

def download_url(url, output_path, show_progress=False):
    if show_progress:
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
            return urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)
    else:
        return urllib.request.urlretrieve(url, filename=output_path)

def str_to_cpp_version(s: str) ->CPPVersion:
    match s.lower():
        case "cpp_98" | "cpp98" | "c++98":
            return CPPVersion.CPP_98
        case "cpp_03" | "cpp03" | "c++03":
            return CPPVersion.CPP_03
        case "cpp_11" | "cpp11" | "c++11":
            return CPPVersion.CPP_11
        case "cpp_14" | "cpp14" | "c++14":
            return CPPVersion.CPP_14
        case "cpp_17" | "cpp17" | "c++17":
            return CPPVersion.CPP_17
        case "cpp_20" | "cpp20" | "c++20":
            return CPPVersion.CPP_20
        case "cpp_23" | "cpp23" | "c++23":
            return CPPVersion.CPP_23
        case _:
            all_versions = ", ".join([x.value for x in CPPVersion])
            raise ValueError(f"Not a valid cpp version, valid options are: {all_versions}")


