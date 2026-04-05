from __future__ import annotations

from utils.title_refine import refine_link_title


def test_refine_takes_first_segment_before_pipe() -> None:
    long = (
        "Main Examination Result 2024 Declared | "
        "Students are advised to check their marksheet and contact the controller of examinations for revaluation"
    )
    out = refine_link_title(long, "results", "https://example.com/result.aspx")
    assert "|" not in out
    assert len(out) <= 130
    assert "Main Examination" in out or "Result" in out


def test_refine_results_snippet_around_keyword() -> None:
    blob = (
        "Welcome to our portal today we announce that the semester result for UG programs "
        "is now available please visit the student section"
    )
    out = refine_link_title(blob, "results", "")
    assert "result" in out.lower()
    assert len(out) < len(blob)


def test_refine_prefix_click_here() -> None:
    out = refine_link_title("Click here to view examination result", "results", "")
    assert not out.lower().startswith("click here")
    assert "result" in out.lower()
