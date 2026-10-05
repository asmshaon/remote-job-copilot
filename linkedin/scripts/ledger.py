"""Connection ledger shared by the linkedin-company-outreach, linkedin-client-outreach,
linkedin-hiring-team-outreach and product-outreach skills.

Nothing here touches LinkedIn. Claude prepares the list, the user sends every request themselves,
and this script keeps the CSVs in order. Every folder below lives under linkedin/<me>/, where <me> is the
person in `.me` (see .claude/skills/job-apply-shared/scripts/me.py), so each person has their own ledgers.

Tracks and folders:
  company -> linkedin/<me>/send-connection/linkedin-connections-by-company-jobs/YYYY-MM-DD.csv
             linkedin/<me>/reject-connection/linkedin-connections-by-company-jobs/YYYY-MM-DD.csv
  client  -> linkedin/<me>/send-connection/linkedin-connection-by-client-projects/YYYY-MM-DD.csv
             linkedin/<me>/reject-connection/linkedin-connection-by-client-projects/YYYY-MM-DD.csv
  hiring  -> linkedin/<me>/send-connection/linkedin-connections-by-hiring-team/YYYY-MM-DD.csv
             linkedin/<me>/reject-connection/linkedin-connections-by-hiring-team/YYYY-MM-DD.csv
  product -> linkedin/<me>/send-connection/linkedin-connections-by-product-outreach/YYYY-MM-DD.csv
             linkedin/<me>/reject-connection/linkedin-connections-by-product-outreach/YYYY-MM-DD.csv
             (CEO/CTO/technical co-founders the user emailed through product outreach; a bonus
             track on top of the 12-a-day target, but inside the 90-in-7-days cap)

Follow-up messages (after someone accepts) go in one file per day and track, for the user to send that day:
  follow-up -> linkedin/<me>/follow-up/<same folder name as the track>/YYYY-MM-DD.csv
  columns: date, name, company, linkedin_url, message_type, message, chars, status, status_checked, log
  status: prepared (written, not sent yet) | sent | skipped

Row status in send files:
  prepared  listed by Claude, not yet confirmed as sent
  pending   the user sent it, shows under Sent invitations on LinkedIn
  accepted  now a 1st-degree connection
  not-sent  prepared but never sent
After acceptance, the conversation (the user sends every message themselves):
  messaged    the user sent a message (msg_count counts them, last_msg_date stamps it)
  replied     they answered (replied_date stamps it); the user's answer is due, then back to messaged
  call / interview / offer   how far it went (jobs: company and hiring tracks)
  call / proposal / won      how far it went (projects: client track)
  no-reply    no answer to message 1 and the follow-up; nothing more is sent
Rows that are not accepted within N days, or whose invitation disappeared without
being accepted, are moved from the send file to that day's reject file.
Anyone already in ANY send or reject file (any track, any status, any date) is never
listed again: `add` refuses them, matching on the profile URL or on name + company.
`add` also requires a `country` from the person's outreach countries (profile.json outreach_countries,
minus blocked_countries) and refuses anyone else.

Commands (run from the repo root, <track> is company, client, hiring or product):
  python linkedin/scripts/ledger.py <track> seen                 every URL in any send or reject file (skip these)
  python linkedin/scripts/ledger.py <track> check <url> [name] [company]   is this person already in any file? (run before research)
  python linkedin/scripts/ledger.py <track> lint '<note>'        check a note reads human (no AI tells); run before add
  python linkedin/scripts/ledger.py <track> today                today's send file and its row count
  python linkedin/scripts/ledger.py <track> add '<json row>'     append one prepared row to today's send file
  python linkedin/scripts/ledger.py <track> open                 prepared + pending rows in all send files (JSON)
  python linkedin/scripts/ledger.py <track> set <url> <status>   pending | accepted | not-sent | messaged | replied | call | interview | offer | proposal | won | no-reply
  python linkedin/scripts/ledger.py <track> convo                messages due after acceptance: message 1, follow-up, answers, no-reply (JSON)
  python linkedin/scripts/ledger.py <track> followup add '<json>' add one message to today's follow-up file (name, linkedin_url, message_type, message, log)
  python linkedin/scripts/ledger.py <track> followup today       today's follow-up file and its rows
  python linkedin/scripts/ledger.py <track> followup open        prepared messages not yet confirmed sent (any day)
  python linkedin/scripts/ledger.py <track> followup sent <url>  the user sent it: marks it sent and sets the person to messaged
  python linkedin/scripts/ledger.py <track> followup skip <url>  the user won't send it
  python linkedin/scripts/ledger.py <track> company <site> [company]   SKIP if any track touched this company in the last 30 days; info if they applied there
  python linkedin/scripts/ledger.py <track> due [--days 7]       pending rows sent N+ days ago (JSON)
  python linkedin/scripts/ledger.py <track> reject <url> <reason>  move row to today's reject file
  python linkedin/scripts/ledger.py <track> stats                counts by status, accepted of sent, still pending, replies and calls
  python linkedin/scripts/ledger.py <track> dupes              same person listed more than once across all tracks (JSON)
  python linkedin/scripts/ledger.py <track> drop <url>           remove a still-prepared row from this track (never sent)
  python linkedin/scripts/ledger.py <track> rejected             every URL in any reject file (never contact again)
"""
import csv
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

TRACKS = {
    "company": "linkedin-connections-by-company-jobs",
    "client": "linkedin-connection-by-client-projects",
    "hiring": "linkedin-connections-by-hiring-team",
    "product": "linkedin-connections-by-product-outreach",
}
FIELDS = [
    "date_sent", "name", "title", "company", "company_site", "country", "linkedin_url",
    "domain_match", "why_target", "source", "note", "status", "status_checked",
    "accepted_date", "last_msg_date", "msg_count", "replied_date",
]
REJECT_FIELDS = FIELDS + ["reject_reason"]
FU_FIELDS = ["date", "name", "company", "linkedin_url", "message_type", "message", "chars", "status", "status_checked", "log"]
FU_TYPES = {"message-1", "follow-up", "answer", "call-offer", "role", "proposal", "check-in", "thank-you"}
# The word, phrase, character and sentence-length checks are shared with every other message
# (job-apply-shared/scripts/apply.py, see job-apply-shared/HUMAN-WRITING.md). Notes add the 300-char and no-link rules.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/job-apply-shared/scripts"))
from apply import style_problems  # noqa: E402
import me  # noqa: E402  the person in .me: their folders, countries and time zone

ROOT = me.out_dir("linkedin")  # linkedin/<me>/


def allowed_countries():
    """Only people (and companies) in the person's outreach countries are ever listed (profile.json)."""
    return me.outreach_countries()


def lint_note(note: str):
    """Problems that make a note read AI-written or break LinkedIn's limit. Empty list = OK."""
    if not note.strip():
        return ["note is empty"]
    problems = []
    if len(note) > 300:
        problems.append(f"{len(note)} chars, max 300")
    problems += style_problems(note)
    if re.search(r"https?://|www\.", note.lower()):
        problems.append("link")
    return problems


STATUSES = {"pending", "accepted", "not-sent", "messaged", "replied", "call", "interview", "offer", "proposal", "won", "no-reply"}
CONNECTED = {"accepted", "messaged", "replied", "call", "interview", "offer", "proposal", "won", "no-reply"}
MSG1_AFTER, FOLLOWUP_AFTER, GIVE_UP_AFTER, CHECK_IN_AFTER = 1, 7, 14, 30  # days: accept -> msg 1 -> follow-up -> stop; quiet after talking -> check-in
COMPANY_COOLDOWN = 30
DAY_FILE = re.compile(r"^\d{4}-\d{2}-\d{2}\.csv$")
def today() -> date:
    return me.today()


def norm(url: str) -> str:
    url = url.strip().split("?")[0].split("#")[0].rstrip("/").lower()
    return re.sub(r"^https?://([a-z]{2,3}\.)?linkedin\.com", "https://www.linkedin.com", url)


def send_dir(track):
    return ROOT / "send-connection" / TRACKS[track]


def followup_dir(track):
    return ROOT / "follow-up" / TRACKS[track]


def followup_rows():
    """(path, rows) for every follow-up file of every track."""
    for track in TRACKS:
        for p in day_files(followup_dir(track)):
            yield track, p, read(p)


def reject_dir(track):
    return ROOT / "reject-connection" / TRACKS[track]


def day_files(folder: Path):
    return sorted(p for p in folder.glob("*.csv") if DAY_FILE.match(p.name))


def read(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path: Path, rows, fields=FIELDS):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def all_rows():
    """Every row in every send and reject file of all tracks, with where it lives."""
    for track in TRACKS:
        for kind, folder in (("send", send_dir(track)), ("reject", reject_dir(track))):
            for p in day_files(folder):
                for r in read(p):
                    yield {**r, "_where": f"{kind}/{TRACKS[track]}/{p.name}"}


def person_key(name, company):
    clean = lambda s: re.sub(r"[^a-z0-9]", "", re.sub(r"\(.*?\)", "", (s or "").lower()))
    return f"{clean(name)}|{clean(company)}" if name and company else None


def existing(url, name=None, company=None):
    """The first row already on file for this person (same URL, or same name + company), else None."""
    url, key = norm(url), person_key(name, company)
    for r in all_rows():
        if norm(r["linkedin_url"]) == url or (key and person_key(r["name"], r["company"]) == key):
            return r
    return None


def seen_urls():
    """Every URL in any send or reject file of any track, whatever its status."""
    return {norm(r["linkedin_url"]) for r in all_rows()}


def rejected_urls():
    """Everyone ever moved to a reject file, in any track. They are never contacted again."""
    return {
        norm(r["linkedin_url"])
        for track in TRACKS
        for p in day_files(reject_dir(track))
        for r in read(p)
    }


def domain(url):
    d = re.sub(r"^https?://", "", (url or "").strip().lower()).split("/")[0]
    return d[4:] if d.startswith("www.") else d


def company_key(name):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\(.*?\)", "", (name or "").lower()))


def days_since(d):
    return (today() - date.fromisoformat(d)).days if d else None


def find(track, url):
    target = norm(url)
    for path in day_files(send_dir(track)):
        rows = read(path)
        for i, row in enumerate(rows):
            if norm(row["linkedin_url"]) == target:
                return path, rows, i
    sys.exit(f"not found in any {track} send file: {url}")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in TRACKS:
        sys.exit(__doc__)
    track, cmd, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    stamp = f"{today():%Y-%m-%d}"

    if cmd == "seen":
        print("\n".join(sorted(seen_urls())))

    elif cmd == "lint":
        problems = lint_note(args[0] if args else "")
        if problems:
            sys.exit("REWRITE: " + "; ".join(problems))
        print(f"ok ({len(args[0])} chars)")

    elif cmd == "check":
        found = existing(args[0], *(args[1:3]))
        if found:
            sys.exit(f"SKIP, already in {found['_where']} ({found['status']}): {found['name']} - {found['company']}")
        print("new: not in any send or reject file")

    elif cmd == "today":
        path = send_dir(track) / f"{stamp}.csv"
        print(f"{path} {len(read(path))}")

    elif cmd == "add":
        row = json.loads(args[0])
        row["linkedin_url"] = norm(row["linkedin_url"])
        country = row.get("country", "").strip().lower()
        if country not in allowed_countries():
            sys.exit(f"blocked, country {row.get('country')!r} is not one of this person's outreach countries "
                     f"(profile.json outreach_countries): {row['linkedin_url']}")
        if row["linkedin_url"] in rejected_urls():
            sys.exit(f"blocked, rejected earlier (never re-send): {row['linkedin_url']}")
        problems = lint_note(row.get("note", ""))
        if problems:
            sys.exit("note rejected, rewrite it in plain human words: " + "; ".join(problems))
        found = existing(row["linkedin_url"], row.get("name"), row.get("company"))
        if found:
            sys.exit(f"duplicate, already in {found['_where']} ({found['status']}): {found['name']} - {found['company']}")
        row.setdefault("date_sent", stamp)
        row.setdefault("status", "prepared")
        row.setdefault("status_checked", stamp)
        path = send_dir(track) / f"{stamp}.csv"
        rows = read(path)
        rows.append(row)
        write(path, rows)
        print(f"added ({len(rows)} today): {row['name']} - {row['company']}")

    elif cmd == "open":
        rows = [
            {**r, "file": str(p)}
            for p in day_files(send_dir(track))
            for r in read(p)
            if r["status"] in ("prepared", "pending")
        ]
        print(json.dumps(rows, indent=2, ensure_ascii=False))

    elif cmd == "set":
        url, status = args[0], args[1]
        if status not in STATUSES:
            sys.exit(f"status must be one of {sorted(STATUSES)}")
        path, rows, i = find(track, url)
        rows[i]["status"] = status
        rows[i]["status_checked"] = stamp
        if status == "accepted" and not rows[i].get("accepted_date"):
            rows[i]["accepted_date"] = stamp
        if status == "replied":
            rows[i]["replied_date"] = stamp
        if status == "messaged":
            rows[i]["last_msg_date"] = stamp
            rows[i]["msg_count"] = str(int(rows[i].get("msg_count") or 0) + 1)
        write(path, rows)
        print(f"{status}: {rows[i]['name']} ({path.name})")

    elif cmd == "due":
        days = int(args[args.index("--days") + 1]) if "--days" in args else 7
        cutoff = today() - timedelta(days=days)
        due = [
            {**r, "file": str(p)}
            for p in day_files(send_dir(track))
            for r in read(p)
            if r["status"] == "pending" and date.fromisoformat(r["date_sent"]) <= cutoff
        ]
        print(json.dumps(due, indent=2, ensure_ascii=False))

    elif cmd == "reject":
        url, reason = args[0], " ".join(args[1:]) or "no response in 7 days"
        path, rows, i = find(track, url)
        row = rows.pop(i)
        write(path, rows)
        row["status"] = "rejected"
        row["status_checked"] = stamp
        row["reject_reason"] = reason
        out = reject_dir(track) / f"{stamp}.csv"
        log = read(out)
        log.append(row)
        write(out, log, REJECT_FIELDS)
        print(f"rejected -> {out}: {row['name']} - {row['company']} ({reason})")

    elif cmd == "dupes":
        # Same person listed more than once across ALL tracks (URL or name + company).
        # Used by the outreach orchestrator after agents ran in parallel.
        groups = {}
        for r in all_rows():
            for k in {norm(r["linkedin_url"]), person_key(r["name"], r["company"])} - {None}:
                groups.setdefault(k, []).append(r)
        seen, out = set(), []
        for k, rs in groups.items():
            ids = tuple(sorted(r["_where"] + r["linkedin_url"] for r in rs))
            if len(rs) > 1 and ids not in seen:
                seen.add(ids)
                out.append([{"name": r["name"], "company": r["company"], "status": r.get("status"),
                             "linkedin_url": r["linkedin_url"], "where": r["_where"]} for r in rs])
        print(json.dumps(out, indent=2, ensure_ascii=False))

    elif cmd == "drop":
        # Remove a row that is still `prepared` (never sent) from this track's send files.
        path, rows, i = find(track, args[0])
        if rows[i]["status"] != "prepared":
            sys.exit(f"refused: only prepared rows can be dropped (this one is {rows[i]['status']})")
        row = rows.pop(i)
        write(path, rows)
        print(f"dropped from {path.name}: {row['name']} - {row['company']}")

    elif cmd == "convo":
        due = {"send_message_1": [], "send_follow_up": [], "answer_reply": [], "check_in": [], "set_no_reply": [],
               "waiting_to_send": []}
        waiting = {norm(f["linkedin_url"]): f for _, fp, rows in followup_rows() if _ == track for f in rows
                   if f["status"] == "prepared"}
        for p in day_files(send_dir(track)):
            for r in read(p):
                if norm(r["linkedin_url"]) in waiting:
                    f = waiting[norm(r["linkedin_url"])]
                    due["waiting_to_send"].append({"name": r["name"], "company": r["company"],
                                                   "message_type": f["message_type"], "written": f["date"]})
                    continue
                n, s_ = int(r.get("msg_count") or 0), r["status"]
                who = {"name": r["name"], "company": r["company"], "linkedin_url": r["linkedin_url"],
                       "why_target": r["why_target"], "file": str(p)}
                if s_ == "accepted" and n == 0 and (days_since(r.get("accepted_date") or r["status_checked"]) or 0) >= MSG1_AFTER:
                    due["send_message_1"].append(who)
                elif s_ == "messaged" and r.get("replied_date"):
                    if (days_since(r.get("last_msg_date")) or 0) >= CHECK_IN_AFTER:
                        due["check_in"].append(who)
                elif s_ == "messaged" and n == 1 and (days_since(r.get("last_msg_date")) or 0) >= FOLLOWUP_AFTER:
                    due["send_follow_up"].append(who)
                elif s_ == "messaged" and n >= 2 and (days_since(r.get("last_msg_date")) or 0) >= GIVE_UP_AFTER:
                    due["set_no_reply"].append(who)
                elif s_ == "replied":
                    due["answer_reply"].append(who)
        print(json.dumps(due, indent=2, ensure_ascii=False))

    elif cmd == "followup":
        sub, rest = (args[0] if args else ""), args[1:]
        if sub == "add":
            row = json.loads(rest[0])
            row["linkedin_url"] = norm(row["linkedin_url"])
            if row.get("message_type") not in FU_TYPES:
                sys.exit(f"message_type must be one of {sorted(FU_TYPES)}")
            msg = row.get("message", "").strip()
            problems = style_problems(msg) + ([f"{len(msg)} chars, keep it under 600"] if len(msg) > 600 else [])
            if not msg or problems:
                sys.exit("message rejected, rewrite it in plain human words: " + ("; ".join(problems) or "empty"))
            path, rows, i = find(track, row["linkedin_url"])
            row.setdefault("name", rows[i]["name"])
            row.setdefault("company", rows[i]["company"])
            out = followup_dir(track) / f"{stamp}.csv"
            log = read(out)
            if any(norm(r["linkedin_url"]) == row["linkedin_url"] for r in log):
                sys.exit(f"already in today's follow-up file: {row['name']}")
            row.update(date=stamp, chars=str(len(msg)), status="prepared", status_checked=stamp, message=msg)
            write(out, log + [row], FU_FIELDS)
            print(f"follow-up added -> {out} ({len(log) + 1} today): {row['name']} ({row['message_type']}, {len(msg)} chars)")
        elif sub == "today":
            out = followup_dir(track) / f"{stamp}.csv"
            rows = read(out)
            print(f"{out} {len(rows)}")
            print(json.dumps(rows, indent=2, ensure_ascii=False))
        elif sub == "open":
            print(json.dumps([{**r, "file": str(fp)} for t, fp, rows in followup_rows() if t == track
                              for r in rows if r["status"] == "prepared"], indent=2, ensure_ascii=False))
        elif sub in ("sent", "skip"):
            url, hit = norm(rest[0]), None
            for t, fp, rows in followup_rows():
                if t != track:
                    continue
                for r in rows:
                    if norm(r["linkedin_url"]) == url and r["status"] == "prepared":
                        r["status"], r["status_checked"], hit = ("sent" if sub == "sent" else "skipped"), stamp, r
                if hit:
                    write(fp, rows, FU_FIELDS)
                    break
            if not hit:
                sys.exit(f"no prepared follow-up for {rest[0]}")
            if sub == "sent":
                path, rows, i = find(track, url)
                rows[i]["status"] = "messaged"
                rows[i]["status_checked"] = rows[i]["last_msg_date"] = stamp
                rows[i]["msg_count"] = str(int(rows[i].get("msg_count") or 0) + 1)
                write(path, rows)
            print(f"{hit['status']}: {hit['name']} ({hit['message_type']})")
        else:
            sys.exit("followup add|today|open|sent|skip")

    elif cmd == "company":
        site, name = domain(args[0]), company_key(args[1] if len(args) > 1 else "")
        same = lambda r: (site and domain(r.get("company_site")) == site) or (name and company_key(r.get("company")) == name)
        for r in all_rows():
            age = days_since(r.get("date_sent"))
            if same(r) and age is not None and age < COMPANY_COOLDOWN and r.get("status") != "not-sent":
                sys.exit(f"SKIP for {COMPANY_COOLDOWN - age} more days: {r['name']} at {r['company']} is in {r['_where']} ({r['status']})")
        for r in read(me.out_dir("product-outreach") / "contacted.csv"):
            age = days_since(r.get("date"))
            if same(r) and age is not None and age < COMPANY_COOLDOWN and r.get("status") != "withdrawn":
                sys.exit(f"SKIP for {COMPANY_COOLDOWN - age} more days: product outreach emailed {r['person']} on {r['date']}")
        for ap in me.out_dir("apply").rglob("applied.csv"):
            for r in read(ap):
                if name and company_key(r.get("company")) == name:
                    print(f"info: applied to '{r.get('title')}' there on {r.get('date')} ({r.get('folder')})")
        print(f"new: no track touched this company in the last {COMPANY_COOLDOWN} days")

    elif cmd == "rejected":
        print("\n".join(sorted(rejected_urls())))

    elif cmd == "stats":
        counts = {}
        for p in day_files(send_dir(track)):
            for r in read(p):
                counts[r["status"]] = counts.get(r["status"], 0) + 1
        counts["rejected"] = sum(len(read(p)) for p in day_files(reject_dir(track)))
        connected = sum(v for k, v in counts.items() if k in CONNECTED)
        sent = connected + counts.get("pending", 0) + counts["rejected"]
        talked = sum(counts.get(k, 0) for k in ("replied", "call", "interview", "offer", "proposal", "won"))
        print(json.dumps({**counts,
                          "accepted_of_sent": f"{connected}/{sent}" + (f" ({connected / sent:.0%})" if sent else ""),
                          "still_pending": counts.get("pending", 0),
                          "replied_of_accepted": f"{talked}/{connected}",
                          "calls_or_more": sum(counts.get(k, 0) for k in ("call", "interview", "offer", "proposal", "won"))}, indent=2))

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
