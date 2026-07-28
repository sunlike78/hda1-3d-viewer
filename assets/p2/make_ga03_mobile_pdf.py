"""Render the native GA-03 DXF into a phone-viewable PDF without rasterising it."""
from pathlib import Path
import make_ga02_mobile_pdf as renderer

ROOT = Path(__file__).resolve().parents[1]
renderer.DXF = ROOT / "output" / "drawings" / "hda1_p2_ga03_preliminary_ru_v4.dxf"
renderer.OUT = ROOT / "output" / "drawings" / "hda1_p2_ga03_mobile_preview_ru.pdf"
renderer.RENDER = ROOT / "output" / "renders" / "hda1_p2_main_node_photoreal.png"
renderer.make_pdf()
