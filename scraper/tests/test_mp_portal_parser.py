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


def test_mp_portal_extracts_date_from_link_text() -> None:
    """Dates embedded in anchor text (common on portals)."""
    html = """
    <html><body>
    <a href="/result.pdf">Semester result 25-03-2025</a>
    </body></html>
    """
    p = MpPortalParser()
    out = p.parse(html, "Test University", "https://univ.example.edu/")
    assert len(out["results"]) >= 1
    assert out["results"][0]["date"] == "2025-03-25"


def test_mp_portal_gyanveer_row_div_us_mdy_date() -> None:
    """Homepage notices use M/D/Y in a row div before the link (not India D/M/Y)."""
    html = """
    <html><body><li class="list-group-item">
      <div class="row"><div><b>2/12/2026</b></div></div>
      <div><a href="/Pages/NewsLetter.aspx?Type=2&amp;id=163">
        Exam time table 3rd sem M.Sc for the examination session Dec-2025
      </a></div>
    </li></body></html>
    """
    p = MpPortalParser()
    out = p.parse(html, "Gyanveer University", "https://www.gyanveeruniversity.edu.in/")
    urls = {item["url"]: item["date"] for item in out["results"]}
    assert urls["https://www.gyanveeruniversity.edu.in/Pages/NewsLetter.aspx?Type=2&id=163"] == "2026-02-12"


def test_mp_portal_gyanveer_li_leading_us_mdy_date() -> None:
    """Leading M/D/Y on the list item line (marquee / list) before anchor text."""
    html = """
    <html><body><li class="list-group-item">2/12/2026
      <div><a href="/Pages/NewsLetter.aspx?Type=2&amp;id=164">
        Exam time table 3rd sem MA for the examination session Dec-2025
      </a></div>
    </li></body></html>
    """
    p = MpPortalParser()
    out = p.parse(html, "Gyanveer University", "https://www.gyanveeruniversity.edu.in/")
    urls = {item["url"]: item["date"] for item in out["results"]}
    assert urls["https://www.gyanveeruniversity.edu.in/Pages/NewsLetter.aspx?Type=2&id=164"] == "2026-02-12"


def test_mp_portal_notice_cell_dd_mon_yyyy() -> None:
    """Detail-style table: Create dates use 12-Feb-2026 (parse before numeric fragments)."""
    html = """
    <html><body><table><tr>
      <td>12-Feb-2026 12:00 AM Till Date: 31-May-2026 12:00 AM</td>
      <td><a href="/Pages/NewsLetter.aspx?Type=2&amp;id=200">Exam time table PDF</a></td>
    </tr></table></body></html>
    """
    p = MpPortalParser()
    out = p.parse(html, "GU", "https://www.gyanveeruniversity.edu.in/")
    urls = {item["url"]: item["date"] for item in out["results"]}
    assert urls["https://www.gyanveeruniversity.edu.in/Pages/NewsLetter.aspx?Type=2&id=200"] == "2026-02-12"


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
