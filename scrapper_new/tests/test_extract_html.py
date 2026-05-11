from scrapper_new.extract import extract_from_html


def test_extract_picks_anchor_with_date_in_row():
    html = """
    <html><body><table>
    <tr><td>15-04-2026</td><td><a href="/results/ug.pdf">UG Result declared</a></td></tr>
    </table></body></html>
    """
    items = extract_from_html(
        html,
        source_page_url="https://univ.example.edu/news/",
        university="Example University",
        content_kind_hint="news",
    )
    urls = {i.url for i in items}
    assert any("univ.example.edu/results/ug.pdf" in u for u in urls)
    any_ok = any(i.title for i in items if "UG Result" in i.title)
    assert any_ok
