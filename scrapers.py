"""
scrapers.py  –  Lightweight scrapers for LinkedIn, Indeed, Naukri.

Each scraper returns a list of dicts:
  {
    "title":       str,
    "company":     str,
    "location":    str,
    "description": str,
    "apply_url":   str,
    "source":      str,   # "LinkedIn" | "Indeed" | "Naukri"
  }

Note: These scrapers use public search-result pages (no login required).
      For LinkedIn / Indeed deep links an account may be needed; the script
      gracefully skips jobs where the description cannot be fetched.
"""

import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from config import JOB_KEYWORDS, JOB_LOCATION, MAX_PAGES

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def _get(url: str, params=None, timeout=15) -> requests.Response | None:
    """Safe GET with retries."""
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            log.warning("GET %s attempt %d failed: %s", url, attempt + 1, e)
            time.sleep(2 ** attempt)
    return None


def _random_sleep(lo=1.5, hi=3.5):
    time.sleep(random.uniform(lo, hi))


# ─────────────────────────────────────────────────────────────
#  LinkedIn
# ─────────────────────────────────────────────────────────────
def scrape_linkedin() -> list[dict]:
    jobs = []
    base = "https://www.linkedin.com/jobs/search"

    for page in range(MAX_PAGES):
        params = {
            "keywords": JOB_KEYWORDS,
            "location": JOB_LOCATION,
            "start":    page * 25,
            "f_TPR":    "r86400",   # last 24 h  (remove for all time)
        }
        resp = _get(base, params=params)
        if not resp:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.base-card")
        if not cards:
            break

        for card in cards:
            title_tag   = card.select_one("h3.base-search-card__title")
            company_tag = card.select_one("h4.base-search-card__subtitle")
            loc_tag     = card.select_one("span.job-search-card__location")
            link_tag    = card.select_one("a.base-card__full-link")

            if not (title_tag and link_tag):
                continue

            apply_url = link_tag["href"].split("?")[0]
            desc      = _fetch_linkedin_desc(apply_url)

            jobs.append({
                "title":       title_tag.get_text(strip=True),
                "company":     company_tag.get_text(strip=True) if company_tag else "N/A",
                "location":    loc_tag.get_text(strip=True)     if loc_tag     else JOB_LOCATION,
                "description": desc,
                "apply_url":   apply_url,
                "source":      "LinkedIn",
            })
            _random_sleep()

        log.info("LinkedIn page %d → %d jobs collected", page + 1, len(jobs))
        _random_sleep(2, 4)

    return jobs


def _fetch_linkedin_desc(url: str) -> str:
    resp = _get(url)
    if not resp:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    div  = soup.select_one("div.description__text") or soup.select_one("div.show-more-less-html")
    return div.get_text(" ", strip=True)[:4000] if div else ""


# ─────────────────────────────────────────────────────────────
#  Indeed
# ─────────────────────────────────────────────────────────────
def scrape_indeed() -> list[dict]:
    jobs  = []
    base  = "https://www.indeed.com/jobs"

    for page in range(MAX_PAGES):
        params = {
            "q":    JOB_KEYWORDS,
            "l":    JOB_LOCATION,
            "start": page * 10,
            "fromage": "1",   # last 1 day  (remove for all time)
        }
        resp = _get(base, params=params)
        if not resp:
            break

        soup  = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.job_seen_beacon") or soup.select("div.tapItem")
        if not cards:
            break

        for card in cards:
            title_tag   = card.select_one("h2.jobTitle span")
            company_tag = card.select_one("span.companyName")
            loc_tag     = card.select_one("div.companyLocation")
            link_tag    = card.select_one("a[id^='job_']") or card.select_one("a.jcs-JobTitle")

            if not (title_tag and link_tag):
                continue

            href      = link_tag.get("href", "")
            apply_url = f"https://www.indeed.com{href}" if href.startswith("/") else href
            desc      = _fetch_indeed_desc(apply_url)

            jobs.append({
                "title":       title_tag.get_text(strip=True),
                "company":     company_tag.get_text(strip=True) if company_tag else "N/A",
                "location":    loc_tag.get_text(strip=True)     if loc_tag     else JOB_LOCATION,
                "description": desc,
                "apply_url":   apply_url,
                "source":      "Indeed",
            })
            _random_sleep()

        log.info("Indeed page %d → %d jobs collected", page + 1, len(jobs))
        _random_sleep(2, 4)

    return jobs


def _fetch_indeed_desc(url: str) -> str:
    resp = _get(url)
    if not resp:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    div  = soup.select_one("div#jobDescriptionText") or soup.select_one("div.jobsearch-JobComponent-description")
    return div.get_text(" ", strip=True)[:4000] if div else ""


# ─────────────────────────────────────────────────────────────
#  Naukri
# ─────────────────────────────────────────────────────────────
def scrape_naukri() -> list[dict]:
    """
    Naukri exposes a public JSON API used by its own frontend.
    This hits the same endpoint with no login required.
    """
    jobs = []
    base = "https://www.naukri.com/jobapi/v3/search"

    keyword_slug = JOB_KEYWORDS.replace(" ", "-").lower()
    location_slug = JOB_LOCATION.replace(" ", "-").lower()

    for page in range(1, MAX_PAGES + 1):
        params = {
            "noOf":       20,
            "urlType":    "search_by_keyword",
            "searchType": "adv",
            "keyword":    JOB_KEYWORDS,
            "location":   JOB_LOCATION,
            "pageNo":     page,
            "k":          keyword_slug,
            "l":          location_slug,
        }
        headers = {**HEADERS, "appid": "109", "systemid": "109"}
        try:
            resp = requests.get(base, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            log.warning("Naukri page %d error: %s", page, e)
            break

        job_list = data.get("jobDetails", [])
        if not job_list:
            break

        for j in job_list:
            title    = j.get("title", "N/A")
            company  = j.get("companyName", "N/A")
            location = ", ".join(j.get("placeholders", [{}])[0].get("label", JOB_LOCATION)
                                 for _ in [1])
            jd_url   = j.get("jdURL", "")
            apply_url = f"https://www.naukri.com{jd_url}" if jd_url.startswith("/") else jd_url
            desc      = _fetch_naukri_desc(apply_url)

            jobs.append({
                "title":       title,
                "company":     company,
                "location":    location,
                "description": desc,
                "apply_url":   apply_url,
                "source":      "Naukri",
            })
            _random_sleep(0.8, 2)

        log.info("Naukri page %d → %d jobs collected", page, len(jobs))
        _random_sleep(2, 4)

    return jobs


def _fetch_naukri_desc(url: str) -> str:
    resp = _get(url)
    if not resp:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    div  = (soup.select_one("div.dang-inner-html")
            or soup.select_one("section.job-desc")
            or soup.select_one("div#job_description"))
    return div.get_text(" ", strip=True)[:4000] if div else ""
