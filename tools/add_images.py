"""Add the sourced public-domain images into the updated syllabus document,
following the document's own caption-then-image table pattern."""
import os, copy, shutil, zipfile, hashlib, urllib.request, struct
import xml.etree.ElementTree as ET

SRC = "/Users/angelysuarez/Documents/IB HL Language and Literature 26-27-Updated.docx"
OUT = ("/Users/angelysuarez/Documents/GitHub/CHS-HL English 26-27 Syllabus/docs/"
       "IB HL Language and Literature 26-27-Updated (images added).docx")
CACHE = os.path.join(os.path.dirname(__file__), "imgcache")
os.makedirs(CACHE, exist_ok=True)
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
w = lambda t: f"{{{W}}}{t}"
for p, u in (("w", W), ("r", R), ("a", A), ("pic", PIC), ("wp", WP)):
    ET.register_namespace(p, u)

L = "https://tile.loc.gov/storage-services/service/pnp/"

# (caption, image url) — appended to the Lange table
LANGE = [
 ("Dorothea Lange. Migrant Mother — frame 1 of 4 (widest). Nipomo, March 1936. "
  "The tent, pole, lantern, pie tin and a second camp are all still visible.",
  L + "fsa/8b29000/8b29500/8b29525v.jpg"),
 ("Dorothea Lange. Migrant Mother — frame 2 of 4. Closer; the pole and lantern remain.",
  L + "fsa/8b29000/8b29500/8b29523v.jpg"),
 ("Dorothea Lange. Migrant Mother — frame 3 of 4. Closer still; the children turn away.",
  L + "fsa/8b29000/8b29500/8b29527v.jpg"),
 ("Dorothea Lange. Dust Bowl Farmer with Tractor and Son, near Claud, New Mexico. 1938.",
  L + "fsa/8b32000/8b32400/8b32410v.jpg"),
 ("Dorothea Lange. Cotton Picker near Firebaugh, California. Shot at eye level.",
  L + "fsa/8b32000/8b32900/8b32947v.jpg"),
 ("Dorothea Lange. Mother and Three Children in a California Squatter Camp.",
  L + "fsa/8c51000/8c51900/8c51918v.jpg"),
 ("Dorothea Lange. Once a Missouri Farmer, Now a Migratory Farm Labourer on the Pacific Coast.",
  L + "fsa/8e07000/8e07300/8e07318v.jpg"),
 ("Dorothea Lange. Ex-Tenant Farmer on Relief Grant, Imperial Valley, California.",
  L + "fsa/8b31000/8b31800/8b31812v.jpg"),
 ("Dorothea Lange. Georgia Road Sign. Language in the landscape.",
  L + "fsa/8b32000/8b32200/8b32291v.jpg"),
]

CARTOONS = [
 ("Welcome to All! Joseph Keppler, Puck, 1880. Uncle Sam at the U.S. Ark of Refuge.",
  L + "ds/16200/16265r.jpg"),
 ("How John May Dodge the Exclusion Act. Puck, 1905. Companion to the Bellew cartoon. "
  "Contains ethnic caricature — teach objectively under s. 1000.05.",
  L + "ppmsca/25900/25972r.jpg"),
 ("The Americanese Wall — as Congressman Burnett Would Build It. 1916.",
  L + "ds/14100/14198r.jpg"),
 ("The Fool Pied Piper. Samuel Ehrhart, Puck, 1909.",
  L + "ppmsca/26300/26380r.jpg"),
 ("History Repeats Itself — the Robber Barons of the Middle Ages and of Today. Puck, 1889.",
  L + "cph/3a30000/3a31000/3a31300/3a31325r.jpg"),
 ("The Open Sesame. Puck, 1896.",
  L + "ppmsca/28800/28898r.jpg"),
 ("A Squelcher for Woman Suffrage. Puck, 6 June 1894.",
  L + "ppmsca/29100/29110r.jpg"),
 ("The Apotheosis of Suffrage. 1896. The counter-position to the cartoon above.",
  L + "cph/3a10000/3a13000/3a13200/3a13267r.jpg"),
 ("The Fin de Siècle Newspaper Proprietor. Puck, 7 March 1894.",
  L + "ppmsca/29000/29087r.jpg"),
 ("Freedom of the Press. c. 1912.",
  L + "ppmsca/19500/19519r.jpg"),
]

DUBOIS = [
 ("W. E. B. Du Bois. The Georgia Negro: A Social Study — Occupations. 1900 Paris Exposition. "
  "Hand-drawn statistical charts; public domain at the Library of Congress.",
  L + "ppmsca/33800/33890v.jpg"),
 ("W. E. B. Du Bois. Negro Population of Georgia. 1900 Paris Exposition.",
  L + "ppmsca/33800/33866v.jpg"),
]

EMU = 914400


def fetch(url):
    key = hashlib.md5(url.encode()).hexdigest()
    path = os.path.join(CACHE, key + ".jpg")
    if os.path.exists(path):
        return open(path, "rb").read()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    d = urllib.request.urlopen(req, timeout=60).read()
    open(path, "wb").write(d)
    return d


def jpeg_size(d):
    i = 2
    while i < len(d) - 9:
        if d[i] != 0xFF:
            i += 1; continue
        m = d[i + 1]
        if m in (0xC0, 0xC1, 0xC2, 0xC3):
            h, wd = struct.unpack(">HH", d[i + 5:i + 9]); return wd, h
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            i += 2; continue
        i += 2 + struct.unpack(">H", d[i + 2:i + 4])[0]
    return None, None


class Builder:
    def __init__(self, zin):
        self.media = []
        self.rels_add = []
        names = [n for n in zin.namelist() if n.startswith("word/media/")]
        self.n = len(names)
        rx = ET.fromstring(zin.read("word/_rels/document.xml.rels"))
        ids = [e.get("Id") for e in rx]
        self.rid = max((int(i[3:]) for i in ids if i[3:].isdigit()), default=100)

    def add_image(self, data):
        self.n += 1
        self.rid += 1
        name = f"claude{self.n}.jpg"
        rid = f"rId{self.rid}"
        self.media.append((name, data))
        self.rels_add.append((rid, f"media/{name}"))
        return rid, name

    def pic_para(self, data, max_in=3.1):
        wd, h = jpeg_size(data)
        if not wd:
            return None
        rid, name = self.add_image(data)
        scale = min(1.0, max_in / (wd / 96.0))
        cx, cy = int(wd / 96.0 * scale * EMU), int(h / 96.0 * scale * EMU)
        xml = (f'<w:p xmlns:w="{W}" xmlns:r="{R}" xmlns:a="{A}" xmlns:pic="{PIC}" '
               f'xmlns:wp="{WP}"><w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>'
               f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
               f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{9000 + self.n}" name="{name}"/>'
               f'<a:graphic><a:graphicData uri="{PIC}">'
               f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{9000 + self.n}" name="{name}"/>'
               f'<pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}"/>'
               f'<a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr>'
               f'<a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
               f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
               f'</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
        return ET.fromstring(xml)


def text_para(text, bold=False, red=False, size="16"):
    p = ET.Element(w("p"))
    ppr = ET.SubElement(p, w("pPr"))
    sp = ET.SubElement(ppr, w("spacing"))
    sp.set(w("before"), "0"); sp.set(w("after"), "40")
    r = ET.SubElement(p, w("r"))
    rpr = ET.SubElement(r, w("rPr"))
    f = ET.SubElement(rpr, w("rFonts"))
    for a in ("ascii", "hAnsi", "cs"):
        f.set(w(a), "Arial Narrow")
    if bold:
        ET.SubElement(rpr, w("b"))
    if red:
        c = ET.SubElement(rpr, w("color")); c.set(w("val"), "C00000")
    sz = ET.SubElement(rpr, w("sz")); sz.set(w("val"), size)
    szc = ET.SubElement(rpr, w("szCs")); szc.set(w("val"), size)
    t = ET.SubElement(r, w("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return p


def add_rows(tbl, items, b, model_row):
    """Append caption|image rows matching the table's existing pattern."""
    for caption, url in items:
        try:
            data = fetch(url)
        except Exception as e:
            print(f"   ! {url[:60]} {e}")
            continue
        tr = copy.deepcopy(model_row)
        tcs = tr.findall(w("tc"))
        for tc in tcs:
            for ch in list(tc):
                if ch.tag != w("tcPr"):
                    tc.remove(ch)
        tcs[0].append(text_para(caption))
        pic = b.pic_para(data)
        if pic is None:
            continue
        (tcs[1] if len(tcs) > 1 else tcs[0]).append(pic)
        if len(tcs) > 1 and not list(tcs[1]):
            tcs[1].append(text_para(""))
        tbl.append(tr)
    return len(items)


def main():
    zin = zipfile.ZipFile(SRC)
    root = ET.fromstring(zin.read("word/document.xml"))
    b = Builder(zin)
    tbls = list(root.iter(w("tbl")))

    lange, cartoons = tbls[3], tbls[6]
    print("adding Lange photographs...")
    add_rows(lange, LANGE, b, lange.findall(w("tr"))[-1])
    print("adding political cartoons...")
    add_rows(cartoons, CARTOONS, b, cartoons.findall(w("tr"))[-1])
    print("adding Du Bois data portraits...")
    # Du Bois has no table of its own; give it one modelled on the cartoons table
    dub = copy.deepcopy(cartoons)
    for tr in dub.findall(w("tr")):
        dub.remove(tr)
    add_rows(dub, DUBOIS, b, cartoons.findall(w("tr"))[0])
    # place the Du Bois table just before the cartoons table, wherever it lives
    parent = next((el for el in root.iter() if cartoons in list(el)), None)
    heading = text_para("Infographics \u2014 W. E. B. Du Bois, Data Portraits (1900)",
                        bold=True, size="20")
    if parent is None:
        parent = root.find(w("body"))
        parent.append(heading); parent.append(dub)
    else:
        i = list(parent).index(cartoons)
        parent.insert(i, dub)
        parent.insert(i, heading)

    rels = ET.fromstring(zin.read("word/_rels/document.xml.rels"))
    for rid, target in b.rels_add:
        e = ET.SubElement(rels, "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
        e.set("Id", rid); e.set("Target", target)
        e.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")

    ct = zin.read("[Content_Types].xml").decode("utf-8")
    if 'Extension="jpg"' not in ct:
        ct = ct.replace("</Types>",
                        '<Default Extension="jpg" ContentType="image/jpeg"/></Types>')

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
            elif item.filename == "word/_rels/document.xml.rels":
                data = ET.tostring(rels, encoding="UTF-8", xml_declaration=True)
            elif item.filename == "[Content_Types].xml":
                data = ct.encode("utf-8")
            z.writestr(item, data)
        for name, d in b.media:
            z.writestr(f"word/media/{name}", d)
    zin.close()
    print(f"\nwrote {OUT}")
    print(f"  images added: {len(b.media)}   size: {os.path.getsize(OUT):,} bytes")


if __name__ == "__main__":
    main()
