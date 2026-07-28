"""Generate GA-03 as a clean preliminary assembly drawing in DXF R2013.

The intent is a readable CAD sheet, not a presentation poster.  Geometry is
at 1:2 on an A3 sheet; displayed dimensions are true millimetres.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "drawings" / "hda1_p2_ga03_preliminary_ru_v4.dxf"


def esc(s: str) -> str:
    # The LibreCAD cyrillic_ii.lff font consumes the standard DXF Unicode
    # escape sequence; this keeps the file ASCII-safe and CAD-portable.
    s = s.replace("\n", r"\P").replace("Ø", "%%c").replace("·", "-").replace("—", "-").replace("–", "-")
    return "".join(ch if ord(ch) < 128 else f"\\U+{ord(ch):04X}" for ch in s)


class D:
    def __init__(self): self.v = []
    def p(self, c, x): self.v += [str(c), str(x)]
    def line(self, lay, x1, y1, x2, y2):
        for c, x in [(0,"LINE"),(8,lay),(10,x1),(20,y1),(30,0),(11,x2),(21,y2),(31,0)]: self.p(c,x)
    def rect(self, lay, x, y, w, h):
        self.line(lay,x,y,x+w,y); self.line(lay,x+w,y,x+w,y+h); self.line(lay,x+w,y+h,x,y+h); self.line(lay,x,y+h,x,y)
    def circle(self, lay, x, y, r):
        for c, q in [(0,"CIRCLE"),(8,lay),(10,x),(20,y),(30,0),(40,r)]: self.p(c,q)
    def arc(self, lay, x, y, r, a, b):
        for c, q in [(0,"ARC"),(8,lay),(10,x),(20,y),(30,0),(40,r),(50,a),(51,b)]: self.p(c,q)
    def text(self, lay, x, y, h, width, s):
        for c,q in [(0,"MTEXT"),(100,"AcDbEntity"),(8,lay),(100,"AcDbMText"),(10,x),(20,y),(30,0),(40,h),(41,width),(71,1),(1,esc(s)),(7,"cyrillic_ii")]: self.p(c,q)
    def hdim(self, x1,x2,yobj,ydim,label):
        # Extension lines, a dimension line and 45-degree closed arrowheads.
        self.line("DIM",x1,yobj,x1,ydim); self.line("DIM",x2,yobj,x2,ydim); self.line("DIM",x1,ydim,x2,ydim)
        a=2.1
        self.line("DIM",x1,ydim,x1+a,ydim+a); self.line("DIM",x1,ydim,x1+a,ydim-a)
        self.line("DIM",x2,ydim,x2-a,ydim+a); self.line("DIM",x2,ydim,x2-a,ydim-a)
        self.text("DIM",(x1+x2)/2-17,ydim+2.2,2.8,34,label)
    def vdim(self,xobj,xdim,y1,y2,label):
        self.line("DIM",xobj,y1,xdim,y1); self.line("DIM",xobj,y2,xdim,y2); self.line("DIM",xdim,y1,xdim,y2)
        a=2.1
        self.line("DIM",xdim,y1,xdim-a,y1+a); self.line("DIM",xdim,y1,xdim+a,y1+a)
        self.line("DIM",xdim,y2,xdim-a,y2-a); self.line("DIM",xdim,y2,xdim+a,y2-a)
        self.text("DIM",xdim+2.7,(y1+y2)/2+1.4,2.8,20,label)
    def save(self):
        h=["0","SECTION","2","HEADER","9","$ACADVER","1","AC1027","9","$DWGCODEPAGE","3","ANSI_1252","9","$INSUNITS","70","4","0","ENDSEC"]
        t=["0","SECTION","2","TABLES","0","TABLE","2","LAYER","70","6"]
        for n,col in [("0",7),("OUTLINE",7),("CENTER",3),("DIM",5),("HATCH",8),("TEXT",7),("TITLE",2)]:
            t += ["0","LAYER","2",n,"70","0","62",str(col),"6","CONTINUOUS"]
        styles=["0","TABLE","2","STYLE","70","1","0","STYLE","2","cyrillic_ii","70","0","40","0","41","1","50","0","71","0","42","2.5","3","cyrillic_ii.lff","4","","0","ENDTAB"]
        e=["0","SECTION","2","ENTITIES"]+self.v+["0","ENDSEC","0","EOF"]
        OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text("\n".join(h+t+["0","ENDTAB"]+styles+["0","ENDSEC"]+e)+"\n",encoding="ascii")


def main():
    d=D()
    # A3 landscape frame and title zone.
    d.rect("OUTLINE",0,0,420,297); d.rect("OUTLINE",10,10,400,277)
    d.text("TITLE",15,279,5.5,245,"HDA-1 · УЗЕЛ СМЕШИВАНИЯ И ВСПЕНИВАНИЯ")
    d.text("TEXT",15,271,2.8,220,"GA-03 · СБОРОЧНЫЙ ВИД · МАСШТАБ 1:2 · РАЗМЕРЫ В ММ")
    d.text("TEXT",15,265,2.4,220,"Предконструкторская проработка: для проверки компоновки, не для изготовления")
    # Section A-A, scale 1:2.  Work with local true-size coordinates.
    s,ox,oy=0.5,128,112
    x=lambda u:ox+s*u; y=lambda u:oy+s*u
    r=lambda lay,a,b,w,h:d.rect(lay,x(a),y(b),s*w,s*h)
    l=lambda lay,a,b,c,e:d.line(lay,x(a),y(b),x(c),y(e))
    c=lambda lay,a,b,rr:d.circle(lay,x(a),y(b),s*rr)
    a=lambda lay,xx,yy,rr,st,en:d.arc(lay,x(xx),y(yy),s*rr,st,en)
    # Chamber wall and cover; cut material receives diagonal hatching.
    r("OUTLINE",-107.5,0,215,142); r("OUTLINE",-105,3,210,129)
    r("OUTLINE",-120,142,240,16); r("OUTLINE",-130,128,260,14)
    r("OUTLINE",-77.5,2.5,155,97.5); r("OUTLINE",-75,2.5,150,95)
    # Shaft and double-ribbon mixing tool. The shaft ends clear of the bottom.
    r("OUTLINE",-10,10.5,20,205); c("OUTLINE",0,53,54)
    a("OUTLINE",0,53,54,210,330); a("OUTLINE",0,53,54,30,150)
    l("OUTLINE",-64,20,-35,78); l("OUTLINE",64,20,35,78)
    # Safety valve envelope, clearly separate from the section wall.
    c("OUTLINE",-126,90,10); r("OUTLINE",-131,52,10,30); r("OUTLINE",-148,56,17,8)
    # Centre line and controlled manual hatch (no text over geometry).
    l("CENTER",-145,71,-112,71); l("CENTER",112,71,145,71); l("CENTER",0,-18,0,176)
    for yy in range(8,132,14):
        l("HATCH",-106,yy,-96,yy+10); l("HATCH",96,yy,106,yy+10)
    for xx in range(-112,113,20): l("HATCH",xx,143,xx+10,153)
    # Outside dimensions: one chain per side, no collision with notes.
    d.hdim(x(-107.5),x(107.5),y(0),y(-40),"Ø215")
    d.hdim(x(-75),x(75),y(2.5),y(-25),"Ø150")
    d.vdim(x(107.5),x(147),y(0),y(142),"142")
    d.vdim(x(77.5),x(118),y(2.5),y(97.5),"95")
    d.text("TEXT",50,83,3.2,140,"РАЗРЕЗ А–А")
    d.text("TEXT",50,77,2.6,140,"Съёмная форма с цельным дном; нижней опоры вала нет")
    d.text("TEXT",50,72,2.6,140,"Зазор до дна 8; инструмент Ø134,02; радиальный зазор 7,99")
    # Top view is intentionally isolated in its own rectangle.
    tx,ty=313,137
    d.rect("OUTLINE",238,65,150,125)
    d.circle("OUTLINE",tx,ty,53.75); d.circle("OUTLINE",tx,ty,37.5); d.circle("OUTLINE",tx,ty,33.505); d.circle("OUTLINE",tx,ty,5)
    d.arc("OUTLINE",tx,ty,31,0,300); d.arc("OUTLINE",tx,ty,31,180,480)
    d.line("CENTER",tx-65,ty,tx+65,ty); d.line("CENTER",tx,ty-65,tx,ty+65)
    d.text("TEXT",266,198,3.2,110,"ВИД СВЕРХУ")
    d.text("TEXT",266,192,2.6,110,"Форма Ø150 · орган A Ø134,02")
    # Notes panel occupies a dedicated zone.
    d.rect("OUTLINE",238,210,150,45)
    d.text("TITLE",243,248,3.8,135,"ИСХОДНЫЕ ДАННЫЕ P2")
    d.text("TEXT",243,240,2.7,135,"Партия 350–500 г · форма 1,679 л\nВал Ø20 · пик 24 Н·м · прогиб 0,095\nИспытания давления: +20 / +40 / +60 кПа\n8 проушин крышки · независимый клапан")
    # Standardised title block.
    d.rect("OUTLINE",238,14,150,35); d.line("OUTLINE",238,28,388,28); d.line("OUTLINE",315,14,315,49)
    d.text("TITLE",243,41,3.7,67,"HDA-1 / GA-03")
    d.text("TEXT",243,22,2.6,67,"СБОРКА P2 · 1:2")
    d.text("TEXT",320,41,2.6,62,"ПРЕДКОНСТРУКТОРСКИЙ\nНЕ ДЛЯ ПРОИЗВОДСТВА")
    d.save(); print(OUT)


if __name__ == "__main__": main()
