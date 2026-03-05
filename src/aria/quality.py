from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from aria.db import Repo


@dataclass(frozen=True)
class QualityResult:
    score: float
    details: dict


def _contains_heading(markdown: str, heading: str) -> bool:
    pattern = rf"(?im)^\s*#{{1,3}}\s*{re.escape(heading)}\s*$"
    return re.search(pattern, markdown) is not None


def _contains_code_block(markdown: str) -> bool:
    return "```" in markdown


def _word_count(markdown: str) -> int:
    words = re.findall(r"\b[\w-]+\b", markdown)
    return len(words)


def score_content(markdown: str) -> QualityResult:
    sections = [
        "Why this matters",
        "Step-by-step implementation",
        "Metrics to track",
        "Pitfalls",
        "Next action",
    ]
    details = {
        "word_count": _word_count(markdown),
        "has_h1": bool(re.search(r"(?m)^\s*#\s+\S+", markdown)),
        "has_code_block": _contains_code_block(markdown),
        "sections_present": [s for s in sections if _contains_heading(markdown, s)],
    }
    score = 0.0
    if details["has_h1"]:
        score += 20
    score += 40 * (len(details["sections_present"]) / len(sections))
    if details["has_code_block"]:
        score += 20
    if details["word_count"] >= 250:
        score += 20
    return QualityResult(score=round(score, 2), details=details)


def score_growth(markdown: str) -> QualityResult:
    sections = [
        "Goal",
        "Hypothesis",
        "Experiment design",
        "Instrumentation & metrics",
        "Risks and mitigations",
        "What to do next based on outcomes",
    ]
    details = {
        "word_count": _word_count(markdown),
        "sections_present": [s for s in sections if _contains_heading(markdown, s)],
    }
    score = 100 * (len(details["sections_present"]) / len(sections))
    if details["word_count"] < 120:
        score *= 0.8
    return QualityResult(score=round(score, 2), details=details)


def score_feedback(markdown: str) -> QualityResult:
    sections = [
        "Problem observed",
        "Who it impacts",
        "Reproduction steps",
        "Recommended product improvement",
        "Expected impact",
        "Evidence to collect",
    ]
    has_severity = re.search(r"(?im)^severity\s*:\s*(high|medium|low)\s*$", markdown) is not None
    details = {
        "word_count": _word_count(markdown),
        "has_severity": has_severity,
        "sections_present": [s for s in sections if _contains_heading(markdown, s)],
    }
    score = 0.0
    if has_severity:
        score += 20
    score += 80 * (len(details["sections_present"]) / len(sections))
    return QualityResult(score=round(score, 2), details=details)


def score_markdown(artifact_type: str, markdown: str) -> QualityResult:
    key = artifact_type.strip().lower()
    if key == "content":
        return score_content(markdown)
    if key == "growth":
        return score_growth(markdown)
    if key == "feedback":
        return score_feedback(markdown)
    return QualityResult(score=0.0, details={"error": f"unsupported artifact_type={artifact_type}"})


def score_file(repo: Repo, *, artifact_type: str, artifact_path: Path) -> QualityResult:
    markdown = artifact_path.read_text(encoding="utf-8")
    result = score_markdown(artifact_type, markdown)
    repo.add_quality_score(
        artifact_type=artifact_type,
        artifact_path=str(artifact_path),
        score=result.score,
        details=result.details,
    )
    return result
