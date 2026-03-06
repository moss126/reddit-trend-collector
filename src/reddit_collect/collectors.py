BASE = "https://www.reddit.com"

def collect_hot(http, sub, limit=100):
    j = http.get(f"{BASE}/r/{sub}/hot.json", {"limit": limit})
    return j["data"]["children"]

def collect_rising(http, sub, limit=100):
    j = http.get(f"{BASE}/r/{sub}/rising.json", {"limit": limit})
    return j["data"]["children"]
