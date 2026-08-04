# CHS IB Language & Literature HL — Interactive Syllabus

An accessible, multi-page website built from the two-year IB Language & Literature HL
course outline for **Celebration High School, cohort 2026–2028**
(Instructor: Angely Suarez, Room 7-245).

## What it does

- **A page per part of the syllabus.** Nine pages, reachable from the **Home** grid or the
  **Sections ▾** menu in the top bar.
- **Every text is mapped.** Each of the six literary works and each non-literary body of
  work carries its IB course concepts and its Global Issue field of inquiry.
- **An Individual Oral pairing page.** 25 non-literary ↔ literary pairings, each with the
  global issue they share and a sentence on why the pair works. Filterable by field of
  inquiry.
- **Working source links.** Every work, photograph, painting, advertisement, speech,
  cartoon and website opens its real source in a new tab.
- **Light & dark themes.** A toggle in the top bar; also respects the reader's operating
  system preference on first visit and remembers the choice in `localStorage`.
- **Read aloud (text-to-speech).** Speaks the page using the browser's speech synthesis,
  with Pause / Restart / Stop, a voice picker, and speed control.
- **Accessibility.** Semantic HTML, a "Skip to main content" link, visible keyboard focus,
  ARIA labels, high-contrast colors in both themes, and reduced-motion support.

## Pages

| Path | Purpose |
|------|---------|
| `index.html` | Course overview, what students will learn, section cards |
| `works.html` | The six HL works, IB category compliance, concept & global issue map |
| `nonliterary.html` | Every non-literary body of work with its sources |
| `concepts.html` | The 7 course concepts and 5 fields of inquiry, with course coverage |
| `pairings.html` | Individual Oral pairings, filterable by field of inquiry |
| `year1.html` | Junior year (2026–2027), quarter by quarter |
| `year2.html` | Senior year (2027–2028), quarter by quarter |
| `assessments.html` | Paper 1, Paper 2, the Individual Oral, the HL Essay |
| `eliot.html` | All 19 T. S. Eliot poems with access links, plus author background |
| `assets/style.css` | Shared styles, light + dark themes |
| `assets/app.js` | Theme toggle + read-aloud behavior |
| `IB-HL Lang and Lit Syllabus.docx` | The source document, bundled for download |

## Sources added to fill gaps

The original outline named several non-literary text types without naming an actual text,
and named a few texts without mapping them. Sources added to close those gaps are marked
**added** on the Non-Literary Texts page; everything unmarked is from the original outline
with its original link. In short:

- **Music** — Tracy Chapman, *Tracy Chapman* (1988)
- **Art** — six Edward Hopper paintings
- **Infographics** — W. E. B. Du Bois's 1900 Data Portraits, Our World in Data, Bloomberg,
  Nightingale
- **Satire** — Swift, Twain, Key & Peele, *The Onion*
- **Speeches** — Truth, Douglass, King, Yousafzai, Thunberg
- **Websites** — Humans of New York, The Pudding
- **Film, advertisements, political cartoons** — existing titles given concept and global
  issue mappings

One structural change: mapping the whole course showed **Beliefs, values and education**
had one literary work (Eliot) and no non-literary text, so no student could choose that
field for the IO. Malala Yousafzai's UN address and *Shutter Island* close that gap.

## Still to decide

- **Dave Whamond cartoon** — a specific cartoon still needs choosing (flagged on the page).
- **Music global issue** — this row was moved from *Art, creativity and the imagination* to
  *Culture, identity and community*; the alternative is noted on the page.

## Viewing it

Open `index.html` in any modern browser — no build step or server required.

## Publishing on GitHub Pages

Push to `main`. The workflow in `.github/workflows/pages.yml` builds and deploys
automatically and turns Pages on by itself, so no Settings change is needed. The site will
be live at `https://<username>.github.io/<repository>/`.

The `.nojekyll` file ensures GitHub Pages serves the files as-is.

> **Note on read-aloud voices:** available voices come from the visitor's own browser and
> operating system, so the voice list varies by device. The feature degrades gracefully and
> hides itself in browsers without speech-synthesis support.
