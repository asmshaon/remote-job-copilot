# Remote Job Copilot

Claude Code skills that help you find remote jobs and apply to them.

- Finds real jobs that fit your work and checks each one on the company's own site
- Builds a one-page resume for each job, from your own files
- Writes cover letters, form answers and LinkedIn notes in plain English

**You stay in control.** Claude never sends, submits or posts anything. You do that yourself.
**Your data stays on your computer.** Your profile and results are never pushed to git.

## Get started (about 15 minutes)

You need [Claude Code](https://claude.com/claude-code), Git, Python 3.10+, and Chrome with the Claude extension.

**1. Get the repo**

```bash
git clone <repo url>
cd <repo name>
```

**2. Install the Python packages**

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

On Windows, use `.venv\Scripts\` instead of `.venv/bin/`.

**3. Start Claude Code with Chrome**

```bash
claude --chrome
```

**4. Set up your profile**

Type `profile setup`. Have your resume (PDF) and a list of your past projects ready.
Claude reads them and asks you a few questions once.

## Use it every day

| Type this | You get |
|---|---|
| `daily jobs` | 3 to 5 good jobs, each with a tailored resume and a cover note. **Start here.** |
| `apply <job link>` | a resume and cover letter for one job you found |
| `custom resume <job link>` | just the tailored resume |
| `outreach` | LinkedIn notes for founders and hiring managers |

After you apply, tell Claude: `applied 1, 3`. It won't show you those jobs again for 6 months.

Your results are saved in `apply/<your-name>/`.

## Need more?

The [full guide](GUIDE.md) covers every command, your settings, resume styles, working as a team,
and fixes for common problems.

A public copy of the tool is at https://github.com/asmshaon/remote-job-copilot.
