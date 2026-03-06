# Reddit Trend Collector V1.4.3-fix

Patch version fixing timeout crashes.

Changes:
- Retry mechanism with exponential backoff
- Skip failed subreddit requests
- Configurable timeout and retry parameters

Run:

python src/main.py --config config.yaml --outdir data
