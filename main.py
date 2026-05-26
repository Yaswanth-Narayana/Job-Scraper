#!/usr/bin/env python3
"""
main.py  –  Entry point for the Job Automation Script.

Flow:
  1. Scrape jobs from LinkedIn, Indeed, Naukri
  2. Score each job against your resume (via Claude AI)
  3. Filter jobs above MIN_MATCH_PCT threshold
  4. Email matched jobs + apply links to your Gmail
  5. Save full results to results.json

Usage:
  python main.py
"""

import json
import logging
import sys
from datetime import datetime
from pathlib  import Path

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("job_automation.log"),
    ],
)
log = logging.getLogger(__name__)


def main():
    log.info("=" * 60)
    log.info("   JOB AUTOMATION SCRIPT  –  %s", datetime.now().strftime("%d %b %Y %I:%M %p"))
    log.info("=" * 60)

    # ── Import here so config errors surface immediately ─────
    from config   import (RESUME_TEXT, ENABLE_LINKEDIN, ENABLE_INDEED,
                          ENABLE_NAUKRI, MIN_MATCH_PCT, JOB_KEYWORDS,
                          JOB_LOCATION, ANTHROPIC_API_KEY, GMAIL_SENDER)
    from scrapers import scrape_linkedin, scrape_indeed, scrape_naukri
    from matcher  import filter_jobs
    from emailer  import send_email

    # ── Validate config ──────────────────────────────────────
    if "PASTE YOUR FULL RESUME" in RESUME_TEXT:
        log.error("❌  Please add your resume text to config.py (RESUME_TEXT).")
        sys.exit(1)
    if "your_anthropic_api_key" in ANTHROPIC_API_KEY:
        log.warning("⚠️  No Anthropic API key set – falling back to keyword matching.")
    if "your_email" in GMAIL_SENDER:
        log.warning("⚠️  Gmail not configured – results will be saved to file only.")

    # ── Step 1: Scrape ───────────────────────────────────────
    all_jobs: list[dict] = []

    if ENABLE_LINKEDIN:
        log.info("🔍 Scraping LinkedIn …")
        jobs = scrape_linkedin()
        log.info("   LinkedIn → %d jobs found", len(jobs))
        all_jobs.extend(jobs)

    if ENABLE_INDEED:
        log.info("🔍 Scraping Indeed …")
        jobs = scrape_indeed()
        log.info("   Indeed → %d jobs found", len(jobs))
        all_jobs.extend(jobs)

    if ENABLE_NAUKRI:
        log.info("🔍 Scraping Naukri …")
        jobs = scrape_naukri()
        log.info("   Naukri → %d jobs found", len(jobs))
        all_jobs.extend(jobs)

    # De-duplicate by apply_url
    seen, unique_jobs = set(), []
    for j in all_jobs:
        url = j.get("apply_url", "")
        if url and url not in seen:
            seen.add(url)
            unique_jobs.append(j)

    log.info("📦 Total unique jobs scraped: %d", len(unique_jobs))

    if not unique_jobs:
        log.warning("No jobs scraped. Check internet connection or try different keywords.")
        sys.exit(0)

    # ── Step 2 & 3: Score + Filter ───────────────────────────
    log.info("🤖 Scoring jobs against your resume (min match: %d%%) …", MIN_MATCH_PCT)
    matched_jobs = filter_jobs(unique_jobs, RESUME_TEXT)

    log.info("✅ %d / %d jobs passed the %d%% threshold",
             len(matched_jobs), len(unique_jobs), MIN_MATCH_PCT)

    # ── Step 4: Save results ─────────────────────────────────
    output_file = Path("results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at":  datetime.now().isoformat(),
            "keywords":      JOB_KEYWORDS,
            "location":      JOB_LOCATION,
            "total_scraped": len(unique_jobs),
            "total_matched": len(matched_jobs),
            "min_match_pct": MIN_MATCH_PCT,
            "jobs":          matched_jobs,
        }, f, indent=2, ensure_ascii=False)
    log.info("💾 Results saved to %s", output_file)

    # ── Step 5: Print summary ────────────────────────────────
    if matched_jobs:
        log.info("")
        log.info("── TOP MATCHES ─────────────────────────────────────────")
        for j in matched_jobs[:10]:
            log.info("  %3d%%  %-45s  %s  (%s)",
                     j["match_pct"], j["title"][:45],
                     j["company"][:25], j["source"])
        log.info("────────────────────────────────────────────────────────")

    # ── Step 6: Email ────────────────────────────────────────
    if "your_email" not in GMAIL_SENDER:
        log.info("📧 Sending email …")
        send_email(matched_jobs)
    else:
        log.info("📧 Email skipped (configure GMAIL_SENDER in config.py).")
        log.info("   Open results.json to review matched jobs.")

    log.info("🏁 Done!")


if __name__ == "__main__":
    main()
