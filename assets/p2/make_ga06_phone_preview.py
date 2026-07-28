"""Create a phone-oriented vector preview from the LibreCAD GA-06 PDF.

The source remains the full native A3 DXF. LibreCAD 2.2's CLI emits an A4
portrait media box on this Windows build even when custom paper is requested;
this wrapper crops the actual vector drawing bounds and places them on an A4
landscape page without rasterising the drawing.
"""
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "drawings" / "hda1_p2_ga06_export_checked.pdf"
OUT = ROOT / "output" / "drawings" / "hda1_p2_ga06_phone_preview_ru.pdf"

if not SRC.exists() or SRC.stat().st_size < 10_000:
    raise FileNotFoundError(f"LibreCAD PDF is missing or invalid: {SRC}")

source = PdfReader(str(SRC)).pages[0]
# Measured against the actual LibreCAD output; leaves the DXF frame intact.
source.cropbox.lower_left = (0, 200)
source.cropbox.upper_right = (595, 630)
page = PdfWriter().add_blank_page(width=842, height=595)
# 595 × 430 crop scaled to 1.37 = 815 × 589; landscape mobile-readable.
page.merge_transformed_page(source, Transformation().scale(1.37).translate(tx=13, ty=-274))
writer = PdfWriter()
writer.add_page(page)
writer.add_metadata({"/Title": "HDA-1 P2 - GA-06 - LibreCAD mobile preview"})
with OUT.open("wb") as fh:
    writer.write(fh)
print(OUT)
