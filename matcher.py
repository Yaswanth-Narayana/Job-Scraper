"""
matcher.py  –  Uses Claude (claude-sonnet-4-20250514) to score
               how well a job description matches the resume.

Returns:
  {
    "match_pct":  int,        # 0-100
    "matched_skills": list,   # skills found in both JD and resume
    "missing_skills": list,   # skills in JD but not in resume
    "summary":    str,        # 2-sentence explanation
  }
"""

import json
import logging
import requests
from config import ANTHROPIC_API_KEY, MIN_MATCH_PCT

log = logging.getLogger(__name__)

_API_URL = "https://api.anthropic.com/v1/messages"
_HEADERS  = {
    "x-api-key":         ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type":      "application/json",
}

_SYSTEM = """You are a professional technical recruiter and resume expert.
Given a RESUME and a JOB DESCRIPTION, respond ONLY with a valid JSON object
(no markdown, no extra text) in this exact format:
{
  "match_pct":       <integer 0-100>,
  "matched_skills":  [<string>, ...],
  "missing_skills":  [<string>, ...],
  "summary":         "<2-sentence plain-English explanation>"
}

Scoring rubric:
  90-100  – Near perfect fit; almost all required skills present
  70-89   – Strong match; minor gaps
  50-69   – Moderate match; some important skills missing
  30-49   – Weak match; significant skill gaps
  0-29    – Poor fit
"""


def score_job(resume_text: str, job: dict) -> dict:
    """Call Claude to score a single job against the resume."""
    prompt = (
        f"RESUME:\n{resume_text.strip()}\n\n"
        f"JOB TITLE: {job['title']} at {job['company']}\n"
        f"SOURCE: {job['source']}\n\n"
        f"JOB DESCRIPTION:\n{job['description'][:3000].strip()}"
    )

    payload = {
        "model":      "claude-sonnet-4-20250514",
        "max_tokens": 600,
        "system":     _SYSTEM,
        "messages":   [{"role": "user", "content": prompt}],
    }

    try:
        resp = requests.post(_API_URL, headers=_HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        raw  = data["content"][0]["text"].strip()

        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        return result

    except json.JSONDecodeError as e:
        log.warning("JSON parse error for '%s': %s", job["title"], e)
        return _fallback_score(resume_text, job)
    except Exception as e:
        log.error("Claude API error for '%s': %s", job["title"], e)
        return _fallback_score(resume_text, job)


def _fallback_score(resume_text: str, job: dict) -> dict:
    """
    Simple keyword-overlap score used when the API call fails.
    Not as accurate as Claude but never crashes.
    """
    import re

    def tokens(text):
        return set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]*\b', text.lower()))

    TECH_KEYWORDS = {
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "react", "angular", "vue", "node", "django", "flask", "fastapi", "spring",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "git",
        "linux", "rest", "graphql", "microservices", "ci/cd", "agile", "scrum",
        "machine learning", "deep learning", "nlp", "data science",
    }

    resume_tok = tokens(resume_text)
    jd_tok     = tokens(job.get("description", ""))

    jd_tech  = jd_tok  & TECH_KEYWORDS
    matched  = resume_tok & jd_tech
    missing  = jd_tech  - resume_tok

    pct = int(len(matched) / max(len(jd_tech), 1) * 100) if jd_tech else 30

    return {
        "match_pct":      min(pct, 100),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "summary":        (
            f"Keyword-based fallback score (API unavailable). "
            f"Found {len(matched)} of {len(jd_tech)} required technical skills."
        ),
    }


def filter_jobs(jobs: list[dict], resume_text: str) -> list[dict]:
    """Score every job and return only those above MIN_MATCH_PCT."""
    results = []
    total   = len(jobs)

    for i, job in enumerate(jobs, 1):
        if not job.get("description"):
            log.info("[%d/%d] Skipped (no description): %s", i, total, job["title"])
            continue

        log.info("[%d/%d] Scoring: %s @ %s", i, total, job["title"], job["company"])
        score = score_job(resume_text, job)
        pct   = score.get("match_pct", 0)

        log.info("  → %d%% match | matched: %s | missing: %s",
                 pct,
                 ", ".join(score.get("matched_skills", [])[:5]),
                 ", ".join(score.get("missing_skills", [])[:5]))

        if pct >= MIN_MATCH_PCT:
            job["match_pct"]      = pct
            job["matched_skills"] = score.get("matched_skills", [])
            job["missing_skills"] = score.get("missing_skills", [])
            job["match_summary"]  = score.get("summary", "")
            results.append(job)

    results.sort(key=lambda x: x["match_pct"], reverse=True)
    return results
