"""Write a clean native DXF R2013 GA-02 sheet for HDA-1 P2.

The A3 sheet uses an explicit 1:2 scale: two 215-mm views cannot fit in the
400-mm usable width at 1:1 without overlap.  All displayed dimensions remain
true millimetres.  The file consists only of standard DXF line, arc, circle
and MTEXT entities.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "drawings" / "hda1_p2_ga02_ru.dxf"


def esc(text: str) -> str:
    text = text.replace("\n", r"\P")
    return "".join(ch if ord(ch) < 128 else f"\\U+{ord(ch):04X}" for ch in text)


class DXF:
    def __init__(self): self.e = []
    def p(self, c, v): self.e += [str(c), str(v)]
    def line(self, layer, x1, y1, x2, y2):
        self.p(0,"LINE"); self.p(8,layer); self.p(10,x1); self.p(20,y1); self.p(30,0); self.p(11,x2); self.p(21,y2); self.p(31,0)
    def rect(self, layer, x, y, w, h):
        self.line(layer,x,y,x+w,y); self.line(layer,x+w,y,x+w,y+h); self.line(layer,x+w,y+h,x,y+h); self.line(layer,x,y+h,x,y)
    def circle(self, layer, x, y, r):
        self.p(0,"CIRCLE"); self.p(8,layer); self.p(10,x); self.p(20,y); self.p(30,0); self.p(40,r)
    def arc(self, layer, x, y, r, start, end):
        self.p(0,"ARC"); self.p(8,layer); self.p(10,x); self.p(20,y); self.p(30,0); self.p(40,r); self.p(50,start); self.p(51,end)
    def text(self, layer, x, y, h, width, value):
        self.p(0,"MTEXT"); self.p(100,"AcDbEntity"); self.p(8,layer); self.p(100,"AcDbMText"); self.p(10,x); self.p(20,y); self.p(30,0); self.p(40,h); self.p(41,width); self.p(71,1); self.p(1,esc(value)); self.p(7,"Standard")
    def save(self):
        header=["0","SECTION","2","HEADER","9","$ACADVER","1","AC1027","9","$INSUNITS","70","4","0","ENDSEC"]
        tables=["0","SECTION","2","TABLES","0","TABLE","2","LAYER","70","5"]
        for name,color in [("0",7),("OUTLINE",7),("DIM",5),("TEXT",7),("CENTER",3),("TITLE",2)]:
            tables += ["0","LAYER","2",name,"70","0","62",str(color),"6","CONTINUOUS"]
        body=["0","SECTION","2","ENTITIES"]+self.e+["0","ENDSEC","0","EOF"]
        OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text("\n".join(header+tables+["0","ENDTAB","0","ENDSEC"]+body)+"\n",encoding="ascii")


def main():
    d=DXF()
    d.rect("OUTLINE",0,0,420,297); d.rect("OUTLINE",10,10,400,277)
    d.text("TITLE",15,278,6,300,"HDA-1 — ГЛАВНЫЙ УЗЕЛ P2 · СБОРКА")
    d.text("TEXT",15,270,3,300,"GA-02 · Бытовая партия 350–500 г · Размеры в мм · Масштаб 1:2 · P2 / не серийная КД")
    s,ox,oy=0.5,140,76
    x=lambda v:ox+s*v; y=lambda v:oy+s*v
    rect=lambda l,a,b,w,h:d.rect(l,x(a),y(b),s*w,s*h)
    line=lambda l,a,b,c,e:d.line(l,x(a),y(b),x(c),y(e))
    circ=lambda l,a,b,r:d.circle(l,x(a),y(b),s*r)
    arc=lambda l,a,b,r,u,v:d.arc(l,x(a),y(b),s*r,u,v)
    # Section A-A: sealed chamber, removable form and a top-supported shaft.
    rect("OUTLINE",-107.5,0,215,142); rect("OUTLINE",-105,3,210,129)
    rect("OUTLINE",-118,142,236,18); rect("OUTLINE",-130,128,260,14); line("OUTLINE",-112.5,143.5,112.5,143.5)
    rect("OUTLINE",-77.5,2.5,155,97.5); rect("OUTLINE",-75,2.5,150,95); rect("OUTLINE",-10,10.5,20,205)
    circ("OUTLINE",0,52,54); arc("OUTLINE",0,52,54,210,330); arc("OUTLINE",0,52,54,30,150)
    line("OUTLINE",-64,20,-35,78); line("OUTLINE",64,20,35,78); line("CENTER",-70,10.5,70,10.5)
    circ("OUTLINE",-125.5,90,10); rect("OUTLINE",-130.5,52,10,30); rect("OUTLINE",-147.5,56,17,8)
    # Dimension geometry (the numerical labels are unscaled true dimensions).
    d.line("DIM",x(-107.5),y(0),x(-107.5),y(-32)); d.line("DIM",x(107.5),y(0),x(107.5),y(-32)); d.line("DIM",x(-107.5),y(-32),x(107.5),y(-32))
    d.text("DIM",90,55,3,80,"НАРУЖ. Ø215")
    d.line("DIM",x(-75),y(2.5),x(-75),y(-18)); d.line("DIM",x(75),y(2.5),x(75),y(-18)); d.line("DIM",x(-75),y(-18),x(75),y(-18))
    d.text("DIM",105,62,3,70,"ФОРМА Ø150")
    d.line("DIM",x(107.5),y(0),x(145),y(0)); d.line("DIM",x(107.5),y(142),x(145),y(142)); d.line("DIM",x(145),y(0),x(145),y(142)); d.text("DIM",215,112,3,30,"142")
    d.line("DIM",x(77.5),y(2.5),x(98),y(2.5)); d.line("DIM",x(77.5),y(97.5),x(98),y(97.5)); d.line("DIM",x(98),y(2.5),x(98),y(97.5)); d.text("DIM",188,104,3,30,"95")
    d.text("TEXT",35,56,3,120,"РАЗРЕЗ А–А · ФОРМА СО СПЛОШНЫМ ДНОМ")
    d.text("DIM",35,49,3,120,"Зазор до дна 8 · нижней опоры вала нет")
    d.text("DIM",35,44,3,120,"Инструмент Ø134,02 · радиальный зазор 7,99")
    # Top view, completely separated from the section.
    tx,ty=315,135
    d.circle("OUTLINE",tx,ty,53.75); d.circle("OUTLINE",tx,ty,37.5); d.circle("OUTLINE",tx,ty,33.505); d.circle("OUTLINE",tx,ty,5)
    d.arc("OUTLINE",tx,ty,31,0,300); d.arc("OUTLINE",tx,ty,31,180,480)
    d.text("TEXT",258,198,4,125,"ВИД СВЕРХУ · ФОРМА Ø150 · ИНСТРУМЕНТ A Ø134,02")
    # Data panel and title block.
    d.rect("OUTLINE",235,210,165,48); d.text("TITLE",240,252,4,150,"ПРОВЕРЕННЫЕ ДАННЫЕ P2")
    d.text("TEXT",240,244,3,150,"Вал Ø20 · пик 24 Н·м · прогиб 0,095\nФорма 1,679 л · камера внутр. Ø210\nСтенд: +20 / +40 / +60 кПа\n8 проушин замка · независимый предохранительный клапан\nОрган A: две открытые ленточные спирали")
    d.rect("OUTLINE",250,12,160,28); d.line("OUTLINE",250,23,410,23); d.line("OUTLINE",330,12,330,40)
    d.text("TITLE",254,34,4,70,"HDA-1 / GA-02"); d.text("TEXT",254,19,3,70,"СБОРКА P2 · 1:2"); d.text("TEXT",334,34,3,70,"ПРЕДКОНСТРУКТОРСКИЙ\nНЕ ДЛЯ ПРОИЗВОДСТВА")
    d.save(); print(OUT)


if __name__ == "__main__": main()
