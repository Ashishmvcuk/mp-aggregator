#!/usr/bin/env python3
"""Parse ALL MP UNIVERSITY DETAILS_updated.pdf text into JSON (extracted via pypdf)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # type: ignore


def extract_pdf_text(pdf_path: Path) -> str:
    if PdfReader is None:
        raise SystemExit("pypdf is required: pip install pypdf")
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def slice_data_body(text: str) -> str:
    """Keep only the main table rows (drop welcome line and footer links)."""
    end_marker = (
        "2(f)Sr.NoTypeName of the UniversityWEBSITESTIME TABLERESULTS"
        "NEWS & NOTIFICATIONSADMIT CARDSTUDENT LOGINScheme/SyllabusAddressZipstateStatusABC ID"
    )
    start = text.find("1Private")
    end = text.find(end_marker)
    if start == -1 or end == -1:
        raise ValueError("Unexpected PDF layout: could not find data boundaries.")
    return text[start : end + len("2(f)")]


# Path segment: no spaces or commas (comma often starts the address after a glued path)
_URL_HOST_PATH = re.compile(
    r"^(https?://[a-zA-Z0-9.-]+(?:/[^/\s,]*)?)(?:\s+(.+))?$"
)


def strip_pdf_url_artifact(u: str) -> str:
    u = u.rstrip()
    if u.endswith("/Website"):
        return u[: -len("Website")]
    return u


def split_last_url_segment(p: str) -> tuple[str, str]:
    """Split final https segment into URL and address (PDF often omits spaces)."""
    p = p.strip()
    addr_prefix = ""
    # Common PDF glitch: query param merged with place name
    if "SYLLABUSGaram" in p:
        i = p.index("SYLLABUSGaram")
        addr_prefix = p[i + len("SYLLABUS") :].strip()
        p = p[: i + len("SYLLABUS")].strip()
    # Path glued to address: "news-eventsSherGanj, Satna" — split on first aA boundary with a comma ahead
    for mm in re.finditer(r"([a-z0-9])([A-Z][a-z])", p):
        if mm.start() >= 6 and p[mm.start() - 6 : mm.start() + 1].lower() == "website":
            # Skip "Website Bhopal…" false split (last "e" of "Website" + "Bhopal")
            continue
        suf = p[mm.start() + 1 :]
        if "," in suf:
            p = p[: mm.start() + 1].strip()
            addr_prefix = suf.strip() + (" " + addr_prefix if addr_prefix else "")
            break
    # URL is host + path without spaces; address starts at first space (e.g. "…org/ N.H.26, …")
    m = _URL_HOST_PATH.match(p)
    if m and m.group(2):
        u = strip_pdf_url_artifact(m.group(1).strip())
        rest = m.group(2).strip()
        addr = (rest + " " + addr_prefix).strip() if addr_prefix else rest
        return u, addr
    if m and not m.group(2):
        u = strip_pdf_url_artifact(m.group(1).strip())
        return (u, addr_prefix) if addr_prefix else (u, "")
    # Space before "Word," — fallback when path has unusual spacing
    m2 = re.search(r"(https?://.+?)\s+([A-Z][a-z][^,]*,)", p)
    if m2:
        u = m2.group(1).strip()
        addr = (m2.group(2) + p[m2.end() :]).strip()
        if addr_prefix:
            addr = (addr + " " + addr_prefix).strip()
        return u, addr
    # Lowercase→uppercase boundary where the rest looks like an address (digit / no comma)
    for mm in re.finditer(r"([a-z0-9])([A-Z][a-z])", p):
        suf = p[mm.start() + 1 :]
        if "," in suf or re.search(r"\d", suf):
            u = p[: mm.start() + 1].strip()
            addr = suf.strip()
            if addr_prefix:
                addr = (addr + " " + addr_prefix).strip()
            return u, addr
    u = strip_pdf_url_artifact(p)
    return (u, addr_prefix) if addr_prefix else (u, "")


def split_urls_before_address(before_zip: str) -> tuple[list[str], str]:
    """
    before_zip is the substring before the 6-digit zip (or empty zip): concatenated URLs + address.
    """
    before_zip = before_zip.strip()
    if not before_zip:
        return [], ""
    parts = re.split(r"(?=https?://)", before_zip)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return [], before_zip
    if not parts[0].startswith("http"):
        return [], before_zip
    urls: list[str] = []
    addr = ""
    for i, p in enumerate(parts):
        if i < len(parts) - 1:
            urls.append(p)
            continue
        u, a = split_last_url_segment(p)
        urls.append(u)
        addr = a
    return urls, addr


def parse_tail_after_urls(addr_from_url: str, zip_raw: str, status: str) -> tuple[str, str, str]:
    """Combine address fragment from URL split with zip/status."""
    z = zip_raw.replace(" ", "") if zip_raw else ""
    return addr_from_url.strip(), z, status


def parse_record(chunk: str) -> dict:
    m = re.match(r"^(\d+)(Private|State|Central|Deemed)\s*(.*)$", chunk, re.DOTALL)
    if not m:
        raise ValueError(f"Bad record chunk: {chunk[:80]!r}")
    sr_s, typ, rest = m.group(1), m.group(2), m.group(3)
    first = rest.find("http")
    if first == -1:
        return {
            "sr_no": int(sr_s),
            "type": typ,
            "name": rest.strip(),
            "website": "",
            "time_table_url": "",
            "results_url": "",
            "news_url": "",
            "admit_card_url": "",
            "student_login_url": "",
            "scheme_syllabus_url": "",
            "extra_urls": [],
            "address": "",
            "zip": "",
            "state": "Madhya Pradesh",
            "status": "",
        }
    name = rest[:first].strip()
    url_block = rest[first:]

    zip_m = re.search(r"(\d{6}|\d{3} \d{3})Madhya Pradesh(2\(f\)(?: & 12\(B\))?)", url_block)
    if zip_m:
        before_zip = url_block[: zip_m.start()].rstrip()
        zip_raw = zip_m.group(1)
        status = zip_m.group(2)
    else:
        mp_m = re.search(r"Madhya Pradesh(2\(f\)(?: & 12\(B\))?)", url_block)
        if not mp_m:
            raise ValueError(f"No Madhya Pradesh footer in record sr {sr_s}")
        before_zip = url_block[: mp_m.start()].rstrip()
        zip_raw = ""
        status = mp_m.group(1)

    urls, addr_from_split = split_urls_before_address(before_zip)
    urls = [strip_pdf_url_artifact(u) for u in urls]
    website = urls[0] if urls else ""
    extra = urls[1:] if len(urls) > 1 else []

    time_table = extra[0] if len(extra) > 0 else ""
    results = extra[1] if len(extra) > 1 else ""
    news = extra[2] if len(extra) > 2 else ""
    admit = extra[3] if len(extra) > 3 else ""
    student_login = extra[4] if len(extra) > 4 else ""
    scheme = extra[5] if len(extra) > 5 else ""
    remainder = extra[6:] if len(extra) > 6 else []

    address, zip_norm, _ = parse_tail_after_urls(addr_from_split, zip_raw, status)

    return {
        "sr_no": int(sr_s),
        "type": typ,
        "name": name,
        "website": website,
        "time_table_url": time_table,
        "results_url": results,
        "news_url": news,
        "admit_card_url": admit,
        "student_login_url": student_login,
        "scheme_syllabus_url": scheme,
        "extra_urls": remainder,
        "address": address,
        "zip": zip_norm,
        "state": "Madhya Pradesh",
        "status": status,
    }


def parse_body(body: str) -> list[dict]:
    starts = [m.start() for m in re.finditer(r"\d+(?:Private|State|Central|Deemed)", body)]
    out: list[dict] = []
    for i, s in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(body)
        out.append(parse_record(body[s:end]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Parse MP university PDF to JSON.")
    ap.add_argument(
        "pdf",
        nargs="?",
        default=Path(__file__).resolve().parents[1] / "ALL MP UNIVERSITY DETAILS_updated.pdf",
        type=Path,
    )
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args()
    text = extract_pdf_text(args.pdf)
    body = slice_data_body(text)
    rows = parse_body(body)
    out_path = args.output or (Path(__file__).resolve().parents[1] / "all_mp_university_details.json")
    out_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} records to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
