"""Write a dependency-free DXF R2013 drawing sheet for HDA-1 P2.

The result is native CAD linework (layers, arcs, circles, text, title block),
not a raster image or an SVG poster.  Coordinates are millimetres on A3-L.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "drawings" / "hda1_p2_ga02_ru.dxf"


def u(text: str) -> str:
    """DXF-safe Unicode escape sequence, understood by AutoCAD-style MTEXT."""
    return "".join(ch if ord(ch) < 128 else f"\\U+{ord(ch):04X}" for ch in text)


class DXF:
    def __init__(self) -> None:
        self.e: list[str] = []

    def pair(self, code: int, value: object) -> None:
        self.e.extend([str(code), str(value)])

    def line(self, layer: str, x1: float, y1: float, x2: float, y2: float) -> None:
        self.pair(0, "LINE"); self.pair(8, layer)
        self.pair(10, x1); self.pair(20, y1); self.pair(30, 0)
        self.pair(11, x2); self.pair(21, y2); self.pair(31, 0)

    def circle(self, layer: str, x: float, y: float, r: float) -> None:
        self.pair(0, "CIRCLE"); self.pair(8, layer)
        self.pair(10, x); self.pair(20, y); self.pair(30, 0); self.pair(40, r)

    def arc(self, layer: str, x: float, y: float, r: float, start: float, end: float) -> None:
        self.pair(0, "ARC"); self.pair(8, layer)
        self.pair(10, x); self.pair(20, y); self.pair(30, 0); self.pair(40, r)
        self.pair(50, start); self.pair(51, end)

    def mtext(self, layer: str, x: float, y: float, h: float, width: float, text: str) -> None:
        self.pair(0, "MTEXT"); self.pair(100, "AcDbEntity"); self.pair(8, layer)
        self.pair(100, "AcDbMText"); self.pair(10, x); self.pair(20, y); self.pair(30, 0)
        self.pair(40, h); self.pair(41, width); self.pair(71, 1); self.pair(1, u(text)); self.pair(7, "Standard")

    def dim_h(self, x1: float, x2: float, y_obj: float, y_dim: float, label: str) -> None:
        layer = "DIM"
        self.line(layer, x1, y_obj, x1, y_dim); self.line(layer, x2, y_obj, x2, y_dim); self.line(layer, x1, y_dim, x2, y_dim)
        a = 2.0
        self.line(layer, x1, y_dim, x1 + a, y_dim + a); self.line(layer, x1, y_dim, x1 + a, y_dim - a)
        self.line(layer, x2, y_dim, x2 - a, y_dim + a); self.line(layer, x2, y_dim, x2 - a, y_dim - a)
        self.mtext(layer, (x1 + x2) / 2 - 22, y_dim - 3.2, 3.0, 44, label)

    def dim_v(self, x_obj: float, x_dim: float, y1: float, y2: float, label: str) -> None:
        layer = "DIM"
        self.line(layer, x_obj, y1, x_dim, y1); self.line(layer, x_obj, y2, x_dim, y2); self.line(layer, x_dim, y1, x_dim, y2)
        a = 2.0
        self.line(layer, x_dim, y1, x_dim + a, y1 + a); self.line(layer, x_dim, y1, x_dim - a, y1 + a)
        self.line(layer, x_dim, y2, x_dim + a, y2 - a); self.line(layer, x_dim, y2, x_dim - a, y2 - a)
        self.mtext(layer, x_dim + 3, (y1 + y2) / 2 + 4, 3.0, 40, label)

    def rect(self, layer: str, x: float, y: float, w: float, h: float) -> None:
        self.line(layer, x, y, x + w, y); self.line(layer, x + w, y, x + w, y + h)
        self.line(layer, x + w, y + h, x, y + h); self.line(layer, x, y + h, x, y)

    def save(self, path: Path) -> None:
        header = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1027", "9", "$INSUNITS", "70", "4", "0", "ENDSEC"]
        tables = ["0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", "5"]
        layers = [("0", 7), ("OUTLINE", 7), ("DIM", 5), ("TEXT", 7), ("CENTER", 3), ("TITLE", 2)]
        for name, color in layers:
            tables += ["0", "LAYER", "2", name, "70", "0", "62", str(color), "6", "CONTINUOUS"]
        tables += ["0", "ENDTAB", "0", "ENDSEC"]
        body = ["0", "SECTION", "2", "ENTITIES"] + self.e + ["0", "ENDSEC", "0", "EOF"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(header + tables + body) + "\n", encoding="ascii")


def main() -> None:
    d = DXF()
    # A3 landscape 420 x 297, 10 mm technical frame.
    d.rect("OUTLINE", 0, 0, 420, 297); d.rect("OUTLINE", 10, 10, 400, 277)
    d.mtext("TITLE", 15, 278, 6, 300, "HDA-1 — ГЛАВНЫЙ УЗЕЛ P2 · СБОРКА")
    d.mtext("TEXT", 15, 270, 3, 300, "GA-02 · Бытовая партия 350–500 г · Все размеры в мм · Статус: P2 / не серийная КД")

    # Longitudinal section, scale 1:1 in CAD (chamber ID 210, shell 2.5).
    cx, bottom = 125, 48
    chamber_i, chamber_o, h = 210, 215, 142
    x0, x1 = cx - chamber_o / 2, cx + chamber_o / 2
    y0, y1 = bottom, bottom + h
    d.rect("OUTLINE", x0, y0, chamber_o, h)
    d.rect("OUTLINE", cx - chamber_i / 2, y0 + 3, chamber_i, h - 13)
    # lid, ring, gasket
    d.rect("OUTLINE", cx - 118, y1, 236, 18); d.rect("OUTLINE", cx - 130, y1 - 14, 260, 14)
    d.line("OUTLINE", cx - 112.5, y1 + 1.5, cx + 112.5, y1 + 1.5)
    # P2 removable form inner Ø150 x 95, with 2.5 mm floor.
    d.rect("OUTLINE", cx - 77.5, y0 + 2.5, 155, 97.5)
    d.rect("OUTLINE", cx - 75, y0 + 2.5, 150, 95)
    # Upper shaft and P2-A double ribbon.  No lower support: shaft ends 8 above floor.
    d.rect("OUTLINE", cx - 10, y0 + 10.5, 20, 205)
    d.circle("OUTLINE", cx, y0 + 52, 54); d.arc("OUTLINE", cx, y0 + 52, 54, 210, 330)
    d.arc("OUTLINE", cx, y0 + 52, 54, 30, 150)
    d.line("OUTLINE", cx - 64, y0 + 20, cx - 35, y0 + 78); d.line("OUTLINE", cx + 64, y0 + 20, cx + 35, y0 + 78)
    # lower clear gap indicated as construction / centre layer, not support.
    d.line("CENTER", cx - 70, y0 + 10.5, cx + 70, y0 + 10.5)
    # safety valve envelope left side
    d.circle("OUTLINE", x0 - 18, y0 + 90, 10); d.rect("OUTLINE", x0 - 23, y0 + 52, 10, 30); d.rect("OUTLINE", x0 - 40, y0 + 56, 17, 8)

    # Orthographic top view, P2 tool and form.
    tx, ty = 325, 145
    d.circle("OUTLINE", tx, ty, 107.5); d.circle("OUTLINE", tx, ty, 75); d.circle("OUTLINE", tx, ty, 67.01); d.circle("OUTLINE", tx, ty, 10)
    d.arc("OUTLINE", tx, ty, 62, 0, 300); d.arc("OUTLINE", tx, ty, 62, 180, 480)
    d.mtext("TEXT", 276, 258, 4, 95, "ВИД СВЕРХУ · ФОРМА Ø150 · ИНСТРУМЕНТ A Ø134")

    # Dimensions
    d.dim_h(x0, x1, y0, 30, "НАРУЖ. Ø215")
    d.dim_h(cx - 75, cx + 75, y0 + 2.5, 22, "ВНУТР. ФОРМА Ø150")
    d.dim_v(x1, x1 + 20, y0, y1, "142")
    d.dim_v(cx + 77.5, cx + 45, y0 + 2.5, y0 + 97.5, "95")
    d.mtext("DIM", 22, 42, 3, 130, "ЗАЗОР ДО ЦЕЛЬНОГО ДНА 8 · НИЖНЕЙ ОПОРЫ ВАЛА НЕТ")
    d.mtext("DIM", 22, 37, 3, 130, "ИНСТРУМЕНТ Ø134,02 · РАДИАЛЬНЫЙ ЗАЗОР 7,99")

    # Notes and engineering data table on the upper right.
    d.rect("OUTLINE", 245, 198, 155, 62)
    d.mtext("TITLE", 250, 253, 4, 140, "ПРОВЕРЕННЫЕ ДАННЫЕ P2")
    d.mtext("TEXT", 250, 244, 3, 145,
            "Вал Ø20 · пик 24 Н·м · прогиб 0,095\n"
            "Форма: 1,679 л · камера: внутр. Ø210\n"
            "Стендовые давления: +20 / +40 / +60 кПа\n"
            "8 проушин замка · независимый предохранительный клапан\n"
            "Рабочий орган A: две открытые ленточные спирали")

    # Title block.
    d.rect("OUTLINE", 250, 12, 160, 28); d.line("OUTLINE", 250, 23, 410, 23); d.line("OUTLINE", 330, 12, 330, 40)
    d.mtext("TITLE", 254, 34, 4, 70, "HDA-1 / GA-02")
    d.mtext("TEXT", 254, 19, 3, 70, "СБОРКА P2 · 1:1")
    d.mtext("TEXT", 334, 34, 3, 70, "ПРЕДКОНСТРУКТОРСКИЙ\nНЕ ДЛЯ ПРОИЗВОДСТВА")
    d.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
