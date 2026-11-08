"""Shared helpers for every job-apply skill (see .claude/skills/job-apply-shared/RULES.md).

Every command takes `--source <name>`, one of: linkedin, post, twitter, hn, himalayas, wellfound, yc,
others, direct. It picks the ledger apply/<me>/<folder>/applied.csv (folders in SOURCE_DIRS below), where
<me> is the person in `.me` (see me.py). The 6-month duplicate check looks at ALL of that person's
ledgers, so a job applied to from one source is blocked in the others too.

  python .claude/skills/job-apply-shared/scripts/apply.py --source <name> check <job_url> ["<company>"] ["<title>"] ["<apply_url>"]
      SKIP if this job (same source job id, company + title, or apply URL) was applied to in the last 6 months.
  python .claude/skills/job-apply-shared/scripts/apply.py --source <name> add '<json row>'
      Record one application in the source's applied.csv (status applied, or email-draft).
      Requires company_country from the person's target countries (profile.json company_countries).
  python .claude/skills/job-apply-shared/scripts/apply.py set <linkedin_job_url> <status>
      Update status: applied | email-draft | withdrawn.
  python .claude/skills/job-apply-shared/scripts/apply.py drafts
      Rows still in email-draft status (check Gmail Sent for them).
  python .claude/skills/job-apply-shared/scripts/apply.py country "<country>"
      ok if a company based there may be targeted.
  python .claude/skills/job-apply-shared/scripts/apply.py email <email.md> [--fixed-subject] [--paras 4]
      Check an application email against the writing rules. --fixed-subject when the job post dictates the subject.
      --paras 4 for the 4-paragraph product-outreach email (default 3): 100-190 words, no skills in paragraph 3.
  python .claude/skills/job-apply-shared/scripts/apply.py text "<answer>"
      Check a free-text form answer for AI-sounding words.

email.md format:
  Subject: <subject>
  To: <address>

  Hi <Name>,

  <paragraph 1: the company and its product, appreciation, optional verified bug>

  <paragraph 2: the user, told through what they built and why, no skill lists>

  <paragraph 3: close about them, another appreciation, wanting to be part of the team>

  Best regards,          (closing for the recipient's culture, see HUMAN-WRITING.md section 4)
  [Gmail default signature]
"""
import csv
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import me  # noqa: E402  who is running this (.me) and their profile.json

# Source -> sub-folder of apply/<me>/. "direct" = one job link the user shared: apply/<me>/<date>/<company>/,
# ledger apply/<me>/applied.csv.
SOURCE_DIRS = {"linkedin": "linkedin-job", "post": "linkedin-post", "others": "others", "twitter": "twitter",
               "hn": "hackernews", "wellfound": "wellfound", "yc": "yc", "himalayas": "himalayas", "direct": ""}
SOURCE = "linkedin"
if "--source" in sys.argv:
    SOURCE = sys.argv[sys.argv.index("--source") + 1]
    SOURCE = {"job": "linkedin"}.get(SOURCE, SOURCE)  # old name
    if SOURCE not in SOURCE_DIRS:
        sys.exit(f"--source must be one of {sorted(SOURCE_DIRS)}")
    i = sys.argv.index("--source")
    del sys.argv[i:i + 2]
FIELDS = ["date", "company", "title", "company_country", "pay_range", "pay_usd_month", "linkedin_url",
          "apply_url", "method", "folder", "status"]
STATUSES = {"applied", "email-draft", "withdrawn"}


def source_root(source):
    base = me.out_dir("apply")
    return base / SOURCE_DIRS[source] if SOURCE_DIRS[source] else base


def ledger_path():
    return source_root(SOURCE) / "applied.csv"


def allowed_countries():
    """Where a target company may be based: profile.json company_countries minus blocked_countries."""
    return me.company_countries()


# One word list for every message that goes to another person (HUMAN-WRITING.md).
# linkedin/scripts/ledger.py imports style_problems() from here, so notes and emails share it.
AI_WORDS = [
    "delve", "leverage", "leveraging", "leveraged", "utilize", "utilized", "utilizing", "synergy", "synergies",
    "cutting-edge", "cutting edge", "game-changer", "game changer", "resonate", "resonated", "resonates",
    "passionate", "passion for", "thrilled", "excited to", "truly", "incredibly", "impressive", "impressed by",
    "amazing", "fantastic", "stellar", "top-notch", "journey", "seamless", "seamlessly", "robust", "innovative",
    "elevate", "empower", "unlock", "spearhead", "spearheaded", "streamline", "harnessing", "fostering", "showcase",
    "showcasing", "realm", "landscape", "ecosystem", "tapestry", "testament", "pivotal", "crucial",
    "comprehensive", "meticulous", "holistic", "invaluable", "commendable", "noteworthy", "furthermore",
    "moreover", "additionally", "nevertheless", "subsequently", "world-class", "state-of-the-art",
    "best-in-class", "revolutionize", "revolutionizing", "results-driven", "proven track record",
    "team player", "detail-oriented", "go-getter", "keen interest", "valuable insights", "your expertise",
    "your insights", "mutual benefit", "mutually beneficial", "in today's", "fast-paced", "at the intersection",
    "deep dive", "dive into", "not just", "it's not about", "whether you're",
    "i am writing to", "i'm writing to", "hope this email finds you", "hope this finds you", "hope this message",
    "hope you are doing well", "hope you're doing well", "i came across", "came across your", "reach out",
    "i'm reaching out", "i am reaching out", "look forward to", "looking forward to", "please find attached",
    "attached is my resume", "i'd love to connect", "i would love to connect", "would be great to connect",
    "let's connect", "expand my network", "grow my network", "don't hesitate", "feel free to",
    "at your earliest convenience", "i wanted to take a moment", "i noticed that you",
]
GENERIC_GREETINGS = ["dear hiring manager", "dear sir", "dear madam", "to whom it may concern",
                     "dear recruiter", "dear hiring team", "hello hiring manager", "hi hiring manager",
                     "dear team", "respected sir"]
DESPERATE = ["need this job", "need a job", "any opportunity", "any position", "desperate", "urgent",
             "please consider me", "i really need", "looking for a job", "looking for job",
             "job opportunity", "give me a chance", "grateful for any", "would be a dream",
             "i am unemployed", "currently unemployed", "open to any role", "will work for",
             "open to work", "new opportunities", "exploring opportunities", "new opportunity",
             "looking for a role", "looking for work", "looking for new"]
# Emails end with one closing line, then Gmail's default signature (never a hand-typed name or links).
CLOSINGS = ["best,", "best regards,", "kind regards,", "regards,", "best wishes,", "cheers,", "thanks,", "many thanks,"]
SIGNATURE = "[Gmail default signature]"
GENERIC_SUBJECTS = ["application for", "job application", "applying for", "resume", "cv for",
                    "application -", "application:", "interested in the", "position of", "candidate for"]
# Tool and language names the "about the user" paragraph of an email must not list. The person's own
# skill pool (resume-base.json) and profile.json stack terms are added on top.
EXTRA_SKILL_TERMS = ["javascript", "typescript", "node", "nodejs", "node.js", "nestjs", "express",
                     "react", "next.js", "nextjs", "vue", "angular", "svelte", "postgres", "postgresql", "mysql",
                     "mongodb", "redis", "elasticsearch", "rabbitmq", "kafka", "bullmq", "aws", "gcp", "azure",
                     "docker", "kubernetes", "terraform", "graphql", "rest api", "rest apis", "microservices", "sql",
                     "nosql", "ci/cd", "typeorm", "prisma", "python", "django", "flask", "fastapi", "java",
                     "spring boot", "kotlin", "golang", "ruby on rails", "rails", "php", "laravel", ".net", "c#",
                     "flutter", "react native"]
BAD_CHARS = {"—": "em dash", "–": "en dash", "’": "curly apostrophe", "‘": "curly quote",
             "“": "curly quote", "”": "curly quote", "…": "ellipsis character",
             ";": "semicolon"}


def has(text, phrase):
    return re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text) is not None


def style_problems(text):
    low = text.lower()
    out = [f"AI-sounding: '{w}'" for w in AI_WORDS if has(low, w)]
    out += [f"sounds needy: '{w}'" for w in DESPERATE if has(low, w)]
    out += [f"character: {n}" for ch, n in BAD_CHARS.items() if ch in text]
    if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", text):
        out.append("emoji")
    if text.count("!") > 1:
        out.append("more than one '!'")
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
        words = sentence.split()
        if len(words) > 30:
            out.append(f"sentence of {len(words)} words, split it (max 30): '{' '.join(words[:8])}...'")
    return out


def skill_terms():
    terms = set(EXTRA_SKILL_TERMS)
    try:
        pool = json.loads(me.resume_base_path().read_text(encoding="utf-8"))["skill_pool"]
        terms |= {i.lower() for items in pool.values() for i in items}
        terms |= {t.lower() for t in me.profile().get("stack", {}).get("terms", [])}
    except (OSError, KeyError, ValueError, SystemExit):
        pass
    return sorted(terms)


def check_email(path, fixed_subject, n_paras=3):
    raw = Path(path).read_text(encoding="utf-8").strip()
    head, _, body = raw.partition("\n\n")
    subject = next((l[8:].strip() for l in head.splitlines() if l.lower().startswith("subject:")), "")
    blocks = [b.strip() for b in re.split(r"\n\s*\n", body.strip()) if b.strip()]
    problems = []

    if not subject:
        problems.append("no 'Subject:' line")
    elif not fixed_subject:
        if len(subject) > 75:
            problems.append(f"subject is {len(subject)} chars, keep it under 75")
        problems += [f"subject is generic ('{g}')" for g in GENERIC_SUBJECTS if g in subject.lower()]

    if len(blocks) < n_paras + 2:
        sys.exit(f"NOT OK: expected greeting, {n_paras} paragraphs and a sign-off, separated by blank lines")
    greeting, paras, signoff = blocks[0], blocks[1:-1], blocks[-1]
    problems += [f"generic greeting ('{g}')" for g in GENERIC_GREETINGS if g in greeting.lower()]
    sign = [l.strip() for l in signoff.splitlines() if l.strip()]
    if not sign or sign[0].lower() not in CLOSINGS:
        problems.append(f"closing must be one of {CLOSINGS} (pick it for the recipient's culture), got {sign[:1]}")
    if sign[1:] != [SIGNATURE]:
        problems.append(f"after the closing put only the line '{SIGNATURE}' (Gmail adds the signature, never type name or links)")
    if len(paras) != n_paras:
        problems.append(f"{len(paras)} body paragraphs, must be exactly {n_paras}")
    about = 2 if n_paras == 4 else 1  # the paragraph about the user: 3rd in product outreach, 2nd in applications
    if len(paras) > about:
        problems += [f"paragraph {about + 1} lists a skill ('{t}'). Describe what was built, not the stack"
                     for t in skill_terms() if has(paras[about].lower(), t)]
    words = sum(len(p.split()) for p in paras)
    low_w, high_w = (110, 240) if n_paras == 3 else (100, 190)
    if not low_w <= words <= high_w:
        problems.append(f"body is {words} words, aim for {low_w}-{high_w}")
    for i, p in enumerate(paras, 1):
        if len(re.findall(r"[.!?](\s|$)", p)) > 5:
            problems.append(f"paragraph {i} has more than 5 sentences")
    problems += style_problems("\n".join([subject, greeting, *paras, signoff]))

    if problems:
        sys.exit("NOT OK:\n  " + "\n  ".join(dict.fromkeys(problems)))
    print(f"ok: subject '{subject}', {n_paras} paragraphs, {words} words")


def rows(ledger=None):
    ledger = ledger or ledger_path()
    if not ledger.exists():
        return []
    with ledger.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def all_rows():
    """Rows from all of this person's ledgers (every source)."""
    return [r for src in SOURCE_DIRS for r in rows(source_root(src) / "applied.csv")]


def job_id(url):
    m = re.search(r"(?:jobs/view/|currentJobId=|activity[:-]|ugcPost[:-]|share[:-]|/status/)(\d+)", url or "")
    return m.group(1) if m else (url or "").strip().rstrip("/").lower()


def key(company, title):
    clean = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
    return f"{clean(company)}|{clean(title)}"


COOLDOWN_DAYS = 180  # the same job is not applied to again within 6 months


def find(url, company=None, title=None, apply_url=None):
    """Most recent application for this job (same LinkedIn job id, same company + title, or same
    external apply URL, so reposts are caught) that still blocks it. Withdrawn drafts don't count.
    Applications older than COOLDOWN_DAYS no longer block."""
    jid, k = job_id(url), key(company, title) if company and title else None
    au = me.norm_url(apply_url)
    cutoff = me.today() - timedelta(days=COOLDOWN_DAYS)
    hits = [
        r for r in all_rows()
        if r["status"] != "withdrawn"
        and datetime.strptime(r["date"], "%Y-%m-%d").date() > cutoff
        and (job_id(r["linkedin_url"]) == jid
             or (k and key(r["company"], r["title"]) == k)
             or (au and me.norm_url(r.get("apply_url", "")) == au))
    ]
    return max(hits, key=lambda r: r["date"]) if hits else None


def blocked_until(r):
    return datetime.strptime(r["date"], "%Y-%m-%d").date() + timedelta(days=COOLDOWN_DAYS)


def main():
    if len(sys.argv) < 2 or (sys.argv[1] != "drafts" and len(sys.argv) < 3):
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "check":
        r = find(args[0], *(args[1:4]))
        if r:
            sys.exit(f"SKIP until {blocked_until(r)}, applied on {r['date']}: {r['company']} - {r['title']} ({r['folder']})")
        print(f"new: not applied in the last {COOLDOWN_DAYS} days")
    elif cmd == "country":
        ok = args[0].strip().lower() in allowed_countries()
        sys.exit(f"SKIP: {args[0]} is not a target country") if not ok else print("ok")
    elif cmd == "drafts":
        print(json.dumps([r for r in rows() if r["status"] == "email-draft"], indent=2))
    elif cmd == "set":
        url, status = args[0], args[1]
        if status not in STATUSES:
            sys.exit(f"status must be one of {sorted(STATUSES)}")
        data, hit = rows(), None
        for r in data:
            if job_id(r["linkedin_url"]) == job_id(url):
                r["status"], hit = status, r
        if not hit:
            sys.exit(f"not found: {url}")
        with ledger_path().open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(data)
        print(f"{status}: {hit['company']} - {hit['title']}")
    elif cmd == "add":
        row = json.loads(args[0])
        country = row.get("company_country", "").strip().lower()
        # A job the user picked themselves (apply-job-link) may be in any country they okay,
        # except their blocked_countries (profile.json).
        if SOURCE == "direct" and country and country not in me.blocked_countries():
            pass
        elif country not in allowed_countries():
            sys.exit(f"blocked: company_country {row.get('company_country')!r} is not one of this person's target "
                     f"countries (profile.json company_countries, minus blocked_countries).")
        if row.get("status", "applied") not in STATUSES:
            sys.exit(f"status must be one of {sorted(STATUSES)}")
        r = find(row["linkedin_url"], row.get("company"), row.get("title"), row.get("apply_url"))
        if r:
            sys.exit(f"blocked until {blocked_until(r)}: already applied on {r['date']} ({r['folder']})")
        row.setdefault("date", f"{me.today():%Y-%m-%d}")
        row.setdefault("status", "applied")
        data = rows() + [row]
        ledger_path().parent.mkdir(parents=True, exist_ok=True)
        with ledger_path().open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(data)
        print(f"recorded ({len(data)} total): {row['company']} - {row['title']}")
    elif cmd == "email":
        n_paras = int(args[args.index("--paras") + 1]) if "--paras" in args else 3
        check_email(args[0], "--fixed-subject" in args, n_paras)
    elif cmd == "text":
        problems = style_problems(" ".join(args))
        sys.exit("REWRITE: " + "; ".join(problems)) if problems else print("ok")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
