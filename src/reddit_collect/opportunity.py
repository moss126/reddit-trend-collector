import re
import math
from collections import defaultdict

STRUCTURE = {
    "magnetic","modular","stackable","foldable","wall","mounted","holder","stand",
    "organizer","tray","rack","case","mount","clip","hook","display","storage"
}

PRODUCT = {
    "holder","organizer","tray","tower","rack","box","case","adapter","mount","stand",
    "storage","display","dryer","spool","dice","token","bookend","bookends","base",
    "terrain","tile","tiles","printer","filament"
}

STOP = {
    "amazon","fba","seller","central","ppc","acos","roas","seo","listing","rank","tracking",
    "stock","stocks","nasdaq","nyse","earnings","vat","tax","shipment","warehouse",
    "the","and","for","with","that","this","from","what","when","where","which","your",
    "made","make","making","just","need","looking","anyone","know","help","best","better",
    "first","second","third","more","most","some","any","much","amp","why","how"
}

SHOWCASE = re.compile(r"(i made|i designed|i printed|i created|i built)", re.I)
PROBLEM = re.compile(r"(need|looking for|any recommendation|anyone know|storage solution|worth it)", re.I)
QUESTION = re.compile(r"\?$")
TOKEN = re.compile(r"[a-z0-9]+")

def tokenize(text):
    toks = TOKEN.findall((text or "").lower())
    return [t for t in toks if len(t) >= 3 and t not in STOP]

def classify(title):
    title = title or ""
    if SHOWCASE.search(title):
        return "showcase"
    if PROBLEM.search(title):
        return "problem"
    if QUESTION.search(title.strip()):
        return "question"
    return "other"

def phrase_candidates(tokens):
    for n in (2, 3, 4):
        for i in range(len(tokens) - n + 1):
            yield " ".join(tokens[i:i+n])

def score_post(data):
    s = float(data.get("score", 0) or 0)
    c = float(data.get("num_comments", 0) or 0)
    return s + 2 * math.log1p(c)

def extract(posts):
    stats = defaultdict(lambda: {
        "mentions": 0,
        "comments": 0,
        "reddit_score_sum": 0.0,
        "showcase": 0,
        "problem": 0,
        "question": 0,
        "examples": [],
        "communities": set(),
        "subreddits": set(),
    })

    for p in posts:
        d = p["data"]
        title = d.get("title", "")
        tokens = tokenize(title)
        kind = classify(title)
        seen = set()

        for ph in phrase_candidates(tokens):
            words = set(ph.split())
            if not (words & STRUCTURE or words & PRODUCT):
                continue
            if ph in seen:
                continue
            seen.add(ph)

            st = stats[ph]
            st["mentions"] += 1
            st["comments"] += int(d.get("num_comments", 0) or 0)
            st["reddit_score_sum"] += score_post(d)
            st["communities"].add(d.get("_community", "unknown"))
            st["subreddits"].add(d.get("subreddit", ""))

            if kind == "showcase":
                st["showcase"] += 1
            elif kind == "problem":
                st["problem"] += 1
            elif kind == "question":
                st["question"] += 1

            if len(st["examples"]) < 3:
                st["examples"].append({
                    "title": title,
                    "subreddit": d.get("subreddit", ""),
                    "comments": d.get("num_comments", 0),
                    "score": d.get("score", 0),
                    "permalink": d.get("permalink", "")
                })

    rows = []
    for phrase, st in stats.items():
        reddit_opportunity = (
            st["mentions"] * 2
            + st["comments"]
            + st["showcase"] * 5
            + st["problem"] * 3
            - st["question"] * 1
        )
        rows.append({
            "phrase": phrase,
            "mentions": st["mentions"],
            "comments": st["comments"],
            "showcase": st["showcase"],
            "problem": st["problem"],
            "question": st["question"],
            "reddit_opportunity": round(reddit_opportunity, 2),
            "reddit_score_avg": round(st["reddit_score_sum"] / max(st["mentions"], 1), 2),
            "communities": sorted(list(st["communities"])),
            "subreddits": sorted([x for x in st["subreddits"] if x]),
            "examples": st["examples"],
        })

    rows.sort(key=lambda x: x["reddit_opportunity"], reverse=True)
    return rows
