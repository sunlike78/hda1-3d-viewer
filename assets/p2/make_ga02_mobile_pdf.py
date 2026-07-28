"""Create a phone-viewable PDF preview from the native GA-02 DXF geometry.

Page 1 reproduces the DXF entities at their native A3 coordinates.  Page 2
is a portrait quick-view with the verified P2 render and the main dimensions.
"""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


ROOT = Path(__file__).resolve().parents[1]
DXF = ROOT / "output" / "drawings" / "hda1_p2_ga02_ru.dxf"
OUT = ROOT / "output" / "drawings" / "hda1_p2_mobile_preview_ru.pdf"
RENDER = ROOT / "output" / "renders" / "hda1_p2_main_node_photoreal.png"
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")


def load_entities(path: Path):
    rows = path.read_text("ascii").splitlines()
    pairs = [(int(rows[i]), rows[i + 1]) for i in range(0, len(rows), 2)]
    result, cur = [], None
    for code, value in pairs:
        if code == 0:
            if cur and cur["kind"] in {"LINE", "CIRCLE", "ARC", "MTEXT"}:
                result.append(cur)
            cur = {"kind": value, "pairs": []}
        elif cur is not None:
            cur["pairs"].append((code, value))
    if cur and cur["kind"] in {"LINE", "CIRCLE", "ARC", "MTEXT"}:
        result.append(cur)
    return result


def prop(entity, code, default=0.0):
    for c, value in entity["pairs"]:
        if c == code:
            return value
    return default


def dxf_text(value: str) -> str:
    value = re.sub(r"\\U\+([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), value)
    return value.replace(r"\P", "\n").replace(r"\n", "\n")


def font_setup():
    pdfmetrics.registerFont(TTFont("HDA", str(FONT)))
    pdfmetrics.registerFont(TTFont("HDABold", str(FONT_BOLD)))


COLORS = {
    "OUTLINE": Color(0.12, 0.13, 0.15), "DIM": HexColor("#315F92"),
    "TEXT": Color(0.12, 0.13, 0.15), "CENTER": HexColor("#397D54"),
    "TITLE": HexColor("#173B63"), "0": Color(0.1, 0.1, 0.1),
}


def draw_dxf(c: canvas.Canvas, entities):
    c.setLineWidth(0.25 * mm)
    for entity in entities:
        layer = prop(entity, 8, "0")
        c.setStrokeColor(COLORS.get(layer, COLORS["0"]))
        kind = entity["kind"]
        if kind == "LINE":
            c.line(float(prop(entity, 10)) * mm, float(prop(entity, 20)) * mm,
                   float(prop(entity, 11)) * mm, float(prop(entity, 21)) * mm)
        elif kind == "CIRCLE":
            x, y, r = float(prop(entity, 10)), float(prop(entity, 20)), float(prop(entity, 40))
            c.circle(x * mm, y * mm, r * mm, stroke=1, fill=0)
        elif kind == "ARC":
            x, y, r = float(prop(entity, 10)), float(prop(entity, 20)), float(prop(entity, 40))
            start, end = float(prop(entity, 50)), float(prop(entity, 51))
            c.arc((x-r)*mm, (y-r)*mm, (x+r)*mm, (y+r)*mm, startAng=start, extent=end-start)
        elif kind == "MTEXT":
            x, y = float(prop(entity, 10)) * mm, float(prop(entity, 20)) * mm
            size, width = float(prop(entity, 40)) * mm, float(prop(entity, 41)) * mm
            text = dxf_text(prop(entity, 1, ""))
            c.setFillColor(COLORS.get(layer, COLORS["0"]))
            c.setFont("HDABold" if layer == "TITLE" else "HDA", size)
            textobj = c.beginText(x, y)
            textobj.setLeading(size * 1.16)
            # DXF MTEXT width is respected approximately by character wrapping.
            max_chars = max(12, int(width / (size * 0.56)))
            for source_line in text.splitlines():
                words, line = source_line.split(), ""
                for word in words:
                    proposed = (line + " " + word).strip()
                    if len(proposed) > max_chars and line:
                        textobj.textLine(line); line = word
                    else:
                        line = proposed
                textobj.textLine(line)
            c.drawText(textobj)


def make_pdf():
    font_setup()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=landscape((297 * mm, 420 * mm)))
    c.setTitle("HDA-1 — GA-02, P2")
    c.setAuthor("Vladimir Evseev / HDA-1")
    c.setSubject("Просмотровый лист GA-02; исходник — DXF R2013")
    draw_dxf(c, load_entities(DXF))
    c.showPage()

    w, h = A4
    c.setPageSize(A4)
    c.setFillColor(HexColor("#F5F7F8")); c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(HexColor("#173B63")); c.setFont("HDABold", 18)
    c.drawString(18*mm, h-20*mm, "HDA-1 · главный узел P2")
    c.setFillColor(HexColor("#46515B")); c.setFont("HDA", 9)
    c.drawString(18*mm, h-27*mm, "Предконструкторский просмотр. Не документ для производства.")
    if RENDER.exists():
        image = ImageReader(str(RENDER)); iw, ih = image.getSize(); target_w = w-36*mm; target_h = target_w*ih/iw
        c.drawImage(image, 18*mm, h-34*mm-target_h, width=target_w, height=target_h, preserveAspectRatio=True)
        y = h-42*mm-target_h
    else:
        y = h-45*mm
    c.setFillColor(HexColor("#173B63")); c.setFont("HDABold", 12)
    c.drawString(18*mm, y, "Что показано")
    c.setFillColor(Color(0.12, 0.13, 0.15)); c.setFont("HDA", 9.5)
    notes = [
        "• Бытовая партия: 350–500 г; съёмная форма Ø150 × 95 мм, 1,679 л.",
        "• Рабочий орган A: две открытые ленточные спирали Ø134,02 мм.",
        "• Вал Ø20 мм, передача через верхнюю муфту; нижней опоры в чаше нет.",
        "• Зазор до цельного дна формы — 8 мм; радиальный зазор — 7,99 мм.",
        "• Расчётный пик — 24 Н·м; испытательные давления: +20/+40/+60 кПа.",
    ]
    y -= 6*mm
    for note in notes:
        c.drawString(18*mm, y, note); y -= 6*mm
    c.setFillColor(HexColor("#315F92")); c.setFont("HDABold", 10)
    c.drawString(18*mm, 19*mm, "Технический лист — следующая страница (A3, альбомная).")
    c.setFillColor(HexColor("#46515B")); c.setFont("HDA", 8)
    c.drawString(18*mm, 13*mm, "Редактируемый первоисточник: hda1_p2_ga02_ru.dxf (DXF R2013).")
    c.save()
    print(OUT)


if __name__ == "__main__":
    make_pdf()
