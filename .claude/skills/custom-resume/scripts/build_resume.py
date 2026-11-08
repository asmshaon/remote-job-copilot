"""Build a one-page tailored resume PDF for the person in `.me`, in the shared resume layout.

The layout (A4, Calibri header, Arial body, sizes, rules and bullet glyphs) is the same for everyone.
The fixed content comes from that person's skillsets-and-contributions/<me>/resume/resume-base.json:
header, contact, company/role/location/dates lines, projects, additional experience, education and
the three skills categories. Only these change per job, from a tailored content file: the highlight
bullets under each job, the description of each featured project (its name and subtitle stay fixed),
and the items inside the fixed skills categories.

Usage (from the repo root):
  python .claude/skills/custom-resume/scripts/build_resume.py <content.json> <out.pdf>
  python .claude/skills/custom-resume/scripts/build_resume.py --base <out.pdf>     # rebuild the current resume as-is
  python .claude/skills/custom-resume/scripts/build_resume.py --lint "<text>"       # check one bullet

content.json (job ids, project ids and categories are the ones in resume-base.json):
  {
    "job": {"company": "...", "title": "...", "url": "..."},
    "keywords": ["...", ...],                            # hard skills/terms from the job post
    "experience": {
      "<job id>": [{"text": "..."}, ...],                # bullet count inside that job's "bullets": [min, max]
      "<job id>": [{"label": "<Project>:", "text": "..."}, ...]   # label optional
    },
    "projects": {"<project id>": "<new description>"},  # optional; name/subtitle fixed
    "skills": {"<Category>": ["...", "..."]}             # optional; a category left out keeps the base text
  }

Exits non-zero, without writing a PDF, if a bullet reads AI-written, the page overflows,
a job's bullet count is out of range, a skills category is not one of the fixed ones,
a skill is not in resume-base.json "skill_pool", or a skills line does not fit on one line. After a
successful build it prints the extracted text (what an ATS reads) and which job keywords are present
or missing.
"""
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.colors import Color, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_DIRS = [Path("C:/Windows/Fonts"), Path("/Library/Fonts"), Path("/System/Library/Fonts/Supplemental"),
             Path.home() / "Library/Fonts", Path("/usr/share/fonts/truetype/msttcorefonts"),
             Path("/usr/share/fonts/truetype/crosextra")]
# name used in the layout: (font files to look for, built-in PDF font if none is installed)
FONTS = {
    "Calibri": (["calibri.ttf", "Calibri.ttf", "Carlito-Regular.ttf"], "Helvetica"),
    "Calibri-Bold": (["calibrib.ttf", "Calibri Bold.ttf", "Carlito-Bold.ttf"], "Helvetica-Bold"),
    "Arial": (["arial.ttf", "Arial.ttf"], "Helvetica"),
    "Arial-Bold": (["arialbd.ttf", "Arial Bold.ttf"], "Helvetica-Bold"),
    "Arial-Italic": (["ariali.ttf", "Arial Italic.ttf"], "Helvetica-Oblique"),
    "Times-BoldTT": (["timesbd.ttf", "Times New Roman Bold.ttf"], "Times-Bold"),
}
FALLBACK_FONTS = []
for name, (files, builtin) in FONTS.items():
    found = next((d / f for d in FONT_DIRS for f in files if (d / f).exists()), None)
    if found:
        pdfmetrics.registerFont(TTFont(name, str(found)))
    else:  # not on Windows and no Microsoft fonts installed: same layout, standard PDF font
        pdfmetrics.registerFont(pdfmetrics.Font(name, builtin, "WinAnsiEncoding"))
        FALLBACK_FONTS.append(name)

# Measurements taken from the original PDF (A4, points, y measured from the top to the baseline).
PAGE_W, PAGE_H = 596, 842
RIGHT = 552.5                 # right edge for dates, locations and the contact block
WRAP_RIGHT = 547.25           # right edge for wrapped text (end of the section rules)
RULE_X, RULE_W, RULE_H = 47.0, 500.25, 0.75
LINK_BLUE = Color(0.07, 0.33, 0.8)
BOTTOM_LIMIT = 800            # last baseline allowed; the original ends at 790.7

DEFAULT_BULLETS = (1, 3)       # per job, unless resume-base.json gives "bullets": [min, max]
MAX_LINES_PER_BULLET = 3

# Words, phrases and characters that make resume text read machine-written.
AI_WORDS = [
    "spearheaded", "spearhead", "leveraged", "leverage", "leveraging", "utilized", "utilize", "utilizing",
    "robust", "seamless", "seamlessly", "cutting-edge", "cutting edge", "state-of-the-art", "best-in-class",
    "world-class", "innovative", "passionate", "synergy", "delve", "orchestrated", "pivotal", "instrumental",
    "transformative", "holistic", "meticulous", "meticulously", "empowered", "empowering", "empower",
    "elevate", "elevated", "streamlined", "streamline", "showcasing", "fostering", "fostered",
    "game-changing", "significantly", "drastically", "blazing", "comprehensive", "ensuring", "harnessed",
    "harness", "paradigm", "tapestry", "testament", "landscape", "ecosystem", "dynamic environment",
    "fast-paced", "results-driven", "detail-oriented", "proven track record", "go-getter", "thought leader",
    "various", "numerous", "a wide range of", "plethora", "myriad", "championed", "revolutionized",
    "enhanced overall", "successfully", "effectively", "efficiently", "strategically", "seamlessly",
]
AI_CHARS = {"\u2014": "em dash", "\u2013": "en dash", "\u2019": "curly apostrophe", "\u2018": "curly quote",
            "\u201c": "curly quote", "\u201d": "curly quote", "\u2026": "ellipsis character", ";": "semicolon",
            "!": "exclamation mark"}


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "job-apply-shared" / "scripts"))
from apply import style_problems  # noqa: E402  shared human-writing check (job-apply-shared/HUMAN-WRITING.md)
import me  # noqa: E402  the person in .me (their resume-base.json)


def lint(text):
    problems = list(style_problems(text))  # shared AI words, needy phrases, characters, sentences over 30 words
    low = text.lower()
    problems += [f"AI-sounding: '{w}'" for w in AI_WORDS if re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", low)]
    problems += [f"character: {n}" for ch, n in AI_CHARS.items() if ch in text]
    if re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", text):
        problems.append("emoji")
    if re.search(r"\b(I|my|me|we|our)\b", text):
        problems.append("first person (I/my/we)")
    if not text.rstrip().endswith("."):
        problems.append("bullet must end with a full stop, like the original")
    return sorted(set(problems))


def width(text, font, size):
    return pdfmetrics.stringWidth(text, font, size)


def wrap_runs(runs, x0, size, right=WRAP_RIGHT):
    """Greedy word wrap of [(text, font)] runs starting at x0. Returns lines of [(text, font)]."""
    words = []
    for text, font in runs:
        for i, w in enumerate(re.split(r"(\s+)", text)):
            if w and not w.isspace():
                words.append((w, font))
    lines, line, x = [], [], x0
    space = width(" ", "Arial", size)
    for w, font in words:
        ww = width(w, font, size)
        need = ww + (space if line else 0)
        if line and x + need > right:
            lines.append(line)
            line, x = [], x0
            need = ww
        line.append((w, font))
        x += need
    if line:
        lines.append(line)
    return lines


class Resume:
    def __init__(self, path, dry=False):
        self.dry = dry
        self.c = None if dry else canvas.Canvas(str(path), pagesize=(PAGE_W, PAGE_H))
        self.y = 0.0
        self.bullet_lines = {}

    # Drawing helpers, y from the top. Every visual line is drawn as ONE text object so an
    # ATS extracts it as one line of text, not one word per line.
    def line(self, y, parts):
        """parts: [(x, text, font, size, color)]; x=None continues right after the previous part."""
        if not self.c:
            return
        t = self.c.beginText()
        for x, s, font, size, color in parts:
            if x is not None:
                t.setTextOrigin(x, PAGE_H - y)
            t.setFont(font, size)
            t.setFillColor(color)
            t.textOut(s)
        self.c.drawText(t)

    def text(self, x, y, s, font, size, color=black):
        self.line(y, [(x, s, font, size, color)])

    def rule(self, y):
        if self.c:
            self.c.setFillColor(black)
            self.c.rect(RULE_X, PAGE_H - y - RULE_H, RULE_W, RULE_H, stroke=0, fill=1)

    def paragraph(self, runs, x, size=10, leading=15.0, bullet=None):
        """Wrapped text at x. bullet=(bx, glyph) puts a bullet glyph at bx on the first line."""
        lines = wrap_runs(runs, x, size)
        for i, words in enumerate(lines):
            if i:
                self.y += leading
            parts = [(bullet[0], bullet[1] + " ", "Arial", size, black)] if bullet and i == 0 else []
            merged = []  # join consecutive words that share a font
            for j, (w, font) in enumerate(words):
                s = (" " if j else "") + w
                if merged and merged[-1][1] == font:
                    merged[-1][0] += s
                else:
                    merged.append([s, font])
            for j, (s, font) in enumerate(merged):
                parts.append((x if j == 0 else None, s, font, size, black))
            self.line(self.y, parts)
        return len(lines)

    @staticmethod
    def at_right(s, font, size):
        return (RIGHT - width(s, font, size), s, font, size, black)

    # sections
    def header(self, base):
        self.text(43.2, 60.1, base["name"], "Calibri-Bold", 20)
        self.text(43.2, 76.2, base["designation"], "Calibri", 13)
        for i, row in enumerate(base["contact"][:4]):  # up to 4 contact rows on the right
            y = 56.7 + i * 14.35
            vx = RIGHT - width(row["text"], "Calibri", 10.5)
            lx = vx - width(row["label"] + " ", "Calibri-Bold", 10.5)
            self.line(y, [(lx, row["label"] + " ", "Calibri-Bold", 10.5, black),
                          (vx, row["text"], "Calibri", 10.5, LINK_BLUE)])
            if self.c:
                self.c.setStrokeColor(LINK_BLUE)
                self.c.setLineWidth(0.75)
                self.c.line(vx, PAGE_H - y - 1.6, RIGHT, PAGE_H - y - 1.6)
                self.c.linkURL(row["url"], (vx, PAGE_H - y - 3, RIGHT, PAGE_H - y + 9), relative=0)

    def heading(self, title, y=None, after=13.4):
        self.y = y if y is not None else self.y + 27.9
        self.text(47.8, self.y, title, "Arial", 11)
        self.rule(self.y + 8.3)
        self.y += 8.3 + after

    def job(self, job, items, first):
        if not first:
            self.y += 25.6
        self.line(self.y, [(50.0, "\u2022 ", "Times-BoldTT", 14, black),
                           (60.0, job["company"] + "  ", "Arial-Bold", 10.5, black),
                           self.at_right(job["location"], "Arial", 9.5)])
        self.y += 12.3
        self.line(self.y, [(49.6, job["role"] + "  ", "Arial-Italic", 10, black),
                           self.at_right(job["dates"], "Arial", 9.5)])
        self.y += 19.8
        counts = []
        for i, item in enumerate(items):
            if i:
                self.y += 16.95
            runs = ([(item["label"], "Arial-Bold")] if item.get("label") else []) + [(item["text"], "Arial")]
            bullet = (60.5, "\u25cb") if len(items) > 1 else None
            counts.append(self.paragraph(runs, 71.8, bullet=bullet))
        self.bullet_lines[job["id"]] = counts

    def titled(self, item, first, text=None):
        if not first:
            self.y += 25.6
        parts = [(47.8, item["name"], "Arial-Bold", 10.5, black), (None, " - ", "Arial", 10.5, black),
                 (None, item["subtitle"] + "  ", "Arial-Bold", 10.5, black)]
        if item.get("dates"):
            parts.append(self.at_right(item["dates"], "Arial", 9.5))
        self.line(self.y, parts)
        self.y += 18.5
        n = self.paragraph([(text or item["text"], "Arial")], 71.8)
        if item.get("id"):
            self.bullet_lines["project:" + item["id"]] = [n]

    def build(self, base, experience, skills=None, projects=None):
        self.header(base)
        self.heading("EXPERIENCE", y=118.6, after=14.9)
        for i, job in enumerate(base["experience"]):
            self.job(job, experience.get(job["id"], job["items"]), i == 0)
        self.heading("PROJECTS")
        for i, p in enumerate(base["projects"]):
            self.titled(p, i == 0, (projects or {}).get(p.get("id")))
        self.heading("ADDITIONAL EXPERIENCE")
        for i, a in enumerate(base["additional"]):
            self.titled(a, i == 0)
        self.heading("EDUCATION")
        for e in base["education"]:
            self.line(self.y, [(47.8, e["degree"], "Arial", 10, black),
                               (None, e["school"] + "  ", "Arial-Bold", 10, black),
                               self.at_right(e["dates"], "Arial", 9.5)])
        self.heading("SKILLS", after=17.0)
        for i, s in enumerate(base["skills"]):
            if i:
                self.y += 17.3
            self.line(self.y, [(47.8, "\u2022 ", "Arial-Bold", 14, black),
                               (58.2, s["label"] + " ", "Arial-Bold", 10, black),
                               (None, (skills or {}).get(s["label"], s["text"]), "Arial", 10, black)])
        return self.y

    def save(self, base):
        self.c.setTitle(f"{base['name'].title()} - Resume")
        self.c.setAuthor(base["name"].title())
        self.c.setSubject(base["designation"])
        self.c.save()


def check_skills(base, wanted):
    """Validate tailored skills. Categories are fixed (Languages, Frameworks, Technologies);
    items must come from base["skill_pool"] and each category must fit on one line.
    Returns ({label: text}, errors). A category left out keeps the base text."""
    labels = [s["label"] for s in base["skills"]]
    pool = {label: {i.lower(): i for i in items} for label, items in base["skill_pool"].items()}
    out, errors = {}, []
    for key, items in wanted.items():
        label = key if key.endswith(":") else key + ":"
        if label not in labels:
            errors.append(f"skills: category '{key}' not allowed, categories are fixed: {', '.join(l[:-1] for l in labels)}")
            continue
        if isinstance(items, str):
            items = [i.strip() for i in items.split(",")]
        if len(items) < 2:
            errors.append(f"skills: {label} needs at least 2 items")
        fixed, seen = [], set()
        for item in items:
            canon = pool[label].get(item.strip().lower())
            if not canon:
                errors.append(f"skills: '{item}' is not in the {label} skill pool (resume-base.json). "
                              "List only skills the user has; add it to the pool first if it is true.")
            elif canon.lower() in seen:
                errors.append(f"skills: '{canon}' listed twice in {label}")
            else:
                seen.add(canon.lower())
                fixed.append(canon)
        text = ", ".join(fixed)
        start = 58.2 + width(label + " ", "Arial-Bold", 10)
        if start + width(text, "Arial", 10) > WRAP_RIGHT:
            errors.append(f"skills: {label} line is too long for one line, drop an item: {text}")
        out[label] = text
    return out, errors


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # bullet glyphs on a Windows console
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--lint":
        problems = lint(" ".join(args[1:]))
        sys.exit("REWRITE: " + "; ".join(problems)) if problems else print("ok")
        return

    # The person picks their resume style in profile.json ("classic" = this layout, "modern" = build_modern.py).
    # A content file can also say "style": "modern" itself.
    style = me.profile().get("resume_style", "classic")
    if args[0] != "--base":
        try:
            c = json.loads(Path(args[0]).read_text(encoding="utf-8"))
            # the content's own shape wins: "experience" = classic, "jobs" = modern
            style = c.get("style") or ("classic" if "experience" in c else "modern" if "jobs" in c else style)
        except (OSError, ValueError):
            pass
    if style == "modern":
        if args[0] == "--base":
            sys.exit("The modern style has no fixed base resume. Build one from a content file instead.")
        import build_modern
        build_modern.main(args[:2])
        return

    base = json.loads(me.resume_base_path().read_text(encoding="utf-8"))
    if args[0] == "--base":
        content, out = {"experience": {}, "keywords": []}, Path(args[1])
    else:
        content, out = json.loads(Path(args[0]).read_text(encoding="utf-8")), Path(args[1])
    experience = content.get("experience", {})

    errors = []
    known = {j["id"] for j in base["experience"]}
    for jid, items in experience.items():
        if jid not in known:
            errors.append(f"unknown job id '{jid}' (use {sorted(known)})")
            continue
        lo, hi = next(j.get("bullets", DEFAULT_BULLETS) for j in base["experience"] if j["id"] == jid)
        if not lo <= len(items) <= hi:
            errors.append(f"{jid}: {len(items)} bullets, allowed {lo}-{hi}")
        for item in items:
            for p in lint(item.get("label", "") + " " + item["text"]):
                errors.append(f"{jid}: {p} in: {item['text'][:70]}...")

    skills, skill_errors = check_skills(base, content.get("skills", {}))
    errors += skill_errors

    dry = Resume(None, dry=True)
    projects = content.get("projects", {})
    project_ids = {p.get("id") for p in base["projects"]}
    for pid, text in projects.items():
        if pid not in project_ids:
            errors.append(f"unknown project id '{pid}' (use {sorted(i for i in project_ids if i)})")
            continue
        for prob in lint(text):
            errors.append(f"project {pid}: {prob} in: {text[:70]}...")

    last = dry.build(base, experience, skills, projects)
    if last > BOTTOM_LIMIT:
        over = last - BOTTOM_LIMIT
        orig = Resume(None, dry=True)
        orig.build(base, {})
        lines = sum(sum(v) for k, v in orig.bullet_lines.items() if not k.startswith("project:"))
        paras = sum(len(v) for k, v in orig.bullet_lines.items() if not k.startswith("project:"))
        errors.append(f"page overflow by {over:.1f}pt (content ends at {last:.1f}pt, limit {BOTTOM_LIMIT}pt). "
                      f"Each wrapped line costs 15pt and each extra bullet 17pt, so cut about {int(over // 15) + 1} line(s). "
                      f"Budget: the base resume uses {lines} experience lines in {paras} bullets/paragraphs.")
    for jid, counts in dry.bullet_lines.items():
        for n, lines in enumerate(counts, 1):
            if lines > MAX_LINES_PER_BULLET:
                errors.append(f"{jid} bullet {n}: {lines} lines, max {MAX_LINES_PER_BULLET}")
    if errors:
        sys.exit("NOT BUILT:\n  " + "\n  ".join(errors))

    out.parent.mkdir(parents=True, exist_ok=True)
    r = Resume(out)
    r.build(base, experience, skills, projects)
    r.save(base)

    text = PdfReader(str(out)).pages[0].extract_text()
    print(f"built {out} (content ends at {last:.1f}pt of {BOTTOM_LIMIT})")
    if FALLBACK_FONTS:
        print(f"note: {', '.join(FALLBACK_FONTS)} not installed, used the standard PDF fonts instead (same layout)")
    print("lines per bullet:", json.dumps(dry.bullet_lines))
    print("---- ATS text ----")
    print(text)
    kws = content.get("keywords", [])
    if kws:
        flat = re.sub(r"\s+", " ", text).lower()
        have = [k for k in kws if k.lower() in flat]
        miss = [k for k in kws if k.lower() not in flat]
        print("---- keywords ----")
        print(f"present {len(have)}/{len(kws)}: {', '.join(have)}")
        print(f"missing: {', '.join(miss) or 'none'}")


if __name__ == "__main__":
    main()
