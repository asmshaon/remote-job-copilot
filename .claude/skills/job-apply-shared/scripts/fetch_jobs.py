"""Fetch remote jobs from public job-board APIs for the apply skills, pre-filtered for the person in `.me`.

Usage (from the repo root):
  python .claude/skills/job-apply-shared/scripts/fetch_jobs.py <source[,source...]|all> <out.json> [--days 30]

Sources: hn, himalayas, remotive, remoteok, jobicy, wwr, or all.

Every job comes out in one shape:
  {source, title, company, url, apply_url, location, salary, salary_min, salary_max, currency,
   period, posted, text, stack_hits, worldwide}
What to search and keep comes from the person's profile.json, section "job_search":
  stack_terms      words that count as their stack in a post (e.g. "node.js", "typescript")
  title_must       a title must contain one of these words (default: engineer, developer, programmer, swe)
  title_include    a title must also contain one of these (the role family, e.g. "back[- ]?end", "full[- ]?stack")
  title_strong     a title with one of these is kept even if the post never names the stack
  title_exclude    titles with any of these are dropped (other stacks, role types they don't do)
  queries          {"himalayas": [...], "remotive": [...], "remoteok": [...], "jobicy": [...], "wwr": [category slugs]}
and profile.json "home_country" (Himalayas only returns jobs open to candidates there).

A job is kept only if the title fits, the post mentions their stack or the title is a strong match,
and it is not clearly region-locked. `worldwide` is "yes" when the text says worldwide / anywhere /
global or names their home country, "check" when unclear. Claude still verifies every job on the
company's own page, as the apply skills require. This script only narrows the list.
"""
import hashlib
import html
import json
import os
import random
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import me  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (job search for personal use)"}
SEARCH = me.profile().get("job_search", {})
HOME = me.profile().get("home_country", "")


def words(key, default, whole=False):
    """One regex from a list of profile.json words (regex fragments). whole=True also needs a word end."""
    items = SEARCH.get(key) or default
    return re.compile(r"\b(" + "|".join(items) + (r")\b" if whole else ")"), re.I) if items else None


STACK = [t.lower() for t in SEARCH.get("stack_terms", [])]
ROLE_OK = words("title_must", ["engineer", "developer", "programmer", "swe"], whole=True)
ROLE_SIDE = words("title_include", ["software", "engineer", "developer"])
ROLE_STRONG = words("title_strong", [])
ROLE_BAD = words("title_exclude", ["sales", "recruiter", "intern"], whole=True)
QUERIES = SEARCH.get("queries", {})
WORLDWIDE = re.compile(r"\b(worldwide|anywhere|everywhere|global(ly)?|any (country|location|timezone|time zone)|"
                       r"work from anywhere|all countries|fully distributed|remote[- ]first,? global)\b", re.I)
LOCKED = re.compile(r"(remote\s*[\(\-–:]\s*(us|usa|u\.s\.|united states|canada|eu|europe|uk|emea|americas|latam|"
                    r"north america|apac|india|germany|france|spain|poland|brazil)\b)|"
                    r"\b(us|u\.s\.|usa|eu|uk|canada)[- ]only\b|must (be based|reside|live) in|"
                    r"authori[sz]ed to work in|onsite only|on-site only|hybrid\b", re.I)


CACHE = os.path.join(tempfile.gettempdir(), "job-fetch-cache", datetime.now().strftime("%Y-%m-%d"))
_last = [0.0]


def polite_wait():
    """Leave 1.5-3 s (random) between requests to the same APIs (HUMAN-BROWSING.md)."""
    gap = random.uniform(1.5, 3.0) - (time.time() - _last[0])
    if gap > 0:
        time.sleep(gap)
    _last[0] = time.time()


def get(url, as_json=True):
    """GET with a per-day cache, polite gaps, and Retry-After on 429."""
    path = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest())
    if os.path.exists(path):
        raw = open(path, "rb").read()
        return json.loads(raw) if as_json else raw
    for attempt in range(3):
        polite_wait()
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
            os.makedirs(CACHE, exist_ok=True)
            open(path, "wb").write(raw)
            return json.loads(raw) if as_json else raw
        except urllib.error.HTTPError as e:
            if attempt == 2 or e.code not in (429, 500, 502, 503, 504):
                raise
            retry = e.headers.get("Retry-After", "")
            time.sleep(min(int(retry), 120) if retry.isdigit() else 10 + attempt * 20)
        except Exception:  # noqa: BLE001 - one flaky source must not stop the run
            if attempt == 2:
                raise
            time.sleep(5 + attempt * 10)


def clean(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return re.sub(r"\s+", " ", text).strip()


def stack_hits(text):
    low = text.lower()
    return sorted({s for s in STACK if re.search(rf"(?<![a-z]){re.escape(s)}(?![a-z])", low)})


REGIONS = re.compile(r"\b(emea|europe|european|eu|americas|latam|latin america|north america|apac|asia[- ]pacific|"
                     r"us|usa|u\.s\.|united states|canada|uk|united kingdom|germany|france|spain|portugal|poland|"
                     r"netherlands|ireland|india|brazil|mexico|argentina|australia|cet|est|pst|gmt[+-]?\d*|utc[+-]?\d*)\b", re.I)


def worldwide_flag(source, location, text, restrictions=None):
    """yes = open worldwide (or explicitly includes their home country), no = region-locked, check = unclear."""
    if source == "himalayas":
        return "yes"  # queried with country=<home country>: empty restrictions or a list that includes it
    loc = (location or "").strip()
    if loc:
        if WORLDWIDE.search(loc) or (HOME and re.search(re.escape(HOME), loc, re.I)):
            return "yes"
        if source == "hn":
            # free text like "REMOTE | Full-time | $150k" or "Berlin | ONSITE"
            if REGIONS.search(loc) or LOCKED.search(loc) or not re.search(r"\bremote\b", loc, re.I):
                return "no"
            return "yes" if WORLDWIDE.search(text[:2000]) else "check"
        if loc.lower() not in {"remote", "remote job", "fully remote", "100% remote"}:
            return "no"  # boards put the allowed place here, anything specific means region-locked
    blob = f"{loc} {text[:2000]}"
    if LOCKED.search(blob) and not WORLDWIDE.search(blob):
        return "no"
    return "yes" if WORLDWIDE.search(blob) else "check"


def role_fits(title, text):
    """The person's role family (profile.json job_search), not an excluded title, and their stack or a strong title."""
    if (ROLE_OK and not ROLE_OK.search(title)) or (ROLE_BAD and ROLE_BAD.search(title)):
        return False
    if ROLE_SIDE and not ROLE_SIDE.search(title):
        return False
    return bool(stack_hits(f"{title} {text}") or (ROLE_STRONG and ROLE_STRONG.search(title)) or not STACK)


def job(**kw):
    kw.setdefault("apply_url", kw.get("url"))
    for k in ("location", "salary", "currency", "period", "text"):
        kw.setdefault(k, "")
    for k in ("salary_min", "salary_max"):
        kw.setdefault(k, None)
    kw["text"] = kw["text"][:4000]
    kw["stack_hits"] = stack_hits(f"{kw['title']} {kw['text']}")
    return kw


# ---- sources ---------------------------------------------------------------------------------

def src_hn(since):
    """Top-level comments from the last two 'Ask HN: Who is hiring?' threads."""
    hits = get("https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&hitsPerPage=10")["hits"]
    threads = [h for h in hits if h["title"].startswith("Ask HN: Who is hiring?")][:2]
    out = []
    for t in threads:
        item = get(f"https://hn.algolia.com/api/v1/items/{t['objectID']}")
        for c in item.get("children", []):
            if not c.get("text"):
                continue
            posted = datetime.fromtimestamp(c["created_at_i"], timezone.utc)
            if posted < since:
                continue
            raw = c["text"]
            text = clean(raw)
            first = clean(re.split(r"<p>", raw)[0])
            parts = [p.strip() for p in first.split("|")]
            links = re.findall(r'href="([^"]+)"', raw)
            emails = sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)))
            out.append(job(
                source="hn", title=parts[1] if len(parts) > 1 else first[:120],
                company=parts[0][:80], url=f"https://news.ycombinator.com/item?id={c['id']}",
                apply_url=links[0] if links else "", location=" | ".join(parts[2:])[:200],
                posted=posted.date().isoformat(), text=text, emails=emails, links=links[:10],
                thread=t["title"]))
    return out


def src_himalayas(since):
    out, seen = [], set()
    for q in QUERIES.get("himalayas", []):
        cursor = None
        for _ in range(4):
            url = "https://himalayas.app/jobs/api/search?" + urllib.parse.urlencode(
                {"q": q, **({"country": HOME} if HOME else {}), **({"cursor": cursor} if cursor else {})})
            data = get(url)
            for j in data.get("jobs", []):
                if j["guid"] in seen:
                    continue
                seen.add(j["guid"])
                posted = datetime.fromtimestamp(j["pubDate"], timezone.utc)
                if posted < since:
                    continue
                loc = ", ".join(j.get("locationRestrictions") or []) or "Worldwide"
                out.append(job(
                    source="himalayas", title=j["title"], company=j["companyName"], url=j["guid"],
                    apply_url=j.get("applicationLink") or j["guid"], location=loc,
                    salary_min=j.get("minSalary"), salary_max=j.get("maxSalary"),
                    currency=j.get("currency") or "", period=j.get("salaryPeriod") or "",
                    posted=posted.date().isoformat(), text=clean(j.get("description") or j.get("excerpt")),
                    timezones=j.get("timezoneRestrictions") or [],
                    worldwide_restrictions=j.get("locationRestrictions") or []))
            cursor = data.get("nextCursor")
            if not cursor:
                break
    return out


def src_remotive(since):
    out, seen = [], set()
    for q in QUERIES.get("remotive", []):
        for j in get("https://remotive.com/api/remote-jobs?" + urllib.parse.urlencode({"search": q}))["jobs"]:
            if j["id"] in seen:
                continue
            seen.add(j["id"])
            posted = datetime.fromisoformat(j["publication_date"]).replace(tzinfo=timezone.utc)
            if posted < since:
                continue
            out.append(job(source="remotive", title=j["title"], company=j["company_name"], url=j["url"],
                           location=j.get("candidate_required_location", ""), salary=j.get("salary", ""),
                           posted=posted.date().isoformat(), text=clean(j.get("description"))))
    return out


def src_remoteok(since):
    out, seen = [], set()
    for tag in QUERIES.get("remoteok", []):
        for j in get(f"https://remoteok.com/api?tag={tag}")[1:]:
            if j["id"] in seen:
                continue
            seen.add(j["id"])
            posted = datetime.fromtimestamp(int(j["epoch"]), timezone.utc)
            if posted < since:
                continue
            out.append(job(source="remoteok", title=j["position"], company=j["company"].strip(), url=j["url"],
                           apply_url=j.get("apply_url") or j["url"], location=j.get("location", ""),
                           salary_min=j.get("salary_min") or None, salary_max=j.get("salary_max") or None,
                           currency="USD", period="annual", posted=posted.date().isoformat(),
                           text=clean(j.get("description"))))
        # polite_wait() in get() spaces requests out
    return out


def src_jobicy(since):
    out, seen = [], set()
    for tag in QUERIES.get("jobicy", []):
        for j in get(f"https://jobicy.com/api/v2/remote-jobs?count=100&tag={tag}").get("jobs", []):
            if j["id"] in seen:
                continue
            seen.add(j["id"])
            posted = datetime.fromisoformat(j["pubDate"].replace(" ", "T")).replace(tzinfo=timezone.utc)
            if posted < since:
                continue
            out.append(job(source="jobicy", title=clean(j["jobTitle"]), company=j["companyName"], url=j["url"],
                           location=j.get("jobGeo", ""), salary_min=j.get("annualSalaryMin"),
                           salary_max=j.get("annualSalaryMax"), currency=j.get("salaryCurrency", ""),
                           period="annual", posted=posted.date().isoformat(),
                           text=clean(j.get("jobDescription") or j.get("jobExcerpt"))))
    return out


def src_wwr(since):
    out = []
    for cat in QUERIES.get("wwr", []):
        root = ET.fromstring(get(f"https://weworkremotely.com/categories/{cat}.rss", as_json=False))
        for it in root.iter("item"):
            f = {c.tag: (c.text or "") for c in it}
            posted = datetime.strptime(f.get("pubDate", "")[:25], "%a, %d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            if posted < since:
                continue
            company, _, title = f.get("title", "").partition(": ")
            out.append(job(source="wwr", title=title or company, company=company, url=f.get("link", ""),
                           location=f.get("region", "") + (" " + f.get("country", "") if f.get("country") else ""),
                           posted=posted.date().isoformat(), text=clean(f.get("description"))))
    return out


SOURCES = {"hn": src_hn, "himalayas": src_himalayas, "remotive": src_remotive,
           "remoteok": src_remoteok, "jobicy": src_jobicy, "wwr": src_wwr}


def main():
    args = sys.argv[1:]
    names = list(SOURCES) if args and args[0] == "all" else (args[0].split(",") if args else [])
    if len(args) < 2 or not names or any(n not in SOURCES for n in names):
        sys.exit(__doc__)
    days = int(args[args.index("--days") + 1]) if "--days" in args else 30
    since = datetime.now(timezone.utc) - timedelta(days=days)

    kept, report = [], {}
    for name in names:
        try:
            jobs = SOURCES[name](since)
        except Exception as e:  # noqa: BLE001
            report[name] = f"error: {e}"
            continue
        n_all = len(jobs)
        for j in jobs:
            j["worldwide"] = worldwide_flag(j["source"], j["location"], j["text"], j.get("worldwide_restrictions"))
        jobs = [j for j in jobs if role_fits(j["title"], j["text"]) and j["worldwide"] != "no"]
        report[name] = f"{n_all} fetched, {len(jobs)} kept"
        kept += jobs

    # de-duplicate the same job posted on several boards
    uniq = {}
    for j in kept:
        k = re.sub(r"[^a-z0-9]", "", (j["company"] + "|" + j["title"]).lower())
        if k not in uniq or (uniq[k]["worldwide"] != "yes" and j["worldwide"] == "yes"):
            uniq[k] = j
    kept = sorted(uniq.values(), key=lambda j: j["posted"], reverse=True)
    kept.sort(key=lambda j: j["worldwide"] != "yes")

    with open(args[1], "w", encoding="utf-8") as f:
        json.dump(kept, f, indent=2, ensure_ascii=False)
    for name, line in report.items():
        print(f"{name:10} {line}")
    print(f"total kept after de-dup: {len(kept)} "
          f"(worldwide=yes: {sum(j['worldwide'] == 'yes' for j in kept)}, check: {sum(j['worldwide'] == 'check' for j in kept)}) -> {args[1]}")


if __name__ == "__main__":
    main()
