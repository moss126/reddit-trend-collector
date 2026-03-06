import time
import random
import requests


class RedditHttp:

    def __init__(self, ua, sleep=1, timeout=20, max_retries=5):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": ua})
        self.sleep = float(sleep)
        self.timeout = float(timeout)
        self.max_retries = int(max_retries)

    def get(self, url, params=None):

        last_err = None

        for i in range(self.max_retries):

            try:

                if self.sleep:
                    time.sleep(self.sleep)

                r = self.s.get(url, params=params, timeout=self.timeout)

                if r.status_code in (429, 500, 502, 503, 504):
                    backoff = min(60, 2 ** i) + random.random()
                    time.sleep(backoff)
                    continue

                r.raise_for_status()
                return r.json()

            except requests.exceptions.RequestException as e:
                last_err = e
                backoff = min(60, 2 ** i) + random.random()
                time.sleep(backoff)

        raise RuntimeError(f"GET failed after retries: {url}; err={last_err}")
