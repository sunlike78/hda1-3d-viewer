"""Read-only integrity check of the saved native FreeCAD P2 assembly.

Run with FreeCADCmd, so this validates the FCStd BRep rather than a render.
"""
from pathlib import Path
import FreeCAD as App

ROOT = Path(r"C:\AI\Constructor\hda1_main_node")
MODEL = ROOT / "output" / "freecad" / "HDA1_P2_Master.FCStd"

doc = App.openDocument(str(MODEL))
required = {
    "PressureChamber", "RemovableBowl", "DoubleRibbonTool", "WetShaft",
    "Lid", "LockRing", "BearingCartridge", "ReliefValve", "AirPort",
}
missing = required - {o.Name for o in doc.Objects}
assert not missing, f"missing objects: {sorted(missing)}"

for name in required:
    obj = doc.getObject(name)
    assert obj.Shape.Volume > 0, f"{name}: empty shape"

tool = doc.getObject("DoubleRibbonTool").Shape
assert len(tool.Solids) == 2, f"expected exactly two ribbon solids, got {len(tool.Solids)}"
bowl = doc.getObject("RemovableBowl").Shape
shaft = doc.getObject("WetShaft").Shape
assert bowl.BoundBox.ZMin == 5.0, "unexpected bowl datum"
assert shaft.BoundBox.ZMin == 8.0, "shaft geometry below intended lower clearance"
assert doc.getObject("BearingCartridge").Shape.BoundBox.ZMin >= 164.0, "bearing is not in dry head"

print("PASS native FreeCAD BRep integrity")
print("objects", len(doc.Objects), "ribbon_solids", len(tool.Solids))
App.closeDocument(doc.Name)
