# 🎯 Job Automation Script

Automatically scrapes **LinkedIn**, **Indeed**, and **Naukri** for Software Engineer jobs,
scores each against your resume using **Claude AI**, and emails you only the best matches.

---

## 📁 File Structure

```
job_automation/
├── config.py          ← ✏️  ALL your settings go here
├── main.py            ← ▶️  Run this
├── scrapers.py        ← LinkedIn / Indeed / Naukri scrapers
├── matcher.py         ← AI-powered resume ↔ JD matching
├── emailer.py         ← Gmail HTML email sender
├── requirements.txt   ← Python dependencies
└── results.json       ← Created after each run (full match report)
```

---

## ⚡ Quick Setup (5 minutes)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Edit `config.py`

Open `config.py` and fill in **all** the fields:

| Field | What to put |
|---|---|
| `JOB_KEYWORDS` | e.g. `"Python Developer"`, `"Full Stack Engineer"` |
| `JOB_LOCATION` | e.g. `"Bengaluru"`, `"Remote"`, `"Mumbai"` |
| `MAX_PAGES` | Pages per platform (3 = ~75 LinkedIn jobs, ~30 Indeed) |
| `MIN_MATCH_PCT` | Email threshold — default `40` |
| `RESUME_TEXT` | Paste your **full** resume as plain text |
| `ANTHROPIC_API_KEY` | Get free at https://console.anthropic.com |
| `GMAIL_SENDER` | Your Gmail address |
| `GMAIL_PASSWORD` | **App Password** (see below) |
| `NOTIFY_EMAIL` | Where to receive match emails (can be same as sender) |

### 3. Get a Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (required)
3. Go to https://myaccount.google.com/apppasswords
4. Create an app password → copy the 16-character code
5. Paste it as `GMAIL_PASSWORD` in `config.py`

> ⚠️ Do NOT use your normal Gmail password — it won't work.

### 4. Get an Anthropic API Key (optional but recommended)

1. Sign up at https://console.anthropic.com
2. Create an API key
3. Paste as `ANTHROPIC_API_KEY` in `config.py`

> Without a key the script falls back to simple keyword matching (less accurate).

---

## ▶️ Run

```bash
cd job_automation
python main.py
```

### What happens:
1. Scrapes LinkedIn + Indeed + Naukri for your keywords
2. Fetches job descriptions for each listing
3. Sends each JD to Claude AI for resume matching
4. Filters jobs ≥ your `MIN_MATCH_PCT`
5. Emails a formatted HTML report with **Apply Now** buttons
6. Saves `results.json` with the full data

---

## 📧 Sample Email Output

You'll receive an email like:

```
🎯 7 Job Match(es) Found — 26 May 2026

[92%] Senior Python Developer @ Flipkart (Naukri)
      ✅ Matched: python, django, aws, docker, postgresql
      ⚠️  Missing: kafka
      [Apply Now →]

[78%] Backend Engineer @ Razorpay (LinkedIn)
      ✅ Matched: python, fastapi, redis, kubernetes
      ⚠️  Missing: go
      [Apply Now →]
...
```

---

## 🔧 Customisation

### Change search filters

In `scrapers.py`:
- LinkedIn: add `"f_E": "2"` to params for Mid-Senior level only
- Indeed: change `"fromage": "1"` to `"7"` for last 7 days
- Naukri: add `"experience": "3-6"` to params for experience range

### Schedule automatic daily runs

**Linux / Mac (cron):**
```bash
# Run every morning at 8 AM
0 8 * * * cd /path/to/job_automation && python main.py
```

**Windows (Task Scheduler):**
- Action: `python C:\path\to\job_automation\main.py`
- Trigger: Daily at 8:00 AM

---

## ⚠️ Notes & Limitations

- **LinkedIn / Indeed** may block scrapers occasionally — the script retries automatically.
  If scraping fails repeatedly, try running with a VPN or reduce `MAX_PAGES`.
- **Naukri** uses a public JSON API so it is the most reliable.
- This script is for **personal, non-commercial use**. Always respect robots.txt and site ToS.
- Job apply links may require an account login on the destination site.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `SMTPAuthenticationError` | Use App Password, not your Gmail password |
| `0 jobs scraped` | Try different `JOB_LOCATION` / `JOB_KEYWORDS` or increase `MAX_PAGES` |
| JSON parse error | API key may be invalid or quota exceeded |
| Import error | Run `pip install -r requirements.txt` |
