import argparse
import json
from pathlib import Path
from datetime import datetime
import yaml

from reddit_collect.http import RedditHttp
from reddit_collect.collectors import collect_hot, collect_rising
from reddit_collect.opportunity import extract
from reddit_collect.report import build_report


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--outdir", default="data")
    args = ap.parse_args()

    cfg = load_config(args.config)

    http = RedditHttp(
        cfg["user_agent"],
        sleep=cfg.get("sleep_seconds", 1),
        timeout=cfg.get("timeout_seconds", 20),
        max_retries=cfg.get("max_retries", 5),
    )

    posts = []
    limit = cfg["limits"]["per_subreddit"]

    for comm, data in cfg["communities"].items():
        for sr in data["subreddits"]:
            try:
                if cfg["collect"]["hot"]:
                    posts += collect_hot(http, sr, limit)

                if cfg["collect"]["rising"]:
                    posts += collect_rising(http, sr, limit)

            except Exception as e:
                print(f"[WARN] failed subreddit={sr}: {e}")
                continue

    rows = extract(posts)

    report = build_report(rows)

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    today = datetime.utcnow().date().isoformat()

    report_path = outdir / f"report_{today}.md"
    report_path.write_text(report, encoding="utf-8")

    json_path = outdir / f"opportunities_{today}.json"
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    print("posts:", len(posts))
    print("report:", report_path)
    print("json:", json_path)


if __name__ == "__main__":
    main()
