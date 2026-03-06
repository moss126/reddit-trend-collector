import csv
from pathlib import Path

HEADER = [
    "phrase",
    "amazon_results",
    "avg_rating",
    "avg_price",
    "avg_reviews",
    "fit",
    "notes",
]

def ensure_template(path: Path, opportunities: list, top_n: int = 50):
    if path.exists():
        return

    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for row in opportunities[:top_n]:
            w.writerow({
                "phrase": row["phrase"],
                "amazon_results": "",
                "avg_rating": "",
                "avg_price": "",
                "avg_reviews": "",
                "fit": "",
                "notes": "",
            })

def load_validation(path: Path):
    if not path.exists():
        return {}

    out = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            phrase = (row.get("phrase") or "").strip()
            if not phrase:
                continue
            out[phrase] = {
                "amazon_results": _to_float(row.get("amazon_results")),
                "avg_rating": _to_float(row.get("avg_rating")),
                "avg_price": _to_float(row.get("avg_price")),
                "avg_reviews": _to_float(row.get("avg_reviews")),
                "fit": _to_float(row.get("fit")),
                "notes": row.get("notes", "").strip(),
            }
    return out

def _to_float(v):
    if v is None or str(v).strip() == "":
        return None
    try:
        return float(v)
    except Exception:
        return None

def score_amazon(v: dict):
    results = v.get("amazon_results")
    rating = v.get("avg_rating")
    price = v.get("avg_price")
    reviews = v.get("avg_reviews")
    fit = v.get("fit")

    score = 0.0

    if results is not None:
        if results <= 200:
            score += 25
        elif results <= 500:
            score += 18
        elif results <= 1000:
            score += 10
        elif results <= 3000:
            score += 4
        else:
            score -= 5

    if rating is not None:
        if 3.8 <= rating <= 4.4:
            score += 12
        elif 4.4 < rating <= 4.7:
            score += 8
        elif rating < 3.5:
            score += 5
        else:
            score += 2

    if reviews is not None:
        if reviews <= 100:
            score += 18
        elif reviews <= 300:
            score += 12
        elif reviews <= 1000:
            score += 6
        else:
            score -= 4

    if price is not None:
        if 15 <= price <= 50:
            score += 10
        elif 10 <= price < 15:
            score += 6
        elif 50 < price <= 90:
            score += 5
        else:
            score += 1

    if fit is not None:
        score += fit * 2

    return round(score, 2)

def merge_validation(opportunities: list, validation: dict):
    merged = []
    for row in opportunities:
        v = validation.get(row["phrase"], {})
        amazon_score = score_amazon(v) if v else None

        total = row["reddit_opportunity"]
        if amazon_score is not None:
            total += amazon_score

        merged.append({
            **row,
            "amazon_results": v.get("amazon_results"),
            "avg_rating": v.get("avg_rating"),
            "avg_price": v.get("avg_price"),
            "avg_reviews": v.get("avg_reviews"),
            "fit": v.get("fit"),
            "notes": v.get("notes", ""),
            "amazon_score": amazon_score,
            "total_score": round(total, 2),
            "validation_status": "validated" if v else "pending",
        })

    merged.sort(key=lambda x: x["total_score"], reverse=True)
    return merged
