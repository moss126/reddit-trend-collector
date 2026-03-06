import requests
import time

class RedditHttp:
    def __init__(self, ua, sleep=1, timeout=20):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": ua})
        self.sleep = float(sleep)
        self.timeout = float(timeout)

    def get(self, url, params=None):
        time.sleep(self.sleep)
        r = self.s.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
