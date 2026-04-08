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
    <a href="/pg-admission.pdf">PG Admission prospectus 2026</a>
    </body></html>
    """
    p = MpPortalParser()
    out = p.parse(html, "Test University", "https://univ.example.edu/")
    assert len(out["results"]) >= 1
    assert len(out["news"]) >= 1
    assert len(out["admit_cards"]) >= 1
    assert len(out["enrollments"]) >= 1
    assert len(out["jobs"]) >= 1
    assert len(out["syllabus"]) >= 1
    assert len(out["blogs"]) >= 1


def test_mp_portal_table_row_ddmon_date() -> None:
    """IGNTU-style admission table: date in first column, link in row."""
    html = """
    <html><body><table>
    <tr>
      <td>05Jan</td>
      <td><a href="/apply-ug">Notification CUET (UG) Admission 2026</a></td>
    </tr>
    <tr>
      <td>16Dec</td>
      <td><a href="/apply-pg">Notification CUET (PG) Admission 2026</a></td>
    </tr>
    </table></body></html>
    """
    p = MpPortalParser()
    out = p.parse(html, "IGNTU", "https://igntu.ac.in/admission")
    enr = {item["url"]: item["date"] for item in out["enrollments"]}
    assert enr["https://igntu.ac.in/apply-ug"] == "2026-01-05"
    assert enr["https://igntu.ac.in/apply-pg"] == "2025-12-16"


def test_mp_portal_skips_bus_feedback_urls() -> None:
    html = """
    <html><body>
    <a href="https://x.example/BusPortal/x">Online Bus Portal</a>
    <a href="https://x.example/FeedBack_Home.aspx">Feedback</a>
    <a href="https://x.example/admission.aspx">Admission</a>
    </body></html>
    """
    p = MpPortalParser()
    out = p.parse(html, "U", "https://x.example/")
    urls = [x["url"] for x in out["enrollments"]]
    assert not any("BusPortal" in u for u in urls)
    assert not any("FeedBack" in u for u in urls)
    assert any("admission" in u for u in urls)
