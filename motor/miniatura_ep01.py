import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import cairo
from desenho import *
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1280, 720)
ctx = cairo.Context(s)
ctx.scale(1280 / W, 720 / H)
parque(ctx, 0.0, hexc("#2E8FEA"), hexc("#9ED8FF"), (1720, 150))
# faixa do por do sol a direita
g = cairo.LinearGradient(1250, 0, W, 0)
g.add_color_stop_rgba(0, 1, 0.5, 0.37, 0)
g.add_color_stop_rgba(1, 1, 0.5, 0.37, 0.75)
ctx.rectangle(0, 0, W, 860); ctx.set_source(g); ctx.fill()
lume(ctx, 1450, 1150, 1.55, 0.5, "uau", (-0.3, -1), "aponta")
teco(ctx, 1000, 760, 0.9, 0.0, 0.0, (1, -0.5))
texto(ctx, "POR QUE O CÉU", 80, 260, 165, AMARELO, TINTA, 30, alinhar="esq")
texto(ctx, "É AZUL?", 80, 470, 205, BRANCO, TINTA, 34, alinhar="esq")
for i in range(3):
    texto(ctx, "?", 1700 + i * 70, 470 - i * 80, 110 + i * 20, BRANCO, TINTA, 16)
logo(ctx, 330, 900, 0.62, 0.0, 1.0)
s.write_to_png(sys.argv[1])
