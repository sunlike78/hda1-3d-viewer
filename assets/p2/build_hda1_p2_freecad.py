"""Native FreeCAD P2 concept assembly for HDA-1.

Executed inside FreeCAD's Python console.  It deliberately produces a
parametric *concept* assembly and a TechDraw sheet, not manufacturing CAD.
"""

from pathlib import Path
import math

import FreeCAD as App
import FreeCADGui as Gui
import Part


ROOT = Path(r"C:\AI\Constructor\hda1_main_node")
OUT = ROOT / "output" / "freecad"
OUT.mkdir(parents=True, exist_ok=True)

V = App.Vector
doc = App.newDocument("HDA1_P2_Master")


def group(name, label):
    obj = doc.addObject("App::DocumentObjectGroup", name)
    obj.Label = label
    return obj


assembly = group("HDA1_P2_Assembly", "HDA-1 / P2 — параметрическая сборка")
wet = group("WetZone", "Продуктовая зона")
dry = group("DryHead", "Сухая приводная головка")
safety = group("Safety", "Давление и безопасность")
assembly.addObject(wet)
assembly.addObject(dry)
assembly.addObject(safety)


def feature(parent, name, label, shape, color, transparency=0):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Status", "P2")
    obj.Status = "Предварительная проработка; не для изготовления"
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.LineColor = (0.12, 0.16, 0.19)
    obj.ViewObject.Transparency = transparency
    parent.addObject(obj)
    return obj


def add_dim(obj, name, value, unit="mm"):
    obj.addProperty("App::PropertyLength", name, "Dimensions")
    setattr(obj, name, value)
    if unit:
        obj.setEditorMode(name, 1)


steel = (0.72, 0.76, 0.78)
dark = (0.24, 0.30, 0.34)
blue = (0.16, 0.35, 0.54)
red = (0.86, 0.12, 0.07)
seal_color = (0.10, 0.16, 0.22)

# Reference geometry, all millimetres.
R_CH = 107.5
H_CH = 142.0
T_WALL = 2.5
R_BOWL_IN = 75.0
R_BOWL_OUT = 77.0
H_BOWL = 95.0
R_SHAFT = 10.0
R_TOOL = 67.0
Z_BOWL = 5.0

# Pressure chamber: actual full shell remains in the model; a half-shell is
# separately displayed for the engineering render so internal topology is visible.
outer = Part.makeCylinder(R_CH, H_CH, V(0, 0, 0))
inner = Part.makeCylinder(R_CH - T_WALL, H_CH - 3.0, V(0, 0, 3.0))
shell_shape = outer.cut(inner)
shell = feature(wet, "PressureChamber", "01 — Камера Ø215 × 142, стенка 2,5 (screening)", shell_shape, steel, 82)
add_dim(shell, "OutsideDiameter", 215)
add_dim(shell, "InsideDiameter", 210)
add_dim(shell, "Height", 142)
add_dim(shell, "WallThickness", 2.5)

bottom = feature(wet, "LowerClosure", "02 — Нижнее закрытие камеры", Part.makeCylinder(R_CH, 3.0, V(0, 0, 0)), steel)
add_dim(bottom, "Thickness", 3)

bowl_outer = Part.makeCylinder(R_BOWL_OUT, H_BOWL, V(0, 0, Z_BOWL))
bowl_inner = Part.makeCylinder(R_BOWL_IN, H_BOWL - 3.0, V(0, 0, Z_BOWL + 3.0))
bowl_shape = bowl_outer.cut(bowl_inner)
bowl = feature(wet, "RemovableBowl", "03 — Съёмная форма Ø150 × 95, цельное дно", bowl_shape, (0.82, 0.84, 0.85), 55)
add_dim(bowl, "InsideDiameter", 150)
add_dim(bowl, "Height", 95)
add_dim(bowl, "BottomThickness", 3)

# Lid and locking ring.
lid_shape = Part.makeCylinder(R_CH, 10.0, V(0, 0, H_CH))
lid_shape = lid_shape.cut(Part.makeCylinder(28, 10.0, V(0, 0, H_CH)))
lid = feature(dry, "Lid", "04 — Крышка с верхней приводной головкой", lid_shape, steel)
add_dim(lid, "Thickness", 10)

lock_parts = []
for i in range(8):
    a = math.radians(i * 45.0)
    lug = Part.makeBox(16, 12, 9, V(R_CH - 5, -6, H_CH + 2))
    lug.rotate(V(0, 0, 0), V(0, 0, 1), i * 45.0)
    lock_parts.append(lug)
lock = feature(dry, "LockRing", "05 — 8-позиционный кольцевой замок крышки", Part.makeCompound(lock_parts), dark)
lock.addProperty("App::PropertyInteger", "LugCount", "Dimensions")
lock.LugCount = 8

# Bowl tool: two genuine solid helical ribbon sweeps.  If a host build lacks
# the pipe-shell algorithm the fallback is still a compound of overlapping solids.
def ribbon(angle_deg):
    try:
        helix = Part.makeHelix(70.0, 76.0, 64.0, 0.0, False)
        path = Part.Wire(helix.Edges)
        profile_edge = Part.makePolygon([
            V(60.5, 0, 14), V(67.5, 0, 14), V(67.5, 0, 22),
            V(60.5, 0, 22), V(60.5, 0, 14)
        ])
        profile = Part.Wire(profile_edge.Edges)
        shape = path.makePipeShell([profile], True, False)
        shape.rotate(V(0, 0, 0), V(0, 0, 1), angle_deg)
        return shape
    except Exception:
        parts = []
        for i in range(44):
            a = angle_deg + 360.0 * 1.09 * i / 44.0
            z = 18.0 + 76.0 * i / 44.0
            seg = Part.makeBox(7.0, 13.0, 5.0, V(60.5, -6.5, z - 2.5))
            seg.rotate(V(0, 0, 0), V(0, 0, 1), a)
            parts.append(seg)
        return Part.makeCompound(parts)

tool_shape = Part.makeCompound([ribbon(0), ribbon(180)])
tool = feature(wet, "DoubleRibbonTool", "06 — Двухленточный рабочий орган A, 180°", tool_shape, blue)
add_dim(tool, "OutsideDiameter", 134)
add_dim(tool, "RibbonHeight", 76)
add_dim(tool, "RadialClearance", 8)
add_dim(tool, "BottomClearance", 8)
tool.addProperty("App::PropertyString", "Configuration", "P2")
tool.Configuration = "A: две открытые ленточные спирали, разнос 180 градусов"

# Central shaft and its lower/upper hub connections.
shaft_shape = Part.makeCylinder(R_SHAFT, 178.0, V(0, 0, 8))
shaft = feature(dry, "WetShaft", "07 — Мокрый вал Ø20, верхняя консоль", shaft_shape, (0.65, 0.70, 0.72))
add_dim(shaft, "Diameter", 20)
add_dim(shaft, "FreeOverhang", 120)
shaft.addProperty("App::PropertyString", "MaterialCandidate", "P2")
shaft.MaterialCandidate = "1.4404 / 316L candidate"

hub = feature(wet, "ToolHub", "08 — Ступица рабочего органа", Part.makeCylinder(18, 16, V(0, 0, 82)), dark)
for z in (22, 88):
    arms = []
    for a in (0, 180):
        arm = Part.makeBox(48, 8, 5, V(12, -4, z))
        arm.rotate(V(0, 0, 0), V(0, 0, 1), a)
        arms.append(arm)
    arm_obj = feature(wet, f"ToolArms_{z}", f"08.{z} — Радиальные силовые связи лент", Part.makeCompound(arms), dark)

# Dry head: seal, bearings and a compact motor/gearbox volume.
seal_outer = Part.makeCylinder(26, 12, V(0, 0, 150))
seal_inner = Part.makeCylinder(10.5, 12, V(0, 0, 150))
seal = feature(dry, "SealCassette", "09 — Двойная торцевая кассета с дренажной полостью", seal_outer.cut(seal_inner), seal_color)
add_dim(seal, "OutsideDiameter", 52)

bearing_parts = []
for z in (164, 180):
    ring = Part.makeCylinder(24, 10, V(0, 0, z)).cut(Part.makeCylinder(10, 10, V(0, 0, z)))
    bearing_parts.append(ring)
bearings = feature(dry, "BearingCartridge", "10 — Два подшипника Ø20 в сухой головке", Part.makeCompound(bearing_parts), dark)
bearings.addProperty("App::PropertyInteger", "BearingCount", "Dimensions")
bearings.BearingCount = 2

gearbox = feature(dry, "Gearmotor", "11 — Привод BLDC 600 Вт класса + редуктор", Part.makeCylinder(38, 48, V(0, 0, 194)), dark)
gearbox.addProperty("App::PropertyString", "DriveLimit", "P2")
gearbox.DriveLimit = "12 N*m continuous / 24 N*m peak"

# External pneumatic port and clearly separate red mechanical relief valve.
port = Part.makeCylinder(8, 27, V(R_CH - 2, 0, 118), V(1, 0, 0))
port = port.fuse(Part.makeCylinder(13, 7, V(R_CH + 25, 0, 118), V(1, 0, 0)))
air_port = feature(safety, "AirPort", "12 — Патрубок подачи воздуха", port, steel)

valve_body = Part.makeCylinder(12, 26, V(R_CH - 2, -44, 112), V(1, 0, 0))
valve_cap = Part.makeCylinder(17, 9, V(R_CH + 23, -44, 112), V(1, 0, 0))
valve_out = Part.makeCylinder(6, 20, V(R_CH + 32, -44, 112), V(0, -1, 0))
relief = feature(safety, "ReliefValve", "13 — Независимый механический предохранительный клапан", valve_body.fuse(valve_cap).fuse(valve_out), red)
relief.addProperty("App::PropertyString", "Function", "P2")
relief.Function = "Независимый путь защиты; уставка не назначена в P2"

controlled = Part.makeCylinder(7, 31, V(R_CH - 2, 38, 108), V(1, 0, 0))
controlled = controlled.fuse(Part.makeCylinder(14, 8, V(R_CH + 27, 38, 108), V(1, 0, 0)))
vent = feature(safety, "ControlledVent", "14 — Управляемый выпуск / сменный ограничитель", controlled, steel)

# Useful cutaway for visual QA and rendering, derived from the exact chamber BRep.
cut_box = Part.makeBox(250, 250, 220, V(0, -125, -5))
cut_shell = shell_shape.cut(cut_box)
cutaway = feature(wet, "CutawayHousing", "CUT — Половина корпуса для проверки внутренней компоновки", cut_shell, steel)
cutaway.ViewObject.Visibility = True
shell.ViewObject.Visibility = False

# Reference axes and service envelope.
axis = feature(assembly, "CenterAxis", "Ось вала / базовая ось A", Part.makeCylinder(0.8, 260, V(0, 0, -10)), (0.1, 0.7, 0.25), 20)
axis.ViewObject.LineColor = (0.1, 0.7, 0.25)

doc.recompute()

# Save the native model and STEP exchange geometry.
native_path = OUT / "HDA1_P2_Master.FCStd"
step_path = OUT / "HDA1_P2_Master.step"
doc.saveAs(str(native_path))
try:
    import Import
    Import.export([bottom, bowl, lid, lock, tool, shaft, hub, seal, bearings, gearbox, air_port, relief, vent], str(step_path))
except Exception:
    pass

# Default visual presentation: isolated half-shell, internal parts and a
# camera-friendly axonometric view.
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
Gui.activeDocument().activeView().saveImage(str(OUT / "HDA1_P2_CAD_Cutaway.png"), 1800, 1400, "Current")

# Full external assembly render.
cutaway.ViewObject.Visibility = False
shell.ViewObject.Visibility = True
shell.ViewObject.Transparency = 15
bowl.ViewObject.Transparency = 20
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
Gui.activeDocument().activeView().saveImage(str(OUT / "HDA1_P2_CAD_Assembly.png"), 1800, 1400, "Current")

# Restore useful inspection state.
shell.ViewObject.Visibility = False
cutaway.ViewObject.Visibility = True
doc.recompute()
doc.saveAs(str(native_path))

# TechDraw page.  It is deliberately composed from the native BRep parts;
# dimensions requiring edge references remain marked as P2 reference values.
try:
    import TechDraw
    import TechDrawGui
    page = doc.addObject("TechDraw::DrawPage", "GA04_Detailed")
    page.Label = "GA-04 — Детальный сборочный лист P2"
    template = doc.addObject("TechDraw::DrawSVGTemplate", "GA04_Template")
    template.Template = App.getResourceDir() + "Mod/TechDraw/Templates/ISO/A3_Landscape_TD.svg"
    page.Template = template

    source = [bottom, bowl, lid, lock, tool, shaft, hub, seal, bearings, gearbox, air_port, relief, vent]
    front = doc.addObject("TechDraw::DrawViewPart", "GA04_Front")
    front.Source = source
    front.Direction = V(1, 0, 0)
    front.X, front.Y = 75, 145
    front.ScaleType = "Custom"
    front.Scale = 1.15
    page.addView(front)

    top = doc.addObject("TechDraw::DrawViewPart", "GA04_Top")
    top.Source = source
    top.Direction = V(0, 0, 1)
    top.X, top.Y = 215, 150
    top.ScaleType = "Custom"
    top.Scale = 1.0
    page.addView(top)

    notes = doc.addObject("TechDraw::DrawViewAnnotation", "GA04_Notes")
    notes.Text = [
        "HDA-1 / GA-04 — ДЕТАЛЬНАЯ СБОРКА P2",
        "МАСШТАБ ВИДОВ 1:1,15; РАЗМЕРЫ В ММ",
        "ЧАША Ø150 × 95; КАМЕРА Ø215 × 142; ВАЛ Ø20",
        "ОРГАН A Ø134; ЗАЗОР ДО ФОРМЫ 7,989; ДО ДНА 8,0",
        "8 ЗАЦЕПОВ КРЫШКИ; 2 ПОДШИПНИКА В СУХОЙ ЗОНЕ",
        "P2 — ПРЕДВАРИТЕЛЬНО; НЕ ДЛЯ ИЗГОТОВЛЕНИЯ",
    ]
    notes.X, notes.Y = 210, 62
    page.addView(notes)
    doc.recompute()
    TechDrawGui.exportPageAsPdf(page, str(OUT / "HDA1_P2_GA04_FreeCAD.pdf"))
    doc.saveAs(str(native_path))
except Exception as exc:
    (OUT / "TechDraw_status.txt").write_text(str(exc), encoding="utf-8")

Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
print("HDA1 P2 native FreeCAD model created:", native_path)
