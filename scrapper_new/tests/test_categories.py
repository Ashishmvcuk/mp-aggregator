from scrapper_new.categories import kind_to_website_category, refine_content_kind


def test_kind_to_website_category():
    assert kind_to_website_category("result") == "results"
    assert kind_to_website_category("timetable") == "admit_cards"
    assert kind_to_website_category("syllabus") == "syllabus"
    assert kind_to_website_category("job") == "jobs"
    assert kind_to_website_category("other") == "news"


def test_refine_from_text():
    assert refine_content_kind("other", "UG Time Table Dec 2026", "https://x/timetable") == "timetable"
    assert refine_content_kind("other", "Semester result", "https://x/result.pdf") == "result"
