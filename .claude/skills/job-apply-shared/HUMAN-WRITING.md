# Human writing: every message that goes to another person

Every skill follows this file **whenever it writes something another person will read**. The skill decides **what** to say. This file decides **how** it sounds. That covers:
- **Messages:** emails (applications, product outreach), LinkedIn connection notes, LinkedIn and X DMs, Wellfound notes, Work at a Startup messages, and the follow-up messages suggested to the user after someone accepts.
- **Everything in a job application:** the tailored resume (every bullet and the featured project descriptions), the cover letter (text and PDF), every free-text form answer ("why us", "describe a project", "anything else"), and any description they submit.
- **Profiles on job sites:** headline, "about" text and the short lines under each job (Wellfound, Work at a Startup, any site where a form builds a profile).
- **Notes for the user** (`report.md`, `company-notes.md`, review lists) should be plain too, though they aren't checked.

The reader is a busy founder, engineer or recruiter, often reading on a phone, often not a native English speaker. The text must read like the user typed it themselves: easy, plain, specific, and with nothing that sounds like an LLM wrote it.

## 1. Easy language

- **Short sentences.** Most under 20 words, never over 30. One idea per sentence.
- **Common words.** Write the word you'd say out loud: "use" not "utilize", "help" not "facilitate", "start" not "commence", "about" not "regarding", "but" not "however" at the start, "so" not "therefore".
- **Concrete, not abstract.** Name the real thing: "the invite email link opens a 404", not "some issues in the onboarding experience". "1,200+ servers report every minute", not "large-scale infrastructure".
- **Active voice, real subjects.** "I built the billing flow", not "The billing flow was implemented".
- **Contractions are fine** ("I've", "you're", "it's"). They sound like a person.
- **Numbers as digits** (200+ teams, 50,000+ resumes), taken exactly from the accomplishments file.
- **No jargon the reader didn't use first.** For a CEO, describe what the user sees. Technical detail is for CTOs and engineers.

## 2. Sound like a person, not an LLM

**Never use these words** (the checker refuses them): delve, leverage, utilize, synergy, cutting-edge, game-changer, resonate, passionate, thrilled, excited to, truly, incredibly, impressive, amazing, fantastic, stellar, top-notch, journey, seamless, robust, innovative, elevate, empower, unlock, spearhead, streamline, harnessing, fostering, showcase, realm, landscape, ecosystem, tapestry, testament, pivotal, crucial, comprehensive, meticulous, holistic, invaluable, commendable, noteworthy, furthermore, moreover, additionally, nevertheless, subsequently, world-class, state-of-the-art, best-in-class, revolutionize, results-driven, proven track record.

**Never use these phrases:** I hope this finds you well, I'm writing to, I came across, reach out, I'd love to connect, expand my network, look forward to hearing, please find attached, don't hesitate, feel free to, at your earliest convenience, in today's fast-paced, at the intersection of, deep dive, your expertise, your insights, mutually beneficial, I wanted to take a moment.

**Never use these characters:** em dash (—), en dash (–), semicolon, curly quotes, the "…" character, emojis, more than one "!". Use a comma or a full stop instead of a dash.

**Avoid these LLM habits** (no checker can catch them all, so reread for them):
- **"Not just X, but Y"** and "It's not about X, it's about Y".
- **Groups of three** in every sentence ("fast, reliable and scalable"). One strong detail beats three vague ones.
- **Empty praise.** Every compliment names one real thing: a feature, a doc page, a design choice.
- **A summing-up line at the end** ("All in all...", "In short..."). Say the thing, then stop.
- **Build-up before the point.** The first sentence already says something real.
- **Rhetorical questions** ("Ever wondered why...?").
- **Over-politeness and over-thanking.** One "thanks" at most.
- **Every sentence the same length and shape.** Mix short and medium.
- **The same opening every time.** Don't start every note with "Hi X, saw/noticed...". Lead with their post, their product, or a plain observation.
- **Needy lines:** "any opportunity", "please consider me", "open to work", "looking for a role", "new opportunities". They write because the work is interesting, never because they need something.

## 3. Resume text

The resume follows sections 1 and 2, with a resume's own shape:
- No first person (no I, my, we). Start each bullet with a plain past-tense verb: Built, Added, Moved, Cut, Wrote, Replaced. (The current job may use present tense.)
- One accomplishment per bullet, one or two short sentences, never over 30 words each: **what they built, for whom, and the result with a real number**.
- Plain words a hiring manager reads in one pass. Tools are named only where that project used them, without keyword stuffing.
- No "ensuring...", "resulting in...", "which led to..." tails that pile clauses onto one sentence. Split it or cut it.
- Checked by `python .claude/skills/custom-resume/scripts/build_resume.py --lint "<bullet>"`, and the build refuses text that fails.

## 4. Email closing and signature

Every email (job applications, product outreach, any other email saved as a Gmail draft) ends the same way:

```
<closing>,
[Gmail default signature]
```

- **Signature: always Gmail's default signature.** Gmail adds it when Compose opens. Claude never types their name, links, phone or a signature block by hand, never edits or deletes the default signature, and types the body above it. In the `.md` file, the line `[Gmail default signature]` marks where it goes. If Compose shows no signature, stop and ask the user to set one (Gmail Settings → General → Signature → "For new emails use"). Don't type one instead.
- **Closing: one line, chosen for the recipient's culture.** In this order:
  1. **How they sign themselves** (their emails, posts, newsletters). A founder who signs "Cheers" can get "Cheers," or "Best,".
  2. **The company's tone:** a casual startup gets the lighter closing, a formal or enterprise company the more formal one.
  3. **Their country**, as the default:

| Country / region | Closing |
|---|---|
| USA, Canada | `Best,` |
| UK, Ireland | `Kind regards,` or `Best wishes,` |
| Australia, New Zealand | `Cheers,` (only if their own tone is casual) or `Best,` |
| Netherlands, Nordics, Estonia, Israel | `Best,` |
| Germany, Austria, Switzerland | `Best regards,` |
| France, Italy, Spain, Portugal, Belgium | `Best regards,` or `Kind regards,` |
| Poland, Czechia, rest of Central/Eastern Europe | `Best regards,` |
| Singapore, Hong Kong, Taiwan | `Best regards,` |
| Japan, South Korea | `Best regards,` |
| UAE, Qatar | `Kind regards,` |
| Unknown | `Best regards,` |

  Allowed closings: `Best,` `Best regards,` `Kind regards,` `Regards,` `Best wishes,` `Cheers,` `Thanks,` `Many thanks,`. Never "Yours faithfully", "Yours sincerely", "Respectfully", "Warmest regards" or anything longer. Note the chosen closing and why in the review.
- **Not emails:** cover letters (text box or PDF) have no Gmail signature, so they end with the closing and then their `preferred_name` from profile.json on the next line (the full name, never just the first name). LinkedIn notes, DMs and in-site messages have no closing block.

## 5. The tests before anything is shown to the user

1. **Checker.** It must print `ok`:
   - emails: `python .claude/skills/job-apply-shared/scripts/apply.py email <email.md>` (add `--paras 4` for product outreach)
   - everything else (cover letters, DMs, notes, form answers, subjects, profile text, follow-ups): `python .claude/skills/job-apply-shared/scripts/apply.py text "<text>"`
   - LinkedIn connection notes: `python linkedin/scripts/ledger.py <track> lint "<note>"` (the same word check plus the 300-character limit)
   - resume bullets and project descriptions: `build_resume.py --lint "<text>"` (the same word check plus the resume rules)

   On `REWRITE`, rewrite the sentence in plainer words. Don't just swap in a synonym.
2. **Read it aloud in your head.** If it sounds like a LinkedIn post, a press release, a cover-letter template or a chatbot, rewrite it.
3. **Swap test.** Put another person's name and company in. If it still works, it's too generic. Rewrite it or skip that person.
4. **Phone test.** Would a busy founder understand it in one read on a phone, without rereading a sentence? If not, shorten it.

## Example

Too LLM:
> I hope this message finds you well. I came across Superlog and was truly impressed by your innovative approach to observability. As a passionate engineer with a proven track record, I'd love to connect and explore how we might collaborate.

Human:
> Hi Arseniy, I tried Superlog today and the Discord template failed to connect on the first try. I built alerting for a monitoring platform 200+ teams use, so this part of your product is close to my own work. Glad to connect.
