# PDF notice titles (optional future)

Notice links often point to `.pdf` files. The scraper records the **URL** and anchor text; it does **not** download PDFs or extract text from inside the file.

**Possible extension:** for rows where the link text is generic (e.g. “Click here”) and the URL ends in `.pdf`, optionally fetch the first page with `pypdf` / `pdfplumber`, derive a title, and refine the `title` field during normalization. This adds dependency weight and latency; keep it behind a feature flag if implemented.
