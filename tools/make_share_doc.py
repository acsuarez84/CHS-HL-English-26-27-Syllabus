"""Teacher-only Word document: QR codes and Canvas embed codes."""
import os, sys
sys.path.insert(0, "/Users/angelysuarez/Documents/GitHub/CHS-HL English 26-27 Syllabus/tools")
from docxlib import Docx, NAVY, MUTED, RED, PALE

REPO = "/Users/angelysuarez/Documents/GitHub/CHS-HL English 26-27 Syllabus"
OUT = os.path.join(REPO, "docs", "teacher",
                   "Syllabus QR Code and Canvas Embed Codes.docx")
URL = "https://acsuarez84.github.io/CHS-HL-English-26-27-Syllabus/"

SECTIONS = [
    ("Syllabus home", "index.html"),
    ("The Six Literary Works", "works.html"),
    ("Non-Literary Texts", "nonliterary.html"),
    ("Concepts & Global Issues", "concepts.html"),
    ("Question Banks", "questions.html"),
    ("Year 1 — 2026–27", "year1.html"),
    ("Year 2 — 2027–28", "year2.html"),
    ("Assessments", "assessments.html"),
    ("Course Policies", "policy.html"),
    ("Citations", "citations.html"),
]

IFRAME = ('<iframe src="' + URL + '"\n'
          '        title="IB Language and Literature HL Syllabus"\n'
          '        width="100%" height="900"\n'
          '        style="border:1px solid #ccc; border-radius:8px;"\n'
          '        allowfullscreen></iframe>')

SECTION_IFRAME = ('<iframe src="' + URL + 'policy.html"\n'
                  '        title="Course Policies"\n'
                  '        width="100%" height="900"\n'
                  '        style="border:1px solid #ccc; border-radius:8px;"></iframe>')

CARD = ('<div style="text-align:center; padding:1.5em; border:2px solid #1F4E79;\n'
        '            border-radius:12px; max-width:520px; margin:1em auto;">\n'
        '  <h2 style="margin:0 0 .3em; color:#1F4E79;">IB Language &amp; Literature HL</h2>\n'
        '  <p style="margin:0 0 1em; color:#555;">Two-Year Course Outline &middot; 2026-2028</p>\n'
        '  <p><a href="' + URL + '" target="_blank" rel="noopener"\n'
        '        style="display:inline-block; background:#1F4E79; color:#fff;\n'
        '               padding:.7em 1.6em; border-radius:999px;\n'
        '               text-decoration:none; font-weight:bold;">Open the Syllabus</a></p>\n'
        '  <p>[ insert the QR image here from Canvas Files ]</p>\n'
        '  <p style="font-size:.85em; color:#666;">Scan with a phone camera</p>\n'
        '</div>')


def code(d, text):
    """Monospaced block on a tinted background, safe to copy out of Word."""
    for line in text.split("\n"):
        d.para([d._run(line or " ", sz=17)], shade=PALE, space_after=0,
               space_before=0, ind=120)
    d.para([d._run("")], space_after=120)


def main():
    d = Docx()
    d.para([d._run("Teacher reference — not part of the student site",
                   b=True, sz=18, color=RED, caps=True)], align="center", space_after=80)
    d.para([d._run("Syllabus QR Code & Canvas Embed Codes", b=True, sz=40,
                   color=NAVY)], align="center", space_after=60)
    d.para([d._run("IB Language & Literature HL · Celebration High School · 2026–2028",
                   sz=22, color=MUTED)], align="center", space_after=280)

    d.heading("The link", 2)
    d.para([d._run(URL, b=True, sz=22, color=NAVY)], shade=PALE, space_after=140)

    # ---- QR codes
    d.heading("QR codes", 2)
    d.para([d._run("Both point at the syllabus home page and use the highest "
                   "error-correction level, so they still scan after photocopying, or "
                   "with a small logo placed in the centre.")])
    d.para([d._run("Scan one with your phone before printing a class set. Thirty "
                   "seconds now saves a wall of posters that do not work.",
                   b=True, color=RED)], space_after=140)

    for label, fn, note in (
        ("For screen — slides, Canvas pages", "syllabus-qr.png", "600 × 600 px"),
        ("For print — handouts, posters, the classroom wall", "syllabus-qr-print.png",
         "1000 × 1000 px"),
    ):
        d.para([d._run(label, b=True, sz=21, color=NAVY)], space_before=140, space_after=40)
        d.para([d._run(note, i=True, sz=18, color=MUTED)], space_after=60)
        p = os.path.join(REPO, "docs", "teacher", fn)
        if os.path.exists(p):
            d.image(open(p, "rb").read(), "png", max_w_in=2.3)
        d.para([d._run("File: docs/teacher/" + fn, sz=17, color=MUTED)], space_after=160)

    # ---- Canvas
    d.heading("Putting it in Canvas", 2, page_break=True)
    d.para([d._run("Open the page in Canvas, click the HTML Editor button "
                   "( </> ) in the Rich Content Editor, and paste one of the blocks "
                   "below.")])
    d.para([d._run("The frame looks empty while you are editing. Canvas only draws it "
                   "once you save and view the page — that is normal.",
                   i=True, color=RED)], space_after=160)

    d.para([d._run("1 · Embed the whole syllabus", b=True, sz=23, color=NAVY)],
           space_before=120, space_after=60)
    code(d, IFRAME)

    d.para([d._run("2 · Embed a single section", b=True, sz=23, color=NAVY)],
           space_before=160, space_after=60)
    d.para([d._run("Swap policy.html for any filename from the table below.")],
           space_after=60)
    code(d, SECTION_IFRAME)

    d.para([d._run("3 · Link and QR card, no frame", b=True, sz=23, color=NAVY)],
           space_before=160, space_after=60)
    d.para([d._run("Use this on a Canvas home page, or if the district blocks embedded "
                   "frames. Upload the QR image to Canvas Files first, then insert it "
                   "where the placeholder line sits.")], space_after=60)
    code(d, CARD)

    d.heading("Filenames for each section", 2, page_break=True)
    d.table([["Section", "Filename"]] + [[a, b] for a, b in SECTIONS],
            widths=[5200, 4160])

    d.para([d._run("It updates itself.", b=True, color=NAVY)], space_before=160,
           space_after=40)
    d.para([d._run("The site republishes whenever the syllabus changes, so anything "
                   "embedded in Canvas stays current. The code never has to be pasted "
                   "again.")])

    d.save(OUT)
    print("wrote", OUT)
    print(f"  {os.path.getsize(OUT):,} bytes")


if __name__ == "__main__":
    main()
