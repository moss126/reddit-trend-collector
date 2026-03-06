import re
import math
from collections import defaultdict
from pathlib import Path
import json

PHRASE_BLACKLIST = {
    "amazon", "fba", "amazon fba", "seller central", "amazon seller",
    "ppc", "acos", "roas", "seo", "listing", "rank tracking",
    "stock", "stocks", "nasdaq", "nyse", "earnings",
    "llc", "vat", "tax", "customs", "shipment", "freight", "warehouse",
}

TOKEN_BLACKLIST = {
    "amazon","fba","seller","central","ppc","acos","roas","seo","listing","rank","tracking",
    "stock","stocks","nasdaq","nyse","earnings","llc","vat","tax","customs","shipment","freight","warehouse",
}

STRUCTURE_SIGNAL_WORDS = {
    "magnetic","modular","stackable","foldable","collapsible","adjustable",
    "wall","mounted","mount","bracket","clip","hook",
    "snap","snapfit","snap-fit","pressfit","press-fit",
    "quick","release","quickrelease","quick-release",
    "hinged","hinge",
    "sliding","slide","rail",
    "rotating","swivel","pivot",
    "locking","lock","latch",
    "spring","springloaded","spring-loaded",
    "telescopic","extendable",
    "detachable","removable",
    "universal","compatible",
    "organizer","storage","holder","stand","display",
    "tray","rack","case",
}

PRODUCT_SIGNAL_WORDS = {
    "adapter","adaptor","mount","bracket","holder","stand","case","cover","cable","cord","wire",
    "battery","charger","switch","sensor","filter","nozzle","hose","pump","motor",
    "kit","tool","tools","gear","part","parts","replacement","refill","cartridge",
    "blade","bit","drill","screw","bolt","nut","clip","hook","magnet",
    "connector","usb","typec","type-c","hdmi","sd","dock","hub","controller",
    "filament","pla","petg","abs","resin","printer","printing","extruder","nozzle","bed","spool",
    "dryer","drybox","enclosure","supports","layer","calibration","bambu","prusa","ender",
    "dice","tower","tray","token","card","deck","sleeve","organizer","insert","storage",
    "vacuum","mop","brush","cleaner","robot",
    "bookend","bookends","book","stand","holder",
}

STOPWORDS = {
    "the","a","an","and","or","but","if","then","so","to","of","in","on","for","with","at","by",
    "is","are","was","were","be","been","being","it","this","that","these","those","i","you","we","they",
    "my","your","our","their","me","him","her","them","as","from","up","down","out","about",
    "help","anyone","question","questions","advice","tips","idea","ideas","looking","need","needs",
    "best","better","worst","new","update","how","what","why","where","when",
    "made","make","making","printed","print","just","first","second","third",
    "can","could","should","would","may","might","will","want","wants","wanted",
    "some","any","many","much","more","most","less","least",
    "there","here","today","yesterday","tomorrow","now","then",
    "please","thanks","thank","thx",
    "vs","versus",
    "amp",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")
MIN_NGRAM = 2
MAX_NGRAM = 3
REQUIRE_SIGNAL = True

def tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = TOKEN_RE.findall(text)
    cleaned = []
    for t in tokens:
        if t == "amp":
            continue
        if len(t) < 3:
            continue
        if t in STOPWORDS:
            continue
        cleaned.append(t)
    return cleaned

def ngrams(tokens: list[str], n: int):
    for i in range(len(tokens) - n + 1):
        yield " ".join(tokens[i:i + n])

def _contains_blacklisted_token(phrase: str) -> bool:
    for t in phrase.split():
        if t in TOKEN_BLACKLIST:
            return True
    return False

def _signal_ok(phrase: str) -> bool:
    toks = phrase.split()
    has_product = any(t in PRODUCT_SIGNAL_WORDS for t in toks)
    has_structure = any(t in STRUCTURE_SIGNAL_WORDS for t in toks)
    return has_product or has_structure

def extract_phrases(title: str) -> list[str]:
    tokens = tokenize(title)
    phrases: list[str] = []
    for n in range(MIN_NGRAM, MAX_NGRAM + 1):
        for g in ngrams(tokens, n):
            if g.isdigit():
                continue
            if g in PHRASE_BLACKLIST:
                continue
            if _contains_blacklisted_token(g):
                continue
            if REQUIRE_SIGNAL and (not _signal_ok(g)):
                continue
            phrases.append(g)
    return phrases

def score_item(item: dict) -> float:
    score = float(item.get("score") or 0)
    comments = float(item.get("num_comments") or 0)
    return score + 2.0 * math.log1p(comments)

def build_phrase_stats(items: list[dict]) -> list[dict]:
    stats = defaultdict(lambda: {"mentions": 0, "score_sum": 0.0, "comments_sum": 0, "examples": []})

    for it in items:
        title = it.get("title") or ""
        s = score_item(it)
        phrases = extract_phrases(title)

        seen_in_post = set()
        for p in phrases:
            if p in seen_in_post:
                continue
            seen_in_post.add(p)

            st = stats[p]
            st["mentions"] += 1
            st["score_sum"] += s
            st["comments_sum"] += int(it.get("num_comments") or 0)

            if len(st["examples"]) < 3:
                st["examples"].append({
                    "title": title[:160],
                    "subreddit": it.get("subreddit"),
                    "permalink": it.get("permalink"),
                    "score": it.get("score"),
                    "num_comments": it.get("num_comments"),
                    "source": it.get("source"),
                })

    rows = []
    for phrase, st in stats.items():
        mentions = st["mentions"]
        avg_score = st["score_sum"] / mentions if mentions else 0.0
        rows.append({
            "phrase": phrase,
            "mentions": mentions,
            "avg_score": round(avg_score, 2),
            "comments_sum": st["comments_sum"],
            "examples": st["examples"],
        })

    rows.sort(key=lambda r: (r["mentions"], r["comments_sum"], r["avg_score"]), reverse=True)
    return rows

def load_prev_phrase_stats(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def save_phrase_stats(path: Path, data, top_n: int = 5000):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def diff_trends(curr_rows: list[dict], prev_map: dict):
    out = []
    for r in curr_rows:
        p = r["phrase"]
        prev = prev_map.get(p, {"mentions": 0, "comments_sum": 0, "avg_score": 0})
        delta_mentions = r["mentions"] - int(prev.get("mentions", 0))
        delta_comments = r["comments_sum"] - int(prev.get("comments_sum", 0))
        growth = 3 * delta_mentions + 1 * delta_comments
        out.append({**r, "delta_mentions": delta_mentions, "delta_comments": delta_comments, "growth": growth})

    rising = sorted(out, key=lambda x: (x["growth"], x["mentions"]), reverse=True)
    new = [x for x in out if int(prev_map.get(x["phrase"], {}).get("mentions", 0)) == 0]
    new.sort(key=lambda x: (x["mentions"], x["comments_sum"]), reverse=True)
    return new, rising
