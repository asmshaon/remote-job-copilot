# Application form answers

Answers Claude may type into job application forms for this person. Anything marked `ASK` is asked in chat the first
time a form needs it, then the answer is saved here (with the date). Claude never guesses these.

## Contact

- Full name: ASK (same as `full_name` in profile.json)
- Preferred name: ASK
- Email sign-off: a closing chosen for the recipient's culture (`Best,`, `Best regards,`, `Kind regards,`, `Regards,`...; see [HUMAN-WRITING.md](../../.claude/skills/job-apply-shared/HUMAN-WRITING.md) section 4), then **the Gmail default signature**, which Gmail adds on Compose. Never type the name or links under an email by hand.
- Sign-off name where there is no Gmail signature (cover letters): the same closing, then the **full preferred name** on the next line. Never just the first name.
- Email: ASK
- Phone: read `others/contacts/phone.txt` in this folder. **Never copy the number into any saved or committed file**; write "(from phone.txt)" instead.
- LinkedIn: ASK
- Portfolio / website: ASK
- GitHub: ASK
- Location (city, country): from the address file below (city + country only when a form just asks for location)
- Full postal address: read `others/address/address.txt` in this folder and type it field by field (street, city, postal code, country). **Never copy the address into any saved or committed file**; write "(from address.txt)" instead.
- Profile photo: the image in `profile-picture/`. Upload it only when the form asks for a photo or avatar.
- Time zone: ASK (same as `timezone_label` in profile.json)

## Work

- Current title: ASK
- Current company: ASK
- Years of professional experience: ASK
- Years with their main language or framework: ASK
- Highest education: ASK
- University grade: ASK
- High school grades: ASK

## Eligibility and terms

- Work authorization: ASK
- Requires visa sponsorship: ASK
- Open to working as a contractor (e.g. via Deel, Remote.com): ASK
- Willing to relocate: ASK
- Notice period / earliest start date: ASK
- Salary expectation: the range in profile.json `pay`. For each job, pick one figure inside it from the market analysis (RULES.md Step 1c), close to the job's posted range when it has one. Convert to the form's currency and period (yearly, monthly, hourly at 160 h/month). Never below `pay.min_month`.
- Working hours overlap: ASK

## Upwork

Used by the upwork-profile skill. Never save exact Upwork earnings here.

- Profile: ASK (Job Success Score, reviews, earnings: just whether they exist)
- Hourly rate on Upwork: ASK
- Minimum fixed price for a catalog Starter tier: ASK
- Hours per week available: ASK
- English level (Upwork scale: Basic, Conversational, Fluent, Native or bilingual): ASK
- Profile video: ASK (who records it)
- Public repos that are OK to mention: ASK

## Personal

(answers to odd form questions go here, with the date they were given)

## Diversity / voluntary questions

- Default: "Decline to answer" / "Prefer not to say" unless the person says otherwise.

## How did you hear about us

- LinkedIn
