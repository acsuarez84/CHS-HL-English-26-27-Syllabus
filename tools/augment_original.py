"""Copy the original syllabus .docx and add a Sources column to the
non-literary chart, with each body of work's sources in its own row."""
import os, re, shutil, zipfile, copy
import xml.etree.ElementTree as ET

SRC = os.path.expanduser("~/Downloads/IB-HL Lang and Lit Syllabus-Student.docx")
OUT = ("/Users/angelysuarez/Documents/GitHub/CHS-HL English 26-27 Syllabus/"
       "docs/IB-HL Lang and Lit Syllabus - Sources Added.docx")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
w = lambda t: f"{{{W}}}{t}"
ET.register_namespace("w", W)

# Sources for each row of the non-literary chart, in order.
# (row label, [ (source, note) ... ])
SOURCES = {
 "Music (album lyrics)": [
   ("Tracy Chapman, Tracy Chapman (1988) — full album", "ADDED"),
   ("• “Fast Car” — escape planned in the second person", ""),
   ("• “Behind the Wall” — unaccompanied voice; violence overheard", ""),
   ("• “Talkin’ Bout a Revolution” — the rhetoric of coming change", ""),
   ("• “Mountains o’ Things” — consumer desire from below", ""),
   ("Profanity-free. Pairs with The Hour of the Star.", "NOTE"),
 ],
 "Photography — Dorothea Lange": [
   ("White Angel Bread Line, San Francisco, 1933 (MoMA)", ""),
   ("Migrant Mother, Nipomo, March 1936 — plus 3 earlier frames", "ADDED"),
   ("Damaged Child, Shacktown, Elm Grove, 1936 (MoMA)", ""),
   ("Plantation Overseer and his Field Hands, 1936", ""),
   ("On the Road to Los Angeles, California, 1937", ""),
   ("Funeral Cortege, End of an Era, 1938 (museum print)", ""),
   ("Dust Bowl Farmer with Tractor and Son, 1938", "ADDED"),
   ("Cotton Picker near Firebaugh, California", "ADDED"),
   ("Mother and Three Children, California Squatter Camp", "ADDED"),
   ("Once a Missouri Farmer, Now a Migratory Labourer", "ADDED"),
   ("Ex-Tenant Farmer on Relief Grant, Imperial Valley", "ADDED"),
   ("Georgia Road Sign", "ADDED"),
   ("12 photographs; FSA negatives are public domain (LoC).", "NOTE"),
 ],
 "Film": [
   ("Interstellar (Nolan, 2014) — PG-13", "ADDED"),
   ("Science, technology and the environment", "FIELD"),
   ("Scenes: the dust storm; the docking sequence; Miller’s planet.", ""),
   ("Pairs with The Woman in the Dunes.", "NOTE"),
 ],
 "Art Edward Hopper": [
   ("Nighthawks, 1942 (Art Institute of Chicago)", "ADDED"),
   ("Automat, 1927 (Des Moines Art Center)", "ADDED"),
   ("Early Sunday Morning, 1930 (Whitney)", "ADDED"),
   ("Room in New York, 1932 (Sheldon)", "ADDED"),
   ("Morning Sun, 1952 (Columbus Museum of Art)", "ADDED"),
   ("New York Movie, 1939 (MoMA)", "ADDED"),
   ("In copyright — project from the museum pages.", "NOTE"),
 ],
 "Advertisements": [
   ("Nike — Purpose, powered by athletes", ""),
   ("The Dove Self-Esteem Project", ""),
   ("Patagonia — Environmental Activism", ""),
   ("Ben & Jerry’s — Activism (select specific campaigns)", ""),
   ("LEGO — About Us", ""),
   ("“Towards a day less war!” — Ad*Access BH1901", ""),
   ("“My barber knows women” — Kreml Hair Tonic, 1944,", "ADDED"),
   ("   Cosmopolitan. Ad*Access BH0543. Sells tonic and war bonds.", ""),
   ("“Home…” — Ad*Access W0333", ""),
   ("World’s Industrial Exhibition, 1853 — Duke EAA A0249", ""),
 ],
 "Infographics (One-Off)": [
   ("W. E. B. Du Bois — Data Portraits, 1900 Paris Exposition", "ADDED"),
   ("Our World in Data — CO₂ and greenhouse gas emissions", "ADDED"),
   ("Bloomberg — What’s Really Warming the World? (2015)", "ADDED"),
   ("Florence Nightingale — the rose diagram, 1858 (optional)", "ADDED"),
   ("Du Bois is public domain at the Library of Congress.", "NOTE"),
 ],
 "Satire / Humor": [
   ("Jonathan Swift, “A Modest Proposal” (1729) — Gutenberg", "ADDED"),
   ("Key & Peele, “Obama’s Anger Translator” — Comedy Central", "ADDED"),
   ("Mark Twain, “Advice to Youth” (1882) — Gutenberg", "ADDED"),
   ("Teacher-vetted satirical headline set", "ADDED"),
   ("Use the Comedy Central page: the YouTube cut is uncensored.", "NOTE"),
 ],
 "Speeches": [
   ("Sojourner Truth, “Ain’t I a Woman?” (1851)", "ADDED"),
   ("Frederick Douglass, “What to the Slave Is the Fourth", "ADDED"),
   ("   of July?” (1852)", ""),
   ("Martin Luther King Jr., “I Have a Dream” (1963)", "ADDED"),
   ("Malala Yousafzai, UN Youth Assembly (2013)", "ADDED"),
   ("Greta Thunberg, UN Climate Action Summit (2019)", "ADDED"),
   ("Spans all five fields. Malala carries Beliefs, values", "NOTE"),
   ("and education, which no other non-literary text does.", ""),
 ],
 "Political Cartoons": [
   ("Frank Bellew, “Melican Leportee Man” — Harper’s Weekly,", ""),
   ("   14 June 1879, p. 476", ""),
   ("“The Rich Growing Richer” — Harper’s Weekly, 2 Sept 1871", ""),
   ("Welcome to All! — Keppler, Puck, 1880", "ADDED"),
   ("How John May Dodge the Exclusion Act — Puck, 1905", "ADDED"),
   ("The Americanese Wall — 1916", "ADDED"),
   ("The Fool Pied Piper — Ehrhart, Puck, 1909", "ADDED"),
   ("History Repeats Itself: Robber Barons — Puck, 1889", "ADDED"),
   ("The Open Sesame — Puck, 1896", "ADDED"),
   ("A Squelcher for Woman Suffrage — Puck, 1894", "ADDED"),
   ("The Apotheosis of Suffrage — 1896", "ADDED"),
   ("The Fin de Siècle Newspaper Proprietor — Puck, 1894", "ADDED"),
   ("Freedom of the Press — c. 1912", "ADDED"),
   ("Bellew and How John May Dodge contain racist caricature:", "NOTE"),
   ("teach objectively under s. 1000.05; log with media specialist.", ""),
 ],
 "Websites / Blogs": [
   ("Climate Change — NASA Science", ""),
   ("Climate — NOAA", ""),
   ("Humans of New York — use the books, not the feed", "ADDED"),
   ("The Pudding — pudding.cool", "ADDED"),
   ("HONY supplies the Identity concept this row claims;", "NOTE"),
   ("NASA and NOAA do no identity work.", ""),
 ],
}

HDR = "Sources"


def cell_text(tc):
    return "".join(n.text or "" for n in tc.iter(w("t"))).strip()


def make_cell(model, lines, width):
    """Clone a cell's formatting, replace its content with `lines`."""
    tc = copy.deepcopy(model)
    # keep tcPr, drop all block children
    for child in list(tc):
        if child.tag != w("tcPr"):
            tc.remove(child)
    tcpr = tc.find(w("tcPr"))
    if tcpr is not None:
        tcw = tcpr.find(w("tcW"))
        if tcw is None:
            tcw = ET.SubElement(tcpr, w("tcW"))
        tcw.set(w("w"), str(width))
        tcw.set(w("type"), "dxa")
        # clear any inherited shading so added rows read as plain cells
        shd = tcpr.find(w("shd"))
        if shd is not None and lines and lines[0][1] != "HDR":
            tcpr.remove(shd)
    for text, tag in lines:
        p = ET.SubElement(tc, w("p"))
        ppr = ET.SubElement(p, w("pPr"))
        sp = ET.SubElement(ppr, w("spacing"))
        sp.set(w("before"), "0"); sp.set(w("after"), "20")
        sp.set(w("line"), "220"); sp.set(w("lineRule"), "auto")
        r = ET.SubElement(p, w("r"))
        rpr = ET.SubElement(r, w("rPr"))
        f = ET.SubElement(rpr, w("rFonts"))
        for a in ("ascii", "hAnsi", "cs"):
            f.set(w(a), "Arial Narrow")
        sz = ET.SubElement(rpr, w("sz")); sz.set(w("val"), "16")
        szc = ET.SubElement(rpr, w("szCs")); szc.set(w("val"), "16")
        if tag == "HDR":
            for e, v in ((w("b"), None), ):
                ET.SubElement(rpr, e)
            c = ET.SubElement(rpr, w("color")); c.set(w("val"), "FFFFFF")
            sz.set(w("val"), "18"); szc.set(w("val"), "18")
        elif tag == "ADDED":
            ET.SubElement(rpr, w("b"))
            c = ET.SubElement(rpr, w("color")); c.set(w("val"), "1F4E79")
        elif tag == "NOTE":
            ET.SubElement(rpr, w("i"))
            c = ET.SubElement(rpr, w("color")); c.set(w("val"), "C00000")
        elif tag == "FIELD":
            ET.SubElement(rpr, w("b"))
            c = ET.SubElement(rpr, w("color")); c.set(w("val"), "1F4E79")
        t = ET.SubElement(r, w("t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = text
    return tc


def main():
    shutil.copy(SRC, OUT)
    zin = zipfile.ZipFile(SRC)
    doc = zin.read("word/document.xml").decode("utf-8")
    root = ET.fromstring(doc)

    tbl = list(root.iter(w("tbl")))[2]          # the non-literary chart
    rows = tbl.findall(w("tr"))
    print(f"chart rows: {len(rows)}")

    # widen the grid: squeeze existing columns, append one for Sources
    grid = tbl.find(w("tblGrid"))
    cols = grid.findall(w("gridCol"))
    old_w = [int(c.get(w("w")) or 0) for c in cols]
    total = sum(old_w) or 9360
    new_src_w = int(total * 0.40)
    scale = (total - new_src_w) / total
    for c, ow in zip(cols, old_w):
        c.set(w("w"), str(int(ow * scale)))
    gc = ET.SubElement(grid, w("gridCol")); gc.set(w("w"), str(new_src_w))

    added = 0
    for ri, tr in enumerate(rows):
        tcs = tr.findall(w("tc"))
        if not tcs:
            continue
        # rescale existing cell widths to match the new grid
        for tc, ow in zip(tcs, old_w):
            tcpr = tc.find(w("tcPr"))
            if tcpr is not None:
                tcw = tcpr.find(w("tcW"))
                if tcw is not None:
                    try:
                        tcw.set(w("w"), str(int(int(tcw.get(w("w"))) * scale)))
                    except (TypeError, ValueError):
                        pass
        label = cell_text(tcs[0])
        if ri == 0:
            lines = [(HDR, "HDR")]
        else:
            key = next((k for k in SOURCES if label.startswith(k[:18])), None)
            lines = SOURCES.get(key, [("—", "")])
            if key:
                added += 1
        tr.append(make_cell(tcs[-1], lines, new_src_w))

    print(f"rows given sources: {added}")

    out_xml = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    # rewrite the archive with the modified document part
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = out_xml
            zout.writestr(item, data)
    zin.close()
    print(f"wrote {OUT}")
    print(f"  size: {os.path.getsize(OUT):,} bytes")


if __name__ == "__main__":
    main()
