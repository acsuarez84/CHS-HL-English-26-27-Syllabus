"""Minimal Office Open XML writer — headings, runs, lists, tables, images."""
import os, zlib, struct, zipfile, html as H

EMU = 914400  # EMU per inch

# Palette lifted from the first-draft Word document
NAVY   = "1F4E79"   # header fill / heading text
PALE   = "EAF1F8"   # banded row fill
GREY   = "F2F2F2"   # neutral fill
PEACH  = "FAE2D5"
SKY    = "DAE9F7"
MINT   = "D9F2D0"
RED    = "C00000"
MUTED  = "595959"


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Docx:
    def __init__(self):
        self.body = []
        self.media = []          # (filename, bytes, w_emu, h_emu)
        self._rid = 10

    # ---- runs ---------------------------------------------------------
    def _run(self, text, b=False, i=False, sz=None, color=None, caps=False):
        rpr = []
        if b: rpr.append("<w:b/>")
        if i: rpr.append("<w:i/>")
        if sz: rpr.append(f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>')
        if color: rpr.append(f'<w:color w:val="{color}"/>')
        if caps: rpr.append("<w:caps/>")
        r = f"<w:rPr>{''.join(rpr)}</w:rPr>" if rpr else ""
        return (f'<w:r>{r}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>')

    def para(self, runs, style=None, align=None, space_before=0, space_after=120,
             ind=0, border_top=False, shade=None):
        ppr = []
        if style: ppr.append(f'<w:pStyle w:val="{style}"/>')
        if align: ppr.append(f'<w:jc w:val="{align}"/>')
        if ind: ppr.append(f'<w:ind w:left="{ind}"/>')
        if border_top:
            ppr.append('<w:pBdr><w:top w:val="single" w:sz="6" w:space="6" '
                       'w:color="BBBBBB"/></w:pBdr>')
        if shade:
            ppr.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>')
        ppr.append(f'<w:spacing w:before="{space_before}" w:after="{space_after}"/>')
        p = f'<w:p><w:pPr>{"".join(ppr)}</w:pPr>{"".join(runs)}</w:p>'
        self.body.append(p)

    def text(self, t, **kw):
        self.para([self._run(t)], **kw)

    def heading(self, t, level=1, page_break=False):
        sizes = {1: 40, 2: 30, 3: 24, 4: 20}
        colors = {1: "1F3864", 2: "2E5496", 3: "333333", 4: "555555"}
        pb = '<w:r><w:br w:type="page"/></w:r>' if page_break else ""
        if pb:
            self.body.append(f"<w:p>{pb}</w:p>")
        self.para([self._run(t, b=True, sz=sizes.get(level, 22),
                             color=colors.get(level, "333333"),
                             caps=(level == 4))],
                  space_before=(240 if level <= 2 else 180), space_after=120)

    def bullet(self, runs, level=0):
        self.para(runs, ind=360 + 360 * level, space_after=60)

    def rule(self):
        self.para([self._run("")], border_top=True, space_after=60)

    # ---- image --------------------------------------------------------
    def image(self, data, ext, max_w_in=4.6):
        w, h = _jpeg_size(data) if ext in ("jpg", "jpeg") else _png_size(data)
        if not w:
            return
        scale = min(1.0, max_w_in / (w / 96.0))
        cx, cy = int(w / 96.0 * scale * EMU), int(h / 96.0 * scale * EMU)
        name = f"image{len(self.media) + 1}.{ext}"
        self.media.append((name, data))
        rid = f"rIdImg{len(self.media)}"
        self.body.append(
            '<w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr><w:r><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{len(self.media)}" '
            f'name="{name}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{len(self.media)}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')

    # ---- table --------------------------------------------------------
    def table(self, rows, widths=None, header=True, band=True):
        if not rows:
            return
        ncol = max(len(r) for r in rows)
        widths = widths or [int(9360 / ncol)] * ncol
        grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
        out = ['<w:tbl><w:tblPr>'
               '<w:tblW w:w="9360" w:type="dxa"/>'
               '<w:tblBorders>'
               f'<w:top w:val="single" w:sz="8" w:color="{NAVY}"/>'
               f'<w:left w:val="single" w:sz="4" w:color="BFD3E6"/>'
               f'<w:bottom w:val="single" w:sz="8" w:color="{NAVY}"/>'
               f'<w:right w:val="single" w:sz="4" w:color="BFD3E6"/>'
               '<w:insideH w:val="single" w:sz="4" w:color="BFD3E6"/>'
               '<w:insideV w:val="single" w:sz="4" w:color="BFD3E6"/>'
               '</w:tblBorders>'
               '<w:tblCellMar>'
               '<w:top w:w="80" w:type="dxa"/><w:left w:w="110" w:type="dxa"/>'
               '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="110" w:type="dxa"/>'
               '</w:tblCellMar></w:tblPr>'
               f'<w:tblGrid>{grid}</w:tblGrid>']
        for ri, row in enumerate(rows):
            hdr = header and ri == 0
            trpr = '<w:trPr><w:tblHeader/></w:trPr>' if hdr else ""
            out.append(f"<w:tr>{trpr}")
            for ci in range(ncol):
                cell = row[ci] if ci < len(row) else ""
                if hdr:
                    fill = NAVY
                elif band and (ri % 2 == 0):
                    fill = PALE
                else:
                    fill = "FFFFFF"
                runs = self._run(cell, b=hdr, sz=19,
                                 color=("FFFFFF" if hdr else None))
                out.append(
                    f'<w:tc><w:tcPr><w:tcW w:w="{widths[ci]}" w:type="dxa"/>'
                    f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
                    '<w:vAlign w:val="top"/></w:tcPr>'
                    f'<w:p><w:pPr><w:spacing w:before="30" w:after="30"/></w:pPr>'
                    f'{runs}</w:p></w:tc>')
            out.append("</w:tr>")
        out.append("</w:tbl>")
        self.body.append("".join(out))
        self.para([self._run("")], space_after=80)

    def chart(self, title, rows, maxbar=28):
        """A labelled bar chart drawn with block characters."""
        self.para([self._run(title, b=True, sz=22, color=NAVY)],
                  space_before=200, space_after=80)
        peak = max((v for _l, v in rows), default=1) or 1
        table = [["", "", ""]]
        body = []
        for label, val in rows:
            bars = "\u25a0" * max(1, round(val / peak * maxbar))
            body.append([label, bars, str(val)])
        self.table([["Category", "Distribution", "n"]] + body,
                   widths=[3000, 5200, 1160])

    # ---- save ---------------------------------------------------------
    def save(self, path):
        rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
        for n, (name, _d) in enumerate(self.media, 1):
            rels.append(f'<Relationship Id="rIdImg{n}" '
                        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                        f'Target="media/{name}"/>')
        rels.append('<Relationship Id="rIdStyles" '
                    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
                    'Target="styles.xml"/>')
        rels.append("</Relationships>")

        doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<w:document '
               'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
               'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
               'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
               'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
               '<w:body>' + "".join(self.body) +
               '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
               '<w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080" '
               'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
               '</w:body></w:document>')

        styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                  '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                  '<w:docDefaults><w:rPrDefault><w:rPr>'
                  '<w:rFonts w:ascii="Arial Narrow" w:hAnsi="Arial Narrow" w:cs="Arial Narrow"/>'
                  '<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault>'
                  '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" '
                  'w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
                  '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>'
                  '</w:style></w:styles>')

        ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
              '<Default Extension="xml" ContentType="application/xml"/>',
              '<Default Extension="jpg" ContentType="image/jpeg"/>',
              '<Default Extension="jpeg" ContentType="image/jpeg"/>',
              '<Default Extension="png" ContentType="image/png"/>',
              '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>',
              '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>',
              '</Types>']

        root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                     '<Relationship Id="rId1" '
                     'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
                     'Target="word/document.xml"/></Relationships>')

        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", "".join(ct))
            z.writestr("_rels/.rels", root_rels)
            z.writestr("word/document.xml", doc)
            z.writestr("word/styles.xml", styles)
            z.writestr("word/_rels/document.xml.rels", "".join(rels))
            for name, data in self.media:
                z.writestr(f"word/media/{name}", data)


def _jpeg_size(d):
    i = 2
    while i < len(d) - 9:
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i + 1]
        if m in (0xC0, 0xC1, 0xC2, 0xC3):
            h, w = struct.unpack(">HH", d[i + 5:i + 9])
            return w, h
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        i += 2 + struct.unpack(">H", d[i + 2:i + 4])[0]
    return None, None


def _png_size(d):
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        return None, None
    w, h = struct.unpack(">II", d[16:24])
    return w, h
