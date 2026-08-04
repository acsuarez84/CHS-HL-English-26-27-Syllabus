# Rebuilding the Word version

The `.docx` linked in the site footer is generated from the built HTML pages,
so it always matches the website.

```bash
python3 tools/make_docx.py
```

Writes `IB-HL Lang and Lit Syllabus.docx` at the repository root: a title page,
then one section per page with a page break between each, all tables, and every
public-domain image embedded.

- `docxlib.py` — a small Office Open XML writer (headings, runs, lists, tables,
  images). No third-party packages required.
- `make_docx.py` — walks the built pages and emits the document. Images are
  cached in the scratch directory on first run.

Re-run it after changing site content so the two do not drift.
