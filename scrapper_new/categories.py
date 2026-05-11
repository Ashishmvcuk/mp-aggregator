"""Map URL roles and text hints to content_kind and website category buckets."""

from __future__ import annotations

import re
# Order when the same URL appears under multiple fields (first wins).
SOURCE_FIELD_PRIORITY: tuple[str, ...] = (
    "results_url",
    "time_table_url",
    "admit_card_url",
    "scheme_syllabus_url",
    "news_url",
    "website",
    "student_login_url",
    "extra_urls",
)

FIELD_TO_KIND: dict[str, str] = {
    "website": "other",
    "time_table_url": "timetable",
    "results_url": "result",
    "news_url": "news",
    "admit_card_url": "admit_card",
    "student_login_url": "other",
    "scheme_syllabus_url": "syllabus",
    "extra_urls": "other",
}


def kind_to_website_category(kind: str) -> str:
    """Map rich content_kind to one of seven site buckets."""
    k = (kind or "other").lower()
    if k == "result":
        return "results"
    if k in ("timetable", "admit_card"):
        return "admit_cards"
    if k == "syllabus":
        return "syllabus"
    if k in ("admission", "exam_form"):
        return "enrollments"
    if k == "job":
        return "jobs"
    if k == "other":
        return "news"
    if k == "news":
        return "news"
    return "news"


_VALID_KINDS = frozenset(
    {
        "result",
        "timetable",
        "news",
        "admit_card",
        "admission",
        "syllabus",
        "exam_form",
        "job",
        "other",
    }
)


def refine_content_kind(
    hint: str,
    title: str,
    link_url: str,
) -> str:
    """Adjust hint using URL and title keywords."""
    low_t = (title or "").lower()
    low_u = (link_url or "").lower()
    blob = f"{low_t} {low_u}"

    if re.search(r"\b(result|revaluation|mark\s*sheet|score\s*card)\b", blob):
        return "result"
    if re.search(r"\b(time\s*table|timetable|date\s*sheet|exam\s*schedule)\b", blob):
        return "timetable"
    if re.search(r"\b(admit\s*card|hall\s*ticket)\b", blob):
        return "admit_card"
    if re.search(r"\b(syllabus|scheme|curriculum)\b", blob):
        return "syllabus"
    if re.search(r"\b(admission|enroll|prospectus|entrance|exam\s*form|application\s*form)\b", blob):
        if "form" in blob or "application" in blob:
            return "exam_form"
        return "admission"
    if re.search(r"\b(job|recruitment|vacancy|career)\b", blob):
        return "job"

    h = (hint or "other").lower()
    return h if h in _VALID_KINDS else "other"
