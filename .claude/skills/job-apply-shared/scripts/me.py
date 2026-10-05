"""Who is using this workspace right now, and their settings.

Several people share this repo. Each person has their own folder:

  skillsets-and-contributions/<me>/     their files and settings (profile.json, resume, accomplishments...)
  apply/<me>/                           their job applications
  linkedin/<me>/                        their LinkedIn outreach ledgers and messages
  product-outreach/<me>/                their product outreach notes and ledger
  upwork/<me>/                          their Upwork profile files

<me> is the folder name (a slug like `jane-doe`). It comes from, in order:
  1. the JOB_HUNT_ME environment variable
  2. the file `.me` at the repo root (one line, the slug; git-ignored, so every person keeps their own)

Usage (from the repo root):
  python .claude/skills/job-apply-shared/scripts/me.py            the slug, e.g. jane-doe
  python .claude/skills/job-apply-shared/scripts/me.py date       today's date in the person's time zone (YYYY-MM-DD)
  python .claude/skills/job-apply-shared/scripts/me.py stamp      date, time and offset for commit messages
  python .claude/skills/job-apply-shared/scripts/me.py paths      every folder and file the skills use for this person
  python .claude/skills/job-apply-shared/scripts/me.py show       profile.json, pretty printed
  python .claude/skills/job-apply-shared/scripts/me.py check      what is missing before the skills can run
  python .claude/skills/job-apply-shared/scripts/me.py set <slug> write `.me` (switch person on this machine)

Other scripts import it: `from me import slug, profile, person_dir, out_dir, now, TZ ...`.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PEOPLE = ROOT / "skillsets-and-contributions"
ME_FILE = ROOT / ".me"
AREAS = ("apply", "linkedin", "product-outreach", "upwork")

# Defaults used when profile.json leaves a field out.
DEFAULT_COMPANY_COUNTRIES = [
    "united states", "usa", "us", "canada", "australia", "new zealand",
    "united kingdom", "uk", "england", "scotland", "wales", "northern ireland", "ireland",
    "germany", "france", "netherlands", "belgium", "luxembourg", "switzerland", "austria",
    "liechtenstein", "denmark", "sweden", "norway", "finland", "iceland", "spain", "portugal",
    "italy", "malta", "monaco", "greece", "cyprus", "poland", "czech republic", "czechia",
    "slovakia", "hungary", "slovenia", "croatia", "romania", "bulgaria", "estonia", "latvia",
    "lithuania",
    "singapore", "japan", "south korea", "korea", "hong kong", "taiwan",
    "united arab emirates", "uae", "qatar", "israel",
]
DEFAULT_OUTREACH_COUNTRIES = [
    "united states", "usa", "us", "canada", "australia", "singapore",
    "united kingdom", "uk", "england", "scotland", "wales", "northern ireland",
    "ireland", "germany", "france", "netherlands", "belgium", "luxembourg", "switzerland",
    "austria", "liechtenstein", "denmark", "sweden", "norway", "finland", "iceland",
    "spain", "portugal", "italy", "malta", "monaco", "andorra", "greece", "cyprus",
    "poland", "czech republic", "czechia", "slovakia", "hungary", "slovenia", "croatia",
    "romania", "bulgaria", "estonia", "latvia", "lithuania", "serbia", "bosnia and herzegovina",
    "montenegro", "north macedonia", "albania", "moldova", "ukraine",
]
REQUIRED = ["slug", "full_name", "email", "headline", "home_country", "city", "utc_offset",
            "resume_file", "pay"]


def slug():
    s = (os.environ.get("JOB_HUNT_ME") or (ME_FILE.read_text(encoding="utf-8") if ME_FILE.exists() else "")).strip()
    if not s:
        sys.exit("No person set. Write your folder name (from skillsets-and-contributions/) into a file "
                 "called .me at the repo root, e.g.\n  python .claude/skills/job-apply-shared/scripts/me.py set jane-doe\n"
                 "New here? Say \"profile setup\" in Claude Code.")
    if not (PEOPLE / s).is_dir():
        sys.exit(f".me says '{s}', but skillsets-and-contributions/{s}/ does not exist. "
                 "Say \"profile setup\" in Claude Code to create it.")
    return s


def person_dir():
    return PEOPLE / slug()


def profile():
    path = person_dir() / "profile.json"
    if not path.exists():
        sys.exit(f"missing {path.relative_to(ROOT)}. Say \"profile setup\" in Claude Code to create it.")
    return json.loads(path.read_text(encoding="utf-8"))


def lower_list(key, default):
    return {c.strip().lower() for c in (profile().get(key) or default)}


def company_countries():
    """Countries a target company may be based in (job apply, product outreach)."""
    return lower_list("company_countries", DEFAULT_COMPANY_COUNTRIES) - blocked_countries()


def outreach_countries():
    """Countries a LinkedIn outreach person (and their company) may be in."""
    return lower_list("outreach_countries", DEFAULT_OUTREACH_COUNTRIES) - blocked_countries()


def blocked_countries():
    """Countries the person never targets, even for a job they pick themselves."""
    return {c.strip().lower() for c in (profile().get("blocked_countries") or [])}


def tz():
    return timezone(timedelta(hours=float(profile().get("utc_offset", 0))))


def now():
    return datetime.now(tz())


def today():
    return now().date()


def out_dir(area):
    """apply/<me>, linkedin/<me>, product-outreach/<me> or upwork/<me>."""
    if area not in AREAS:
        raise ValueError(area)
    return ROOT / area / slug()


def resume_base_path():
    return person_dir() / "resume" / "resume-base.json"


def find_one(folder, patterns):
    folder = person_dir() / folder
    for pat in patterns:
        hits = sorted(h for h in folder.glob(pat) if h.is_file() and not h.name.startswith("."))
        if hits:
            return hits[0]
    return None


def paths():
    p, d = profile(), person_dir()
    rel = lambda x: str(x.relative_to(ROOT)).replace("\\", "/") if x else None
    return {
        "me": slug(),
        "profile": rel(d / "profile.json"),
        "profile_answers": rel(d / "profile-answers.md"),
        "proof_map": rel(d / "proof-map.md"),
        "accomplishments": rel(find_one("contributions", ["*.pdf", "*.md", "*.docx", "*"])),
        "skill_set": rel(find_one("skills", ["*.md", "*"])),
        "resume_pdf": rel(d / "resume" / p.get("resume_file", "resume.pdf")),
        "resume_base": rel(resume_base_path()),
        "profile_picture": rel(find_one("profile-picture", ["*.jpg", "*.jpeg", "*.png"])),
        "product_directories": rel(find_one("product-directories", ["*.pdf", "*.md", "*"])),
        "address": rel(d / "others" / "address" / "address.txt"),
        "phone": rel(d / "others" / "contacts" / "phone.txt"),
        "apply": rel(out_dir("apply")),
        "linkedin": rel(out_dir("linkedin")),
        "product_outreach": rel(out_dir("product-outreach")),
        "upwork": rel(out_dir("upwork")),
    }


def check():
    p, d, problems = profile(), person_dir(), []
    problems += [f"profile.json: '{k}' is missing" for k in REQUIRED if p.get(k) in (None, "", [], {})]
    if p.get("slug") and p["slug"] != slug():
        problems.append(f"profile.json: slug is '{p['slug']}' but the folder is '{slug()}'")
    pay = p.get("pay") or {}
    if not pay.get("min_month"):
        problems.append("profile.json: pay.min_month is missing")
    for key, label in (("accomplishments", "contributions/ (career accomplishments)"),
                       ("skill_set", "skills/ (skill set)"),
                       ("profile_picture", "profile-picture/"),
                       ("product_directories", "product-directories/")):
        if not paths()[key]:
            problems.append(f"nothing in {label}")
    for name in ("profile-answers.md", "proof-map.md", "resume/resume-base.json", f"resume/{p.get('resume_file', '?')}"):
        if not (d / name).exists():
            problems.append(f"missing {name}")
    for name in ("others/address/address.txt", "others/contacts/phone.txt"):
        if not (d / name).exists():
            problems.append(f"missing {name} (only needed when a form asks; never committed)")
    return problems


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "slug"
    if cmd == "set":
        if len(args) < 2 or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args[1]):
            sys.exit("usage: me.py set <slug>   (lowercase letters, digits and hyphens)")
        ME_FILE.write_text(args[1] + "\n", encoding="utf-8")
        print(f"this machine now works as '{args[1]}' (.me)")
    elif cmd == "slug":
        print(slug())
    elif cmd == "date":
        print(f"{today():%Y-%m-%d}")
    elif cmd == "stamp":
        print(now().strftime("%Y-%m-%d %H:%M %z"))
    elif cmd == "paths":
        print(json.dumps(paths(), indent=2))
    elif cmd == "show":
        print(json.dumps(profile(), indent=2, ensure_ascii=False))
    elif cmd == "check":
        problems = check()
        if problems:
            sys.exit("NOT READY:\n  " + "\n  ".join(problems))
        print(f"ready: {slug()}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
