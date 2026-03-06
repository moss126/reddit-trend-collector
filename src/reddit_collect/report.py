def _examples(examples):
    out = []
    for e in examples[:3]:
        link = f"https://www.reddit.com{e.get('permalink','')}" if e.get("permalink") else ""
        out.append(
            f"- [{e.get('subreddit','')}] {e.get('title','')} "
            f"(score={e.get('score',0)}, comments={e.get('comments',0)})"
        )
        if link:
            out.append(f"  {link}")
    return "\n".join(out)

def build_report(rows):
    out = []
    out.append("# Reddit 产品机会报告\n")

    out.append("## Reddit 产品机会 Top20\n")
    for i, r in enumerate(rows[:20], 1):
        out.append(
            f"{i}. **{r['phrase']}** | reddit_opportunity={r['reddit_opportunity']} | "
            f"mentions={r['mentions']} | comments={r['comments']} | "
            f"showcase={r['showcase']} | problem={r['problem']} | question={r['question']}"
        )
        out.append(_examples(r["examples"]))
        out.append("")

    validated = [r for r in rows if r.get("validation_status") == "validated"]
    if validated:
        out.append("## Amazon 验证 Top20\n")
        for i, r in enumerate(validated[:20], 1):
            out.append(
                f"{i}. **{r['phrase']}** | total_score={r['total_score']} | amazon_score={r['amazon_score']} | "
                f"results={r.get('amazon_results')} | rating={r.get('avg_rating')} | "
                f"price={r.get('avg_price')} | reviews={r.get('avg_reviews')} | fit={r.get('fit')}"
            )
            if r.get("notes"):
                out.append(f"- notes: {r['notes']}")
            out.append("")

    out.append("## 综合机会 Top20\n")
    for i, r in enumerate(rows[:20], 1):
        out.append(
            f"{i}. **{r['phrase']}** | total_score={r['total_score']} | "
            f"reddit={r['reddit_opportunity']} | amazon={r.get('amazon_score')}"
        )
        out.append("")

    pending = [r for r in rows if r.get("validation_status") != "validated"][:20]
    if pending:
        out.append("## 待验证候选 Top20\n")
        for i, r in enumerate(pending, 1):
            out.append(
                f"{i}. **{r['phrase']}** | reddit_opportunity={r['reddit_opportunity']} | "
                f"subreddits={', '.join(r.get('subreddits', [])[:4])}"
            )
        out.append("")

    return "\n".join(out)
