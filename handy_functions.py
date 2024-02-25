import urllib.request
from tqdm import tqdm

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