"""Ledger for the product-outreach skill (see .claude/skills/product-outreach/SKILL.md).

One row per email draft (one person). Stored in product-outreach/<me>/contacted.csv, where <me> is the
person in `.me` (see .claude/skills/job-apply-shared/scripts/me.py).

  python .claude/skills/product-outreach/scripts/ledger.py check <company_site> ["<company>"]
      SKIP if this company was emailed in the last 180 days. Also prints (as info) whether the user applied
      to a job there or sent a LinkedIn request to someone there.
  python .claude/skills/product-outreach/scripts/ledger.py person <email> [<linkedin_url>]
      SKIP if this person was ever emailed before (any date, any status).
  python .claude/skills/product-outreach/scripts/ledger.py add '<json row>'
      Record one email (status email-draft, or "held" for a teammate whose email waits; see SKILL.md Step 6).
      company_country must be one of the person's target countries (profile.json). Include score and bug_area so stats can show what works.
  python .claude/skills/product-outreach/scripts/ledger.py set <email> <status>
      Statuses: email-draft held sent followed-up no-reply replied call interview offer withdrawn.
      sent and followed-up also stamp sent_date / followup_date (today).
  python .claude/skills/product-outreach/scripts/ledger.py drafts
      Rows still in email-draft status (check Gmail Sent for them).
  python .claude/skills/product-outreach/scripts/ledger.py due
      What needs doing: follow-ups (sent 5+ days ago), no-reply (followed up 7+ days ago),
      and held teammates whose company went quiet (their email can now be drafted).
  python .claude/skills/product-outreach/scripts/ledger.py stats
      Counts by status, and reply rate by score, bug_area and directory.
  python .claude/skills/product-outreach/scripts/ledger.py seen
      Every company domain already in the ledger (to skip while browsing directories).
"""
import csv
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "job-apply-shared" / "scripts"))
import me  # noqa: E402  the person in .me; same target-country list as the job-apply skills

LEDGER = me.out_dir("product-outreach") / "contacted.csv"
FIELDS = ["date", "product", "company", "company_site", "company_country", "person", "role", "email",
          "email_source", "linkedin_url", "directory", "subject", "folder", "status",
          "score", "bug_area", "sent_date", "followup_date"]
STATUSES = {"email-draft", "held", "sent", "followed-up", "no-reply", "replied", "call", "interview", "offer",
            "withdrawn"}
REPLIED = {"replied", "call", "interview", "offer"}
FOLLOWUP_AFTER, GIVE_UP_AFTER = 5, 7
COOLDOWN_DAYS = 180


def domain(url):
    d = re.sub(r"^https?://", "", (url or "").strip().lower()).split("/")[0]
    return d[4:] if d.startswith("www.") else d


def norm(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower().replace(" inc", "").replace(" ltd", ""))


def read(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(data):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(data)


def same_company(r, site, company):
    return (site and domain(r.get("company_site")) == domain(site)) or (company and norm(r.get("company")) == norm(company))


def main():
    if len(sys.argv) < 2 or (sys.argv[1] not in ("drafts", "seen", "due", "stats") and len(sys.argv) < 3):
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    data = read(LEDGER)
    today = me.today()

    if cmd == "check":
        site, company = args[0], (args[1] if len(args) > 1 else "")
        for r in data:
            if same_company(r, site, company) and r["status"] != "withdrawn":
                until = datetime.strptime(r["date"], "%Y-%m-%d").date() + timedelta(days=COOLDOWN_DAYS)
                if until > today:
                    sys.exit(f"SKIP until {until}: emailed {r['person']} ({r['role']}) on {r['date']} ({r['folder']})")
        for p in me.out_dir("apply").rglob("applied.csv"):
            for r in read(p):
                if company and norm(r.get("company")) == norm(company):
                    print(f"info: applied to '{r['title']}' there on {r['date']} ({r['folder']})")
        for p in (me.out_dir("linkedin") / "send-connection").rglob("*.csv"):
            for r in read(p):
                if same_company(r, site, company):
                    print(f"info: LinkedIn request to {r['name']} ({r['title']}) on {r['date_sent']}, {r['status']}")
        print("new: not emailed in the last 180 days")
    elif cmd == "person":
        email, li = args[0].strip().lower(), (args[1].rstrip("/").lower() if len(args) > 1 else "")
        for r in data:
            if r["email"].lower() == email or (li and r["linkedin_url"].rstrip("/").lower() == li):
                sys.exit(f"SKIP: already emailed on {r['date']} ({r['company']}, {r['status']})")
        print("new")
    elif cmd == "add":
        row = json.loads(args[0])
        if row.get("company_country", "").strip().lower() not in me.company_countries():
            sys.exit(f"blocked: company_country {row.get('company_country')!r} is not one of this person's "
                     f"target countries (profile.json company_countries, minus blocked_countries).")
        for r in data:
            if r["email"].lower() == row.get("email", "").strip().lower():
                sys.exit(f"blocked: {row['email']} already emailed on {r['date']}")
        row.setdefault("date", f"{today:%Y-%m-%d}")
        row.setdefault("status", "email-draft")
        if row["status"] not in STATUSES:
            sys.exit(f"status must be one of {sorted(STATUSES)}")
        write(data + [row])
        print(f"recorded ({len(data) + 1} total): {row['company']} - {row['person']} ({row['role']})")
    elif cmd == "set":
        email, status = args[0].strip().lower(), args[1]
        if status not in STATUSES:
            sys.exit(f"status must be one of {sorted(STATUSES)}")
        hits = [r for r in data if r["email"].lower() == email]
        if not hits:
            sys.exit(f"not found: {email}")
        for r in hits:
            r["status"] = status
            if status == "sent" and not r.get("sent_date"):
                r["sent_date"] = f"{today:%Y-%m-%d}"
            if status == "followed-up":
                r["followup_date"] = f"{today:%Y-%m-%d}"
        write(data)
        print(f"{status}: {hits[0]['company']} - {hits[0]['person']}")
    elif cmd == "drafts":
        print(json.dumps([r for r in data if r["status"] == "email-draft"], indent=2))
    elif cmd == "due":
        def age(d):
            return (today - datetime.strptime(d, "%Y-%m-%d").date()).days if d else -1
        follow = [r for r in data if r["status"] == "sent" and age(r.get("sent_date") or r["date"]) >= FOLLOWUP_AFTER]
        quiet = [r for r in data if r["status"] == "followed-up" and age(r.get("followup_date")) >= GIVE_UP_AFTER]
        nxt = []
        for r in data:
            if r["status"] != "held":
                continue
            mates = [m for m in data if same_company(m, r["company_site"], r["company"]) and m["status"] != "held"]
            if mates and all(m["status"] in ("no-reply", "withdrawn") for m in mates):
                nxt.append(r)
        out = {"follow_up": follow, "set_no_reply": quiet, "email_next_person": nxt}
        print(json.dumps({k: [f"{r['company']} - {r['person']} <{r['email']}>" for r in v] for k, v in out.items()},
                         indent=2))
    elif cmd == "stats":
        out_rows = [r for r in data if r["status"] not in ("email-draft", "held", "withdrawn")]
        by_status = {}
        for r in data:
            by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        print("status:", json.dumps(by_status))
        companies = {}
        for r in out_rows:
            c = companies.setdefault(domain(r["company_site"]), {"row": r, "replied": False})
            c["replied"] |= r["status"] in REPLIED
        print(f"companies emailed: {len(companies)}, replied: {sum(c['replied'] for c in companies.values())}")
        for col in ("score", "bug_area", "directory"):
            groups = {}
            for c in companies.values():
                g = groups.setdefault(c["row"].get(col) or "unknown", [0, 0])
                g[0] += 1
                g[1] += c["replied"]
            print(f"by {col}: " + ", ".join(f"{k} {v[1]}/{v[0]}" for k, v in sorted(groups.items())))
    elif cmd == "seen":
        print("\n".join(sorted({domain(r["company_site"]) for r in data})))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
