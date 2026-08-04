"""Build a Word document from the generated syllabus site."""
import os, re, html, urllib.request, hashlib
from html.parser import HTMLParser
from docxlib import Docx, NAVY, PALE, MUTED, RED

SITE = "/Users/angelysuarez/Documents/GitHub/CHS-HL English 26-27 Syllabus"
CACHE = os.path.join(os.path.dirname(__file__), "imgcache")
os.makedirs(CACHE, exist_ok=True)
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

PAGES = [
    ("index.html",       "Course Overview"),
    ("works.html",       "1. The Six Literary Works"),
    ("nonliterary.html", "2. Non-Literary Texts & Bodies of Work"),
    ("concepts.html",    "3. Concepts & Global Issues"),
    ("questions.html",   "4. Question Banks"),
    ("year1.html",       "5. Year 1 — Junior Year (2026–2027)"),
    ("year2.html",       "6. Year 2 — Senior Year (2027–2028)"),
    ("assessments.html", "7. Diploma Programme Assessments"),
    ("policy.html",      "8. Course Policies"),
    ("citations.html",   "9. Citations — APA 7th & MLA 9th"),
]

SKIP_CLASS = {"topbar", "reader-bar", "sticky-stack", "site-foot", "skip-link",
              "bg-emblem", "nb-tabs", "nb-nav", "globe-stage", "nb-spiral",
              "pager", "nb-cover"}


def fetch(url):
    key = hashlib.md5(url.encode()).hexdigest()
    ext = "png" if url.lower().endswith(".png") else "jpg"
    path = os.path.join(CACHE, f"{key}.{ext}")
    if os.path.exists(path):
        return open(path, "rb").read(), ext
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, timeout=45).read()
        open(path, "wb").write(data)
        return data, ext
    except Exception as e:
        print(f"   ! image failed: {url[:70]} {e}")
        return None, None


class Page(HTMLParser):
    """Walks a built page and emits document blocks."""

    def __init__(self, doc):
        super().__init__()
        self.d = doc
        self.stack = []          # open tags
        self.skip = 0            # depth inside a skipped element
        self.buf = []            # text buffer
        self.mode = None         # current block type
        self.in_main = False
        self.bold = 0
        self.ital = 0
        self.rows = None         # table rows being collected
        self.row = None
        self.cell = None
        self.list_depth = 0

    # -- helpers
    def flush(self):
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if not t:
            return
        if self.mode in ("h1", "h2", "h3", "h4"):
            lvl = int(self.mode[1])
            self.d.heading(t, lvl)
        elif self.mode == "li":
            self.d.bullet([self.d._run("• " + t)], level=max(0, self.list_depth - 1))
        elif self.mode == "summary":
            self.d.para([self.d._run(t, b=True, sz=19, caps=True, color="555555")],
                        space_before=120, space_after=60)
        elif self.mode == "dt":
            self.buf = []
            self._dt = t
        elif self.mode == "dd":
            self.d.bullet([self.d._run(getattr(self, "_dt", "") + " — ", b=True),
                           self.d._run(t)])
        else:
            self.d.para([self.d._run(t)])

    # -- tags
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        if self.skip:
            self.skip += 1
            return
        if tag == "main":
            self.in_main = True
            return
        if not self.in_main:
            return
        if cls & SKIP_CLASS or a.get("hidden") is not None and tag != "div":
            self.skip = 1
            return
        if tag == "img":
            src = a.get("src", "")
            if src.startswith("http"):
                data, ext = fetch(src)
                if data:
                    self.flush()
                    self.d.image(data, ext)
                    alt = a.get("alt", "")
                    if alt:
                        self.d.para([self.d._run(alt, i=True, sz=16, color="666666")],
                                    space_after=140)
            return
        if tag in ("h1", "h2", "h3", "h4", "p", "li", "summary", "dt", "dd"):
            self.flush()
            self.mode = tag
            if tag == "li":
                pass
        elif tag in ("ul", "ol"):
            self.flush(); self.list_depth += 1
        elif tag == "table":
            self.flush(); self.rows = []
        elif tag == "tr" and self.rows is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag in ("b", "strong"):
            self.bold += 1
        elif tag in ("i", "em"):
            self.ital += 1
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.skip:
            self.skip -= 1
            return
        if tag == "main":
            self.flush(); self.in_main = False
            return
        if not self.in_main:
            return
        if tag in ("h1", "h2", "h3", "h4", "p", "li", "summary", "dt", "dd"):
            if self.cell is None:
                self.flush()
            self.mode = None
        elif tag in ("ul", "ol"):
            self.flush(); self.list_depth = max(0, self.list_depth - 1)
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if any(c for c in self.row):
                self.rows.append(self.row)
            self.row = None
        elif tag == "table" and self.rows is not None:
            self.d.table(self.rows)
            self.rows = None
        elif tag in ("b", "strong"):
            self.bold = max(0, self.bold - 1)
        elif tag in ("i", "em"):
            self.ital = max(0, self.ital - 1)
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, d):
        if self.skip or not self.in_main:
            return
        if self.cell is not None:
            self.cell.append(d)
        else:
            self.buf.append(d)

    def handle_entityref(self, name):
        self.handle_data(html.unescape("&" + name + ";"))

    def handle_charref(self, name):
        self.handle_data(html.unescape("&#" + name + ";"))




def charts(d):
    """Course-at-a-glance charts, in the style of the first-draft document."""
    d.body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
    d.para([d._run("Course at a Glance", b=True, sz=36, color=NAVY)], space_after=60)
    d.rule()
    d.para([d._run("The charts below summarise how the course meets IB HL requirements "
                   "and how its texts are distributed. Every figure is counted from the "
                   "course outline itself.", i=True, sz=20, color=MUTED)],
           space_after=200)

    d.para([d._run("IB HL compliance", b=True, sz=26, color=NAVY)],
           space_before=160, space_after=80)
    d.table([
        ["Requirement", "Minimum", "This course", "Status"],
        ["Literary works studied", "6", "6", "Met"],
        ["Works in translation, PRL authors", "2", "2", "Met"],
        ["Works originally in the language studied, PRL", "2", "2", "Met"],
        ["Free choice works", "2", "2", "Met"],
        ["Literary forms", "3", "4  (novella, tragedy, poetry, short fiction)", "Exceeded"],
        ["Periods", "3", "4  (1622, 1911–30, 1948–62, 1977)", "Exceeded"],
        ["Countries or regions", "3", "6  (UK, US, Argentina, Brazil, Japan, NZ)", "Exceeded"],
        ["Continents", "2", "4  (Europe, N. America, S. America, Asia/Oceania)", "Exceeded"],
    ], widths=[3400, 1150, 3400, 1410])

    d.chart("Literary works by region",
            [("South America", 2), ("Europe (UK)", 1), ("North America", 1),
             ("Asia (Japan)", 1), ("Oceania / UK", 1)])

    d.chart("Literary works by form",
            [("Novella", 2), ("Poetry", 1), ("Tragedy", 1), ("Short fiction", 1),
             ("Novel", 1)])

    d.chart("Non-literary sources by body of work",
            [("Political cartoons", 12), ("Photography", 13), ("Advertisements", 9),
             ("Speeches", 5), ("Websites & blogs", 4), ("Art", 6),
             ("Infographics", 4), ("Satire", 4), ("Music", 1), ("Film", 1)])

    d.para([d._run("Global issue coverage", b=True, sz=26, color=NAVY)],
           space_before=200, space_after=80)
    d.para([d._run("The Individual Oral needs one non-literary text and one literary "
                   "work sharing a field of inquiry. Every field must therefore have "
                   "both.", sz=20, color=MUTED)], space_after=100)
    d.table([
        ["Field of inquiry", "Literary works", "Non-literary", "Available for the IO"],
        ["Culture, identity and community", "3", "Yes", "Yes"],
        ["Beliefs, values and education", "1", "Yes", "Yes  (narrowest — see note)"],
        ["Politics, power and justice", "1", "Yes", "Yes"],
        ["Art, creativity and the imagination", "0 primary", "Yes", "Secondary only"],
        ["Science, technology and the environment", "1", "Yes", "Yes"],
    ], widths=[3400, 1700, 1700, 2560])
    d.para([d._run("Note. Beliefs, values and education is carried by Eliot on the "
                   "literary side and by Malala Yousafzai's UN address on the "
                   "non-literary side. It is the narrowest field in the course; a "
                   "student choosing it should know that before committing.",
                   i=True, sz=18, color=RED)], space_after=160)

    d.para([d._run("Assessment weighting and timing", b=True, sz=26, color=NAVY)],
           space_before=200, space_after=80)
    d.table([
        ["Component", "Type", "When"],
        ["Individual Oral", "Internal, externally moderated", "Mid-March to mid-April 2027"],
        ["HL Essay", "External, 1,200–1,500 words", "Before Winter Break, December 2027"],
        ["Paper 1", "External, guided textual analysis", "May 2028"],
        ["Paper 2", "External, comparative essay", "May 2028"],
    ], widths=[2600, 3600, 3160])

    d.chart("Literary works per quarter",
            [("Y1 Q1  Tunnel", 1), ("Y1 Q2  Eliot", 1), ("Y1 Q3  Dunes", 1),
             ("Y1 Q4  Mansfield", 1), ("Y2 Q1  Othello", 1),
             ("Y2 Q2  Hour of the Star", 1)])


def main():
    d = Docx()
    # ---- title page
    d.para([d._run("Celebration High School", b=True, sz=26, color="2E5496")],
           align="center", space_before=1800, space_after=60)
    d.para([d._run("IB Language & Literature", b=True, sz=56, color="1F3864")],
           align="center", space_after=40)
    d.para([d._run("HIGHER LEVEL", b=True, sz=32, color="2E5496")],
           align="center", space_after=240)
    d.para([d._run("Two-Year Course Outline · Cohort 2026–2028", sz=24)],
           align="center", space_after=60)
    d.para([d._run("Instructor: Angely Suarez · Room 7-245", sz=22)],
           align="center", space_after=40)
    d.para([d._run("angely.suarezdejesus@osceolaschools.net", sz=22, color="2E5496")],
           align="center", space_after=600)
    d.para([d._run("All works and schedules are subject to change.", i=True, sz=20,
                   color="666666")], align="center", space_after=40)
    d.para([d._run("Generated from the course website · "
                   "acsuarez84.github.io/CHS-HL-English-26-27-Syllabus", sz=18,
                   color="888888")], align="center")

    charts(d)

    for fn, title in PAGES:
        path = os.path.join(SITE, fn)
        if not os.path.exists(path):
            print(f" - {fn}: missing, skipped")
            continue
        print(f" + {fn}")
        d.body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        d.para([d._run(title, b=True, sz=36, color="1F3864")],
               space_after=60, border_top=False)
        d.rule()
        p = Page(d)
        p.feed(open(path, encoding="utf-8").read())
        p.flush()

    out = os.path.join(SITE, "IB-HL Lang and Lit Syllabus.docx")
    d.save(out)
    print(f"\nwrote {out}")
    print(f"  blocks: {len(d.body)}   images: {len(d.media)}   "
          f"size: {os.path.getsize(out):,} bytes")


if __name__ == "__main__":
    main()
