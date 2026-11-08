"""Ledger for the daily-jobs skill (research only, the user applies by hand).

Picks live in apply/<me>/daily/picks.csv. When the user says they applied, the pick is also written to the
shared applied ledger of its source through apply.py, so every job-apply skill blocks it for 6 months.

Usage (from the repo root):
  python .claude/skills/daily-jobs/scripts/daily.py status
      Picks still waiting for an answer, and the last 7 days' numbers (picked / applied / skipped, by source).
  python .claude/skills/daily-jobs/scripts/daily.py seen <job_url> ["<company>"] ["<title>"]
      SKIP if this job was picked or skipped in the last 60 days (same URL, or same company + title).
  python .claude/skills/daily-jobs/scripts/daily.py add '<json>'
      Record one pick. Keys: rank, company, title, source, job_url, apply_url, company_country,
      pay_range, pay_usd_month, solid, folder. Date defaults to today.
  python .claude/skills/daily-jobs/scripts/daily.py applied <YYYY-MM-DD|latest> <rank> [<rank>...]
      Mark picks applied and record them in the shared ledger (apply.py --source <source> add).
  python .claude/skills/daily-jobs/scripts/daily.py skip <YYYY-MM-DD|latest> <rank> ["<reason>"]
      Mark a pick skipped (not shown again for 60 days).
"""
import csv
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "job-apply-shared" / "scripts"))
import me  # noqa: E402

FIELDS = ["date", "rank", "company", "title", "source", "job_url", "apply_url", "company_country",
          "pay_range", "pay_usd_month", "solid", "folder", "status", "note"]
SOURCES = {"linkedin", "post", "twitter", "hn", "himalayas", "wellfound", "yc", "others", "direct"}
SEEN_DAYS = 60
APPLY = Path(__file__).resolve().parents[2] / "job-apply-shared" / "scripts" / "apply.py"


def ledger():
    return me.out_dir("apply") / "daily" / "picks.csv"


def rows():
    p = ledger()
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(data):
    p = ledger()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(data)


def norm_url(u):
    # Keep params that identify the job (HN item?id=...), drop tracking ones.
    return me.norm_url(u)


def key(company, title):
    clean = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
    return f"{clean(company)}|{clean(title)}"


def pick_date(arg, data):
    if arg == "latest":
        if not data:
            sys.exit("no picks yet")
        return max(r["date"] for r in data)
    datetime.strptime(arg, "%Y-%m-%d")
    return arg


def find(data, date, rank):
    hits = [r for r in data if r["date"] == date and str(r["rank"]) == str(rank)]
    if not hits:
        sys.exit(f"no pick #{rank} on {date}")
    return hits[0]


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd, data = args[0], rows()

    if cmd == "status":
        waiting = [r for r in data if r["status"] == "picked"]
        print(f"waiting for an answer: {len(waiting)}")
        for r in waiting:
            print(f"  {r['date']} #{r['rank']} {r['company']} - {r['title']} ({r['source']})")
        since = f"{me.today() - timedelta(days=7):%Y-%m-%d}"
        week = [r for r in data if r["date"] > since]
        print(f"last 7 days: {len(week)} jobs (" + ", ".join(
            f"{n} {s}" for s, n in Counter(r["status"] for r in week).items()) + ")")
        applied = Counter(r["source"] for r in week if r["status"] == "applied")
        if applied:
            print("applied by source: " + ", ".join(f"{s} {n}" for s, n in applied.most_common()))

    elif cmd == "seen":
        url, company, title = args[1], (args[2] if len(args) > 2 else ""), (args[3] if len(args) > 3 else "")
        cutoff = f"{me.today() - timedelta(days=SEEN_DAYS):%Y-%m-%d}"
        k = key(company, title) if company and title else None
        for r in data:
            if r["date"] > cutoff and (norm_url(r["job_url"]) == norm_url(url)
                                       or (k and key(r["company"], r["title"]) == k)):
                sys.exit(f"SKIP: {r['status']} on {r['date']} (#{r['rank']} {r['company']} - {r['title']})")
        print("new")

    elif cmd == "add":
        row = json.loads(args[1])
        if row.get("source") not in SOURCES:
            sys.exit(f"source must be one of {sorted(SOURCES)}")
        for need in ("rank", "company", "title", "job_url", "company_country", "folder"):
            if not str(row.get(need, "")).strip():
                sys.exit(f"missing {need}")
        row.setdefault("date", f"{me.today():%Y-%m-%d}")
        row.setdefault("status", "picked")
        if any(r["date"] == row["date"] and str(r["rank"]) == str(row["rank"]) for r in data):
            sys.exit(f"pick #{row['rank']} on {row['date']} already exists")
        save(data + [row])
        print(f"picked #{row['rank']}: {row['company']} - {row['title']}")

    elif cmd in ("applied", "skip"):
        if len(args) < 3:
            sys.exit(__doc__)
        date = pick_date(args[1], data)
        ranks = args[2:] if cmd == "applied" else [args[2]]
        note = args[3] if cmd == "skip" and len(args) > 3 else ""
        for rank in ranks:
            r = find(data, date, rank)
            if cmd == "applied":
                ledger_row = {"date": f"{me.today():%Y-%m-%d}", "company": r["company"], "title": r["title"],
                              "company_country": r["company_country"], "pay_range": r["pay_range"],
                              "pay_usd_month": r["pay_usd_month"], "linkedin_url": r["job_url"],
                              "apply_url": r["apply_url"], "method": "manual (daily-jobs)",
                              "folder": r["folder"], "status": "applied"}
                res = subprocess.run([sys.executable, str(APPLY), "--source", r["source"], "add",
                                      json.dumps(ledger_row)], capture_output=True, text=True)
                print((res.stdout or res.stderr).strip())
                if res.returncode != 0 and "already applied" not in (res.stdout + res.stderr):
                    sys.exit(f"not recorded in the shared ledger: #{rank} {r['company']}")
                r["status"] = "applied"
            else:
                r["status"], r["note"] = "skipped", note
            print(f"{r['status']}: #{rank} {r['company']} - {r['title']}")
        save(data)

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
