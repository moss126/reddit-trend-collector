import re
from collections import defaultdict

PRODUCT_END = {"holder","organizer","tray","rack","stand","mount","box","case","clip","scale"}
TOKEN = re.compile(r"[a-z0-9]+")

def tokenize(t):
    return TOKEN.findall((t or "").lower())

def extract(posts):

    stats = defaultdict(lambda: {"mentions":0,"comments":0,"examples":[]})

    for p in posts:
        d = p["data"]
        title = d.get("title","")
        toks = tokenize(title)

        phrase=None

        for n in (3,2):
            for i in range(len(toks)-n+1):
                cand=toks[i:i+n]
                if cand[-1] in PRODUCT_END:
                    phrase=" ".join(cand)
                    break
            if phrase:
                break

        if not phrase:
            continue

        st = stats[phrase]
        st["mentions"] += 1
        st["comments"] += d.get("num_comments",0)

        if len(st["examples"])<3:
            st["examples"].append({
                "title":title,
                "subreddit":d.get("subreddit"),
                "permalink":d.get("permalink")
            })

    rows=[
        {"phrase":k,"mentions":v["mentions"],"comments":v["comments"],"examples":v["examples"]}
        for k,v in stats.items()
    ]

    rows.sort(key=lambda x:(x["mentions"]+x["comments"]),reverse=True)

    return rows
