import argparse
import json
from pathlib import Path
from datetime import datetime

from reddit_collect import load_config
from reddit_collect.http import RedditHttp
from reddit_collect.collectors import collect_hot, collect_rising
from reddit_collect.opportunity import extract
from reddit_collect.amazon_validation import ensure_template, load_validation, merge_validation
from reddit_collect.report import build_report

def _tag_posts(raw_posts, community):
    tagged = []
    for p in raw_posts:
        if "data" in p:
            p["data"]["_community"] = community
        tagged.append(p)
    return tagged

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--outdir", default="data")
    args = ap.parse_args()

    cfg = load_config(args.config)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    http = RedditHttp(
        cfg["user_agent"],
        sleep=cfg.get("sleep_seconds", 1),
        timeout=cfg.get("timeout_seconds", 20),
    )

    posts = []
    per_limit = int((cfg.get("limits") or {}).get("per_subreddit", 100))

    for comm, data in (cfg.get("communities") or {}).items():
        for sr in data.get("subreddits", []):
            if (cfg.get("collect") or {}).get("hot", True):
                posts += _tag_posts(collect_hot(http, sr, per_limit), comm)
            if (cfg.get("collect") or {}).get("rising", True):
                posts += _tag_posts(collect_rising(http, sr, per_limit), comm)

    opportunities = extract(posts)

    template_path = outdir / "validation_template.csv"
    ensure_template(template_path, opportunities, top_n=60)

    validation = load_validation(template_path)
    merged = merge_validation(opportunities, validation)

    today = datetime.utcnow().date().isoformat()

    report = build_report(merged)
    report_path = outdir / f"report_{today}.md"
    report_path.write_text(report, encoding="utf-8")

    json_path = outdir / f"opportunities_{today}.json"
    json_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    print("posts:", len(posts))
    print("report:", report_path)
    print("json:", json_path)
    print("validation_template:", template_path)

if __name__ == "__main__":
    main()
