from urllib.parse import quote_plus

def build_report(rows):

    out=["# Reddit Product Opportunities\n"]

    for i,r in enumerate(rows[:20],1):

        q=quote_plus(r["phrase"])

        out.append(f"{i}. {r['phrase']} (mentions={r['mentions']} comments={r['comments']})")
        out.append(f"Reddit https://www.reddit.com/search/?q={q}")
        out.append(f"Amazon https://www.amazon.com/s?k={q}")
        out.append(f"Google https://www.google.com/search?q={q}")

        for e in r["examples"]:
            link="https://reddit.com"+e["permalink"]
            out.append(f"- {e['title']}")
            out.append(f"  {link}")

        out.append("")

    return "\n".join(out)
