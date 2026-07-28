"""Produce a readable phone copy from a verified LibreCAD PDF export.

The primary drawing is the native DXF.  LibreCAD 2.2 on this host prints thin
CAD strokes as near-white pixels; this makes a clearly marked screen copy from
that actual export, without changing its geometry or annotations.
"""
from pathlib import Path
import subprocess
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "drawings" / "hda1_p2_ga06_export_current.pdf"
OUT = ROOT / "output" / "drawings" / "hda1_p2_ga06_screen_copy_ru.pdf"
RASTER = ROOT / "output" / "drawings" / "_ga06_librecad_300"
PNG = ROOT / "output" / "drawings" / "_ga06_librecad_300-1.png"
POPPLER = Path(r"C:\Users\Vladimir\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")

if not SOURCE.exists() or SOURCE.stat().st_size < 100_000:
    raise FileNotFoundError("verified LibreCAD source PDF was not found")
subprocess.run([str(POPPLER), "-png", "-r", "300", "-f", "1", "-l", "1", str(SOURCE), str(RASTER)], check=True)

im = ImageOps.grayscale(Image.open(PNG))
# Darken every CAD stroke below very light grey while retaining the white sheet.
ink = im.point(lambda p: 0 if p < 242 else 255)
box = ImageOps.invert(ink).getbbox()
if box is None:
    raise RuntimeError("LibreCAD output contains no visible drawing")
pad = 30
box = (max(0, box[0]-pad), max(0, box[1]-pad), min(im.width, box[2]+pad), min(im.height, box[3]+pad))
ink = ink.crop(box)
screen = ROOT / "output" / "drawings" / "_ga06_screen_ink.png"
ink.save(screen, optimize=True)

w, h = landscape(A4)
c = canvas.Canvas(str(OUT), pagesize=(w, h))
font = Path(r"C:\Windows\Fonts\arial.ttf")
font_bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
pdfmetrics.registerFont(TTFont("HDAArial", str(font)))
pdfmetrics.registerFont(TTFont("HDAArialBold", str(font_bold)))
c.setFillColorRGB(0.12, 0.20, 0.30)
c.setFont("HDAArialBold", 8)
c.drawString(18, h-14, "GA-06 · экранная копия из нативного DXF, экспортированного LibreCAD")
c.setFillColorRGB(0.25, 0.25, 0.25)
c.setFont("HDAArial", 6.5)
c.drawRightString(w-18, h-14, "P2 · не для производства")
avail_w, avail_h = w-36, h-32
scale = min(avail_w/ink.width, avail_h/ink.height)
dw, dh = ink.width*scale, ink.height*scale
c.drawImage(ImageReader(ink), (w-dw)/2, 12+(avail_h-dh)/2, width=dw, height=dh, mask='auto')
c.save()
print(OUT)
