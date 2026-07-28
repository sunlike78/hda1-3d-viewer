"""GA-06: readable P2 reference drawing, as native DXF R2013.

This page intentionally uses conventional orthographic views.  The two open
helical ribbons are never represented by decorative crossing loops: in the
section their generated edges are shown, and in B-B their real 180-degree
spacing is shown.  Values are source dimensions of the FreeCAD P2 model.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_ga03_pro_dxf as base

OUT = ROOT / "output" / "drawings" / "hda1_p2_ga06_detailed_projections_ru.dxf"


def balloon(d, n, bx, by, tx, ty):
    d.line("DIM", bx, by, tx, ty)
    d.circle("TITLE", bx, by, 4.1)
    d.text("TITLE", bx - 1.35, by - 1.35, 2.7, 4, str(n))


def main():
    base.OUT = OUT
    d = base.D()
    # Frame: A3 landscape. Drawing regions deliberately consume the sheet.
    d.rect("OUTLINE", 0, 0, 420, 297)
    d.rect("OUTLINE", 10, 10, 400, 277)
    d.text("TITLE", 15, 279, 5.6, 290, "HDA-1 - УЗЕЛ СМЕШИВАНИЯ И ВСПЕНИВАНИЯ")
    d.text("TEXT", 15, 270, 2.8, 290, "GA-06 - СБОРОЧНЫЕ ПРОЕКЦИИ P2 - масштаб 1:2 - размеры в мм")
    d.text("TEXT", 15, 264, 2.35, 290, "Геометрия выведена по параметрам HDA1_P2_Master.FCStd; лист P2 не является рабочей КД.")

    # A-A, main longitudinal section (true dimensions at scale 1:2).
    s, ox, oy = .5, 118, 55
    x = lambda v: ox + s*v
    y = lambda v: oy + s*v
    R = lambda layer,a,b,w,h: d.rect(layer, x(a), y(b), s*w, s*h)
    L = lambda layer,a,b,c,e: d.line(layer, x(a), y(b), x(c), y(e))
    # chamber / lid / removable bowl with a solid bottom
    R("OUTLINE", -107.5, 0, 215, 142)
    R("OUTLINE", -105, 3, 210, 129)
    R("OUTLINE", -118, 142, 236, 10)
    R("OUTLINE", -130, 152, 260, 10)
    R("OUTLINE", -77.5, 3, 155, 97)
    R("OUTLINE", -75, 6, 150, 94)
    # top-only shaft: its lower end is clear of form floor by 8 mm
    R("OUTLINE", -10, 14, 20, 208)
    R("OUTLINE", -18, 89, 36, 16)  # tool hub
    # two actual open ribbon edges in section, each is a distinct inclined band
    for sx in (-1, 1):
        L("OUTLINE", sx*63, 18, sx*40, 50)
        L("OUTLINE", sx*60, 18, sx*37, 50)
        L("OUTLINE", sx*40, 50, sx*63, 84)
        L("OUTLINE", sx*37, 50, sx*60, 84)
    # guide / cut hatching, centreline, no text inside geometry
    L("CENTER", 0, -16, 0, 172)
    for yy in range(6, 132, 15):
        L("HATCH", -106, yy, -96, yy+10); L("HATCH", 96, yy, 106, yy+10)
    for xx in range(-116, 117, 19): L("HATCH", xx, 143, xx+9, 152)
    # pressure port / independent relief valve on right, respectively positions 8/9
    R("OUTLINE", 105, 106, 38, 12); d.circle("OUTLINE", x(145), y(112), 5)
    R("OUTLINE", 105, 78, 34, 13); d.circle("OUTLINE", x(143), y(84.5), 7)
    # dimensions outside the main geometry
    d.hdim(x(-107.5), x(107.5), y(0), y(-31), "Ø215 камера")
    d.hdim(x(-75), x(75), y(3), y(-18), "Ø150 форма")
    d.vdim(x(107.5), x(145), y(0), y(142), "142")
    d.vdim(x(77.5), x(117), y(3), y(100), "95")
    # The captions live below all dimension strings, avoiding a common drawing error.
    d.text("TEXT", 17, 29, 3.4, 170, "РАЗРЕЗ A-A - ЧАША СО СПЛОШНЫМ ДНОМ; НИЖНЕЙ ОПОРЫ ВАЛА НЕТ")
    d.text("DIM", 20, 23, 2.6, 170, "Вал Ø20; орган A Ø134; радиальный зазор 8; зазор до дна 8")
    # callouts are leaders linked to a single balloon each
    balloon(d, 1, 22, 113, x(-106), y(95))
    balloon(d, 2, 34, 75, x(-75), y(42))
    balloon(d, 3, 76, 99, x(-55), y(52))
    balloon(d, 4, 38, 145, x(-88), y(154))
    balloon(d, 5, 105, 163, x(0), y(170))
    balloon(d, 6, 122, 168, x(0), y(185))
    balloon(d, 8, 208, 111, x(125), y(112))
    balloon(d, 9, 207, 82, x(123), y(84.5))

    # B-B: plan at ribbon level. Two rectangular radial sections at 180 degrees.
    cx, cy = 296, 145
    d.circle("OUTLINE", cx, cy, 53.75)
    d.circle("OUTLINE", cx, cy, 37.5)
    d.circle("OUTLINE", cx, cy, 33.5)
    d.circle("OUTLINE", cx, cy, 5)
    d.rect("OUTLINE", cx+5, cy-3.5, 28.5, 7)
    d.rect("OUTLINE", cx-33.5, cy-3.5, 28.5, 7)
    d.line("CENTER", cx-62, cy, cx+62, cy); d.line("CENTER", cx, cy-62, cx, cy+62)
    d.text("TITLE", 238, 208, 3.7, 140, "СЕЧЕНИЕ B-B - УРОВЕНЬ ЛЕНТ")
    d.text("TEXT", 238, 201, 2.7, 145, "Две открытые ленты; разнос 180°; наружный диаметр 134")
    d.hdim(cx-37.5, cx+37.5, cy-37.5, cy-48, "Ø150")
    d.hdim(cx-33.5, cx+33.5, cy-33.5, cy-57, "Ø134")

    # Right elevation: external head and the eight-lug lock, separate from main section.
    d.rect("OUTLINE", 238, 52, 88, 26)
    d.rect("OUTLINE", 246, 78, 72, 63)
    d.rect("OUTLINE", 258, 141, 48, 11)
    d.rect("OUTLINE", 272, 152, 20, 30)
    for xx in (244, 260, 276, 292, 308): d.rect("OUTLINE", xx, 73, 7, 8)
    d.text("TITLE", 238, 45, 3.4, 110, "ВИД СПЕРЕДИ")
    d.text("TEXT", 238, 38, 2.55, 115, "8-позиционный замок; сухая головка\nс 2 подшипниками Ø20")
    balloon(d, 7, 339, 166, 291, 167)

    # Position table is separate; text has no leaders crossing a view.
    d.rect("OUTLINE", 335, 75, 65, 138)
    d.rect("TITLE", 335, 204, 65, 9)
    d.text("TITLE", 338, 207, 2.7, 58, "ПОЗИЦИИ")
    rows = [
        "1 Камера Ø215 x 142",
        "2 Форма Ø150 x 95",
        "3 Орган A: 2 ленты 180°",
        "4 Крышка и замок",
        "5 Вал Ø20; вылет 120",
        "6 Сухая головка",
        "7 BLDC привод P2",
        "8 Мех. пред. клапан",
        "9 Подача / выпуск воздуха",
    ]
    yy = 197
    for row in rows:
        d.line("OUTLINE", 335, yy-4, 400, yy-4)
        d.text("TEXT", 338, yy, 2.35, 58, row)
        yy -= 13

    # Notes, title block.
    d.rect("OUTLINE", 238, 218, 162, 38)
    d.text("TITLE", 242, 250, 3.2, 150, "КОНТРОЛЬНЫЕ УСЛОВИЯ P2")
    d.text("TEXT", 242, 242, 2.45, 152,
           "Стендовые точки давления: +20 / +40 / +60 кПа.\n"
           "Вал: пик 24 Н·м; расчётный прогиб 0,095 мм.\n"
           "Рабочий орган - единая сборка со ступицей и радиальными связями.\n"
           "До изготовления: FEM, ресурс, замок, камера и протокол испытаний.")
    d.rect("OUTLINE", 245, 14, 155, 28); d.line("OUTLINE", 245, 25, 400, 25); d.line("OUTLINE", 324, 14, 324, 42)
    d.text("TITLE", 249, 35, 3.9, 70, "HDA-1 / GA-06")
    d.text("TEXT", 249, 20, 2.7, 70, "СБОРКА P2 · 1:2")
    d.text("TEXT", 328, 35, 2.5, 68, "ПРЕДВАРИТЕЛЬНЫЙ\nНЕ ДЛЯ ПРОИЗВОДСТВА")
    d.save()
    print(OUT)


if __name__ == "__main__":
    main()
