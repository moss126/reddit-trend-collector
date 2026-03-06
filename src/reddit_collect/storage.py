import json
from pathlib import Path
from typing import List, Dict, Any

def ensure_dirs(outdir: Path):
    (outdir / "raw").mkdir(parents=True, exist_ok=True)
    (outdir / "reports").mkdir(parents=True, exist_ok=True)

class StateStore:
    def __init__(self, path: Path, max_seen: int = 50000):
        self.path = path
        self.max_seen = max_seen
        self._seen = []
        self._seen_set = set()
        self._load()

    def _load(self):
        if not self.path.exists():
            self._seen = []
            self._seen_set = set()
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self._seen = list(data.get("seen_names", []))
        self._seen_set = set(self._seen)

    def seen(self, name: str) -> bool:
        return name in self._seen_set

    def add(self, name: str):
        if name in self._seen_set:
            return
        self._seen.append(name)
        self._seen_set.add(name)

        if len(self._seen) > self.max_seen:
            drop = len(self._seen) - self.max_seen
            for _ in range(drop):
                old = self._seen.pop(0)
                self._seen_set.discard(old)

    def save(self):
        self.path.write_text(
            json.dumps({"seen_names": self._seen}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

class JsonlStore:
    def __init__(self, raw_dir: Path):
        self.raw_dir = raw_dir

    def write_jsonl(self, items: List[Dict[str, Any]]):
        by_source = {}
        for it in items:
            by_source.setdefault(it["source"], []).append(it)

        for src, rows in by_source.items():
            p = self.raw_dir / f"{src}.jsonl"
            with p.open("a", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
