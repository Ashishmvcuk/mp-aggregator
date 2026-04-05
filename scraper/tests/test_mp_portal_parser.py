from __future__ import annotations

from parsers.mp_portal_parser import MpPortalParser


def test_mp_portal_classifies_buckets() -> None:
    html = """
    <html><body>
    <a href="/result.aspx">Semester Result 2024</a>
    <a href="/news/notice.pdf">University Notice</a>
    <a href="/admit.pdf">Download Admit Card</a>
    <a href="/jobs.html">Faculty Recruitment 2026</a>
    <a href="/syllabus.pdf">Syllabus B.Tech</a>
    <a href="/blog/post">Editorial blog post title here</a>
    </body></html>
    """
    p = MpPortalParser()
    out = p.parse(html, "Test University", "https://univ.example.edu/")
    assert len(out["results"]) >= 1
    assert len(out["news"]) >= 1
    assert len(out["admit_cards"]) >= 1
    assert len(out["jobs"]) >= 1
    assert len(out["syllabus"]) >= 1
    assert len(out["blogs"]) >= 1
