# Putting the syllabus in Canvas

**Site URL**
`https://acsuarez84.github.io/CHS-HL-English-26-27-Syllabus/`

Verified embeddable: GitHub Pages sends no `X-Frame-Options` and no
`frame-ancestors` policy, and the site is HTTPS — which Canvas requires.

---

## QR codes

| File | Size | Use |
|------|------|-----|
| `assets/syllabus-qr.png` | 540 × 540 px | Screen, slides, Canvas pages |
| `assets/syllabus-qr-print.png` | 1080 × 1080 px | Print — handouts, posters, the classroom wall |

Encoded at **error-correction level Q** (~25% recoverable), so they still scan
after photocopying, or if you drop a small logo in the centre.

Both decode to the site URL exactly — verified by decoding them back, not just
by eye.

---

## Embedding in Canvas

Open the page, click the **HTML Editor** (`</>`) in the Rich Content Editor, and
paste. The iframe will look blank while editing — Canvas only renders it in
**View** mode.

### 1. Full embed

```html
<p>
  <iframe src="https://acsuarez84.github.io/CHS-HL-English-26-27-Syllabus/"
          title="IB Language and Literature HL Syllabus"
          width="100%" height="900"
          style="border:1px solid #ccc; border-radius:8px;"
          allowfullscreen>
  </iframe>
</p>
<p style="font-size:0.9em">
  If the syllabus does not load,
  <a href="https://acsuarez84.github.io/CHS-HL-English-26-27-Syllabus/" target="_blank"
     rel="noopener">open it in a new tab</a>.
</p>
```

### 2. Jump straight to one section

Swap the filename to land students where you want them:

| Section | Replace the end of the URL with |
|---------|--------------------------------|
| Literary works | `works.html` |
| Non-literary texts | `nonliterary.html` |
| Concepts & global issues | `concepts.html` |
| Question banks | `questions.html` |
| Year 1 | `year1.html` |
| Year 2 | `year2.html` |
| Assessments | `assessments.html` |
| Course policies | `policy.html` |
| Citations | `citations.html` |

```html
<iframe src="https://acsuarez84.github.io/CHS-HL-English-26-27-Syllabus/policy.html"
        title="Course Policies" width="100%" height="900"
        style="border:1px solid #ccc; border-radius:8px;"></iframe>
```

### 3. Button plus QR, no iframe

Useful on a Canvas home page, and it survives any district iframe restriction.

```html
<div style="text-align:center; padding:1.5em; border:2px solid #1F4E79;
            border-radius:12px; max-width:520px; margin:1em auto;">
  <h2 style="margin:0 0 .3em; color:#1F4E79;">IB Language &amp; Literature HL</h2>
  <p style="margin:0 0 1em; color:#555;">Two-Year Course Outline · Cohort 2026–2028</p>
  <p>
    <a href="https://acsuarez84.github.io/CHS-HL-English-26-27-Syllabus/"
       target="_blank" rel="noopener"
       style="display:inline-block; background:#1F4E79; color:#fff;
              padding:.7em 1.6em; border-radius:999px; text-decoration:none;
              font-weight:bold;">Open the Syllabus</a>
  </p>
  <p style="margin-top:1em;">
    <img src="QR_IMAGE_URL_HERE" alt="QR code linking to the course syllabus"
         width="180" height="180">
  </p>
  <p style="font-size:.85em; color:#666;">Scan with a phone camera</p>
</div>
```

To use that QR image: upload `assets/syllabus-qr.png` to **Canvas Files**, then
insert it with the RCE image button and copy the `src` Canvas gives it into
`QR_IMAGE_URL_HERE`. Hot-linking from GitHub also works:

```
https://acsuarez84.github.io/CHS-HL-English-26-27-Syllabus/assets/syllabus-qr.png
```

---

## Notes

- **Height.** `900` suits most pages. The non-literary section is long — either
  raise it or let students scroll inside the frame.
- **Editing view.** A blank box while editing is normal. Save and view the page.
- **If your district blocks iframes**, use option 3 — a link and a QR code always
  work.
- **Updating.** The site redeploys on every push, so anything embedded in Canvas
  updates itself. Nothing to re-paste.
