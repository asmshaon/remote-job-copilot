"""Build a one-page tailored resume in the "modern" style for the person in `.me`.

The modern style is a clean one-column page: name and tagline on the left with the contact links in a
2 x 2 grid on the right, then CAREER SUMMARY, PROFESSIONAL EXPERIENCE and SKILLS (a two-column grid).
Black, white and gray only. Arial / Liberation Sans. Rendered as HTML by Chromium (Playwright), so the
text stays selectable for an ATS.

Everything personal comes from the person's profile.json (full_name, email, linkedin, github, portfolio)
and from the content file. Nothing about any one person is written in this script.

Normally run through build_resume.py, which sends here when profile.json has "resume_style": "modern":
  python .claude/skills/custom-resume/scripts/build_resume.py <content.json> <out.pdf>
or directly:
  python .claude/skills/custom-resume/scripts/build_modern.py <content.json> <out.pdf>

content.json for the modern style:
  {
    "style": "modern",
    "job": {"company": "...", "title": "...", "url": "..."},
    "keywords": ["...", ...],                        # hard skills/terms from the job post
    "page": "A4" | "Letter",                         # Letter for US/Canada jobs, A4 for the rest (default:
                                                     # profile.json "resume_page", else A4)
    "tagline": "Senior Backend Engineer · Payments and APIs",   # one line, no DevOps-first titles
    "summary": "3 to 4 sentences",
    "jobs": [{"company": "...", "role": "...", "dates": "Mon YYYY – Mon YYYY · Remote",
              "ctx": "optional one-line italic context", "bullets": ["...", "..."]}],
    "earlier": ["2009 to 2015", "one paragraph"],    # optional
    "skills": [["Frontend:", ["React", "Next.js"]], ...]   # 4 to 8 categories, 2 to 5 items each
  }

Checks (exits non-zero and writes no PDF when one fails): every bullet and the summary pass the shared
human-writing lint; no em dash anywhere; the page is exactly one page; the empty band under the last line
is at most 24pt (fill it with real content, never bigger fonts); no bullet or paragraph ends with a single
word alone on its last line. On success it prints the measured bottom gap, the ATS text and the keyword
coverage.
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from glob import glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "job-apply-shared" / "scripts"))
import me  # noqa: E402

PAGE_H = {"A4": 841.89, "Letter": 792.0}
BOTTOM_MARGIN = 28.8      # 0.4in
MAX_GAP = 24.0            # pt of empty space allowed under the last line

ICONS = {
    "email": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24"><rect x="1" y="1" width="22" height="22" rx="3" fill="currentColor"/><circle cx="7" cy="7" r="1.8" fill="#fff"/><rect x="5.3" y="10" width="3.4" height="9" fill="#fff"/><path d="M10.8 10h3.2v1.4c.5-.9 1.6-1.7 3.2-1.7 2.6 0 3.4 1.6 3.4 4.2V19h-3.4v-4.4c0-1.2-.3-2.1-1.5-2.1s-1.7.9-1.7 2.1V19h-3.2z" fill="#fff"/></svg>',
    "github": '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>',
    "website": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>',
}

CSS = """
@page { size: %(page)s; margin: 0.45in 0.5in 0.4in 0.5in; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, "Liberation Sans", Helvetica, sans-serif; font-size: 8.75pt; line-height: 1.3; color: #111; background: #fff; }
a { color: inherit; text-decoration: none; }
header { display: flex; justify-content: space-between; align-items: flex-end; gap: 18pt; padding-bottom: 6pt; }
h1 { white-space: nowrap; font-size: 19pt; letter-spacing: -0.2pt; line-height: 1.1; color: #000; }
.tagline { white-space: nowrap; font-size: 9.6pt; font-weight: bold; color: #333; margin-top: 3pt; }
.contact { display: grid; grid-template-columns: auto auto; column-gap: 12pt; row-gap: 3pt; font-size: 8.6pt; color: #111; padding-left: 12pt; flex: none; border-left: 0.5pt solid #999; }
.contact a { display: flex; align-items: center; gap: 4pt; }
.contact svg { width: 9pt; height: 9pt; color: #333; flex: none; }
h2 { font-size: 8.9pt; text-transform: uppercase; letter-spacing: 1pt; color: #000; margin: 8pt 0 3pt; padding-bottom: 2pt; border-bottom: 0.5pt solid #999; }
h2.exp, h2.skl { margin-top: 12pt; }
.job { margin-top: 7pt; }
.job-head { display: flex; justify-content: space-between; align-items: baseline; }
.co { font-weight: bold; font-size: 9.4pt; color: #000; }
.sep { color: #999; margin: 0 4pt; }
.role { font-weight: bold; }
.date { font-size: 8.4pt; color: #555; white-space: nowrap; }
.ctx { font-style: italic; font-size: 8.4pt; color: #555; margin: 1pt 0 1.5pt; }
ul { padding-left: 11pt; }
li { margin-bottom: 1.4pt; }
li::marker { color: #555; }
.earlier { margin-top: 7pt; font-size: 8.5pt; }
.skills { display: grid; grid-template-columns: 0.85in 1fr 0.85in 1fr; column-gap: 6pt; row-gap: 4pt; }
.skills b { font-weight: bold; }
"""


def contacts(p):
    """Contact links from profile.json. Only the ones the person has are shown."""
    out = []
    if p.get("email"):
        out.append(("email", f"mailto:{p['email']}", p["email"]))
    for key, icon in (("linkedin", "linkedin"), ("github", "github"), ("portfolio", "website")):
        url = (p.get(key) or "").strip()
        if url:
            text = re.sub(r"^https?://(www\.)?", "", url).rstrip("/")
            out.append((icon, url, text))
    return out


def render(cv, p, page):
    e = lambda s: html.escape(s, quote=False)
    links = "".join(f'<a href="{href}">{ICONS[k]}<span>{e(t)}</span></a>' for k, href, t in contacts(p))
    jobs = []
    for j in cv["jobs"]:
        ctx = f'<div class="ctx">{e(j["ctx"])}</div>' if j.get("ctx") else ""
        bullets = "".join(f"<li>{e(b)}</li>" for b in j["bullets"])
        jobs.append(
            f'<div class="job"><div class="job-head"><span><span class="co">{e(j["company"])}</span>'
            f'<span class="sep">|</span><span class="role">{e(j["role"])}</span></span>'
            f'<span class="date">{e(j["dates"])}</span></div>{ctx}<ul>{bullets}</ul></div>')
    earlier = ""
    if cv.get("earlier"):
        label, text = cv["earlier"]
        earlier = f'<div class="earlier"><b>Earlier Experience ({e(label)}):</b> {e(text)}</div>'
    skills = "".join(f"<b>{e(k)}</b><span>{e(', '.join(v))}</span>" for k, v in cv["skills"])
    name = p.get("full_name", "")
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>{e(name)} | Resume</title><style>{CSS % {"page": page}}</style></head><body>
<header><div><h1>{e(name)}</h1><div class="tagline">{e(cv["tagline"])}</div></div>
<div class="contact">{links}</div></header>
<h2>Career Summary</h2><p>{e(cv["summary"])}</p>
<h2 class="exp">Professional Experience</h2>{''.join(jobs)}{earlier}
<h2 class="skl">Skills</h2><div class="skills">{skills}</div>
</body></html>"""


def find_chromium():
    """A Chromium already on this machine, so `playwright install` is only needed when none is found."""
    roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), str(Path.home() / ".cache" / "ms-playwright"),
             str(Path.home() / "Library" / "Caches" / "ms-playwright"),
             str(Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"), "/opt/pw-browsers"]
    patterns = ["chromium_headless_shell-*/*/chrome-headless-shell*", "chromium-*/chrome-*/chrome",
                "chromium-*/chrome-*/chrome.exe", "chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium"]
    found = [f for r in roots if r for pat in patterns for f in glob(os.path.join(r, pat)) if os.path.isfile(f)]
    return sorted(found, reverse=True)[0] if found else None


def to_pdf(doc, out):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("NOT BUILT: the modern style needs Playwright. Run:  pip install -r requirements.txt  "
                 "then  python -m playwright install chromium")
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception:
            exe = find_chromium()
            if exe:
                browser = pw.chromium.launch(executable_path=exe)
            else:
                try:
                    browser = pw.chromium.launch(channel="chrome")  # the installed Google Chrome
                except Exception:
                    sys.exit("NOT BUILT: no Chromium found. Run:  python -m playwright install chromium")
        page = browser.new_page()
        page.set_content(doc)
        page.pdf(path=str(out), prefer_css_page_size=True, print_background=True)
        browser.close()


def measure(pdf, page):
    """(page count, bottom gap in pt, single-word last lines)."""
    from pypdf import PdfReader
    pages = len(PdfReader(str(pdf)).pages)
    box = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    ymax = max(float(y) for y in re.findall(r'<word [^>]*yMax="([\d.]+)"', box))
    widows = []
    for block in re.findall(r"<block [^>]*>(.*?)</block>", box, re.S):
        lines = [re.findall(r">([^<]+)</word>", ln) for ln in re.findall(r"<line [^>]*>(.*?)</line>", block, re.S)]
        # a wrapped bullet or paragraph whose last line holds one word (bullets end with a full stop)
        widows += [ln[0] for i, ln in enumerate(lines) if i > 0 and len(ln) == 1 and ln[0].endswith(".")]
    return pages, round(PAGE_H[page] - BOTTOM_MARGIN - ymax, 1), widows


def build(content_path, out_path):
    from build_resume import lint  # the shared bullet lint (AI words, characters, sentence length)
    cv = json.loads(Path(content_path).read_text(encoding="utf-8"))
    p = me.profile()
    page = cv.get("page") or p.get("resume_page") or "A4"
    errors = []
    if page not in PAGE_H:
        errors.append(f"page must be A4 or Letter, not {page}")
    for key in ("tagline", "summary", "jobs", "skills"):
        if not cv.get(key):
            errors.append(f"missing '{key}'")
    if errors:
        sys.exit("NOT BUILT:\n  " + "\n  ".join(errors))

    for j in cv["jobs"]:
        for b in j["bullets"]:
            errors += [f"{j['company']}: {x} in: {b[:70]}..." for x in lint(b)]
    # The summary may speak in first person and may run to 4 sentences.
    errors += [f"summary: {x}" for x in lint(cv["summary"]) if not x.startswith("first person")]
    n = len(re.findall(r"[.!?](\s|$)", cv["summary"].strip()))
    if n > 4:
        errors.append(f"summary has {n} sentences, keep it to 3 or 4")
    if not 4 <= len(cv["skills"]) <= 8:
        errors.append(f"skills: {len(cv['skills'])} categories, use 4 to 8 (6 fills the grid best)")
    doc = render(cv, p, page)
    if "—" in doc:
        errors.append("em dash found")
    if errors:
        sys.exit("NOT BUILT:\n  " + "\n  ".join(dict.fromkeys(errors)))

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        trial = Path(tmp) / "trial.pdf"
        to_pdf(doc, trial)
        pages, gap, widows = measure(trial, page)
        problems = []
        if pages != 1:
            problems.append(f"{pages} pages: cut or merge bullets (never shrink fonts or spacing)")
        elif gap > MAX_GAP:
            problems.append(f"{gap}pt empty at the bottom (max {MAX_GAP:.0f}pt): add real content from the "
                            f"accomplishments (a bullet is about 12pt a line), never bigger fonts")
        problems += [f"single word '{w}' alone on a last line: reword that bullet" for w in widows]
        if problems:
            sys.exit(f"NOT BUILT ({page}, {pages} page(s), bottom gap {gap}pt):\n  " + "\n  ".join(problems))
        out.write_bytes(trial.read_bytes())

    from pypdf import PdfReader
    text = PdfReader(str(out)).pages[0].extract_text()
    print(f"built {out} (modern, {page}, 1 page, bottom gap {gap}pt)")
    print("---- ATS text ----")
    print(text)
    kws = cv.get("keywords", [])
    if kws:
        flat = re.sub(r"\s+", " ", text).lower()
        have = [k for k in kws if k.lower() in flat]
        print("---- keywords ----")
        print(f"present {len(have)}/{len(kws)}: {', '.join(have)}")
        print(f"missing: {', '.join(k for k in kws if k not in have) or 'none'}")


def venv_python():
    """The repo's .venv Python (pip install -r requirements.txt there), when this one lacks Playwright."""
    root = HERE.parents[3]
    for rel in (".venv/bin/python", ".venv/Scripts/python.exe"):
        if (root / rel).exists():
            return root / rel
    return None


def main(args=None):
    args = sys.argv[1:] if args is None else args
    if len(args) != 2 or args[0].startswith("--"):
        sys.exit(__doc__)
    try:
        import playwright  # noqa: F401
    except ImportError:
        py = venv_python()
        in_venv = Path(sys.prefix).resolve() == (HERE.parents[3] / ".venv").resolve()
        if py and not in_venv:
            sys.exit(subprocess.run([str(py), str(Path(__file__).resolve()), *args]).returncode)
    build(args[0], args[1])


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
