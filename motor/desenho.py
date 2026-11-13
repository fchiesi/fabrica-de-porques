"""Primitivas de desenho, personagens (Lume e Teco) e cenarios reutilizaveis.

Estilo do canal: vetor chapado, contorno azul-marinho grosso e arredondado,
cores saturadas mas nao neon. Tudo em 1920x1080.
"""
import math, random
import cairo

W, H = 1920, 1080
PI = math.pi


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


TINTA = hexc("#1D2A4A")
BRANCO = hexc("#FFFFFF")
PELE_LUME = hexc("#A0663F")
CABELO = hexc("#2B1B14")
AMARELO = hexc("#FFC93C")
AZUL_SHORT = hexc("#3D6FD8")
VERMELHO = hexc("#E8505B")
TECO = hexc("#2EC4B6")
TECO_ESC = hexc("#1F9E93")
TELA = hexc("#10233F")
CIANO = hexc("#7FF0FF")
GRAMA = hexc("#7CCB5B")
GRAMA_ESC = hexc("#5BAE45")
CEU_TOPO = hexc("#4FA9F5")
CEU_BASE = hexc("#BFE6FF")
SOL = hexc("#FFD93D")

ESPECTRO = [hexc("#FF4D4D"), hexc("#FF9F1C"), hexc("#FFE24D"), hexc("#4CD964"), hexc("#3D8BFF"), hexc("#8E5CFF")]


# ---------------------------------------------------------------- utilidades
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def suave(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def pop(x):
    """0->1 com leve passada (easeOutBack)."""
    x = clamp01(x)
    if x >= 1:
        return 1.0
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def janela(t, a, b):
    return clamp01((t - a) / (b - a)) if b > a else float(t >= a)


def lerp(a, b, k):
    return a + (b - a) * k


def mistura(c1, c2, k):
    return tuple(lerp(a, b, k) for a, b in zip(c1, c2))


def cor(ctx, c):
    ctx.set_source_rgba(*c)


def preencher(ctx, fundo, lw=6, contorno=TINTA):
    cor(ctx, fundo)
    if lw:
        ctx.fill_preserve()
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        cor(ctx, contorno)
        ctx.stroke()
    else:
        ctx.fill()


def circulo(ctx, x, y, r):
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * PI)


def elipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * PI)
    ctx.restore()


def retarr(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -PI / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, PI / 2)
    ctx.arc(x + r, y + h - r, r, PI / 2, PI)
    ctx.arc(x + r, y + r, r, PI, 3 * PI / 2)
    ctx.close_path()


def estrela(ctx, x, y, r, pontas=5, giro=-PI / 2, interno=0.45):
    ctx.new_sub_path()
    for i in range(pontas * 2):
        rr = r if i % 2 == 0 else r * interno
        a = giro + i * PI / pontas
        (ctx.move_to if i == 0 else ctx.line_to)(x + rr * math.cos(a), y + rr * math.sin(a))
    ctx.close_path()


def linha(ctx, pts, lw, c, cap=cairo.LINE_CAP_ROUND):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cap)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    cor(ctx, c)
    ctx.stroke()


def seta(ctx, x0, y0, x1, y1, c, lw=8, cabeca=22):
    linha(ctx, [(x0, y0), (x1, y1)], lw, c)
    a = math.atan2(y1 - y0, x1 - x0)
    ctx.new_path()
    ctx.move_to(x1 + math.cos(a) * cabeca * 0.6, y1 + math.sin(a) * cabeca * 0.6)
    ctx.line_to(x1 + math.cos(a + 2.5) * cabeca, y1 + math.sin(a + 2.5) * cabeca)
    ctx.line_to(x1 + math.cos(a - 2.5) * cabeca, y1 + math.sin(a - 2.5) * cabeca)
    ctx.close_path()
    cor(ctx, c)
    ctx.fill()


# --------------------------------------------------------------------- texto
def fonte(ctx, tam, peso=cairo.FONT_WEIGHT_BOLD, nome="Fredoka"):
    ctx.select_font_face(nome, cairo.FONT_SLANT_NORMAL, peso)
    ctx.set_font_size(tam)


def texto(ctx, s, x, y, tam, c=BRANCO, contorno=TINTA, lw=0, alinhar="centro", nome="Fredoka"):
    """y = linha de base do texto."""
    fonte(ctx, tam, nome=nome)
    e = ctx.text_extents(s)
    if alinhar == "centro":
        x0 = x - e.width / 2 - e.x_bearing
    elif alinhar == "dir":
        x0 = x - e.width - e.x_bearing
    else:
        x0 = x - e.x_bearing
    ctx.new_path()
    ctx.move_to(x0, y)
    ctx.text_path(s)
    if lw:
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        cor(ctx, contorno)
        ctx.stroke_preserve()
    cor(ctx, c)
    ctx.fill()
    return e


def pilula(ctx, s, x, y, tam, fundo=BRANCO, cor_txt=TINTA, prog=1.0, pad=0.55):
    """Etiqueta arredondada centrada em (x, y), com entrada 'pop'."""
    k = pop(prog)
    if k <= 0.001:
        return
    fonte(ctx, tam)
    e = ctx.text_extents(s)
    w, h = e.width + tam * pad * 2, tam * 1.55
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    ctx.push_group()
    retarr(ctx, -w / 2 + 6, -h / 2 + 8, w, h, h / 2)
    cor(ctx, hexc("#000000", 0.18))
    ctx.fill()
    retarr(ctx, -w / 2, -h / 2, w, h, h / 2)
    preencher(ctx, fundo, 6)
    texto(ctx, s, 0, tam * 0.36, tam, cor_txt)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(clamp01(prog * 3))
    ctx.restore()


# ---------------------------------------------------------------- personagens
def _braco(ctx, pts, pele):
    linha(ctx, pts, 30, TINTA)
    linha(ctx, pts, 19, pele)
    ctx.new_path()
    circulo(ctx, pts[-1][0], pts[-1][1], 15)
    preencher(ctx, pele, 5)


def lume(ctx, x, y, s, t, expr="feliz", olhar=(0.0, 0.0), braco="baixo", seed=0.0):
    """Lume, 8 anos, curiosa. (x, y) = pes. Altura ~ 470*s."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    resp = math.sin(t * 2.4 + seed) * 3

    # pernas e tenis
    for sx in (-1, 1):
        retarr(ctx, sx * 30 - 13, -115, 26, 105, 12)
        preencher(ctx, PELE_LUME, 5)
        elipse(ctx, sx * 36, -10, 32, 17)
        preencher(ctx, VERMELHO, 5)
    # short
    retarr(ctx, -64, -158 + resp, 128, 66, 22)
    preencher(ctx, AZUL_SHORT, 6)

    # bracos atras do corpo quando abaixados
    ombro_e, ombro_d = (-56, -246 + resp), (56, -246 + resp)
    w = math.sin(t * 9) * 22
    poses = {
        "baixo": ([ombro_e, (-82, -200), (-86, -150)], [ombro_d, (82, -200), (86, -150)]),
        "aponta": ([ombro_e, (-82, -200), (-86, -150)], [ombro_d, (115, -280), (165, -335)]),
        "acena": ([ombro_e, (-82, -200), (-86, -150)], [ombro_d, (120, -290), (130 + w, -370)]),
        "queixo": ([ombro_e, (-82, -200), (-86, -150)], [ombro_d, (70, -190), (22, -268)]),
        "alto": ([ombro_e, (-115, -300), (-135 + w * 0.3, -385)], [ombro_d, (115, -300), (135 - w * 0.3, -385)]),
    }
    be, bd = poses.get(braco, poses["baixo"])

    # tronco
    retarr(ctx, -66, -272 + resp, 132, 132, 42)
    preencher(ctx, AMARELO, 6)
    estrela(ctx, 0, -205 + resp, 22)
    preencher(ctx, BRANCO, 4)
    _braco(ctx, be, PELE_LUME)
    if braco != "queixo":
        _braco(ctx, bd, PELE_LUME)

    # cabeca
    cy = -338 + resp
    for px in (-84, 84):  # puffs
        circulo(ctx, px, cy - 62, 56)
        preencher(ctx, CABELO, 6)
    circulo(ctx, 0, cy + 4, 94)
    preencher(ctx, CABELO, 6)
    retarr(ctx, -18, cy + 70, 36, 30, 8)
    preencher(ctx, PELE_LUME, 5)
    circulo(ctx, 0, cy + 8, 82)
    preencher(ctx, PELE_LUME, 6)
    # franja
    ctx.new_path()
    ctx.arc(0, cy + 2, 86, PI * 1.04, PI * 1.96)
    ctx.curve_to(70, cy - 10, 40, cy - 40, 10, cy - 30)
    ctx.curve_to(-20, cy - 48, -55, cy - 30, -86, cy - 4)
    ctx.close_path()
    preencher(ctx, CABELO, 0)
    estrela(ctx, 62, cy - 70, 20)
    preencher(ctx, AMARELO, 4)

    # olhos
    ox, oy = olhar
    pisca = ((t + seed * 1.7) % 3.9) < 0.13
    for sx in (-1, 1):
        ex, ey = sx * 31, cy + 10
        if pisca:
            linha(ctx, [(ex - 14, ey), (ex + 14, ey)], 6, TINTA)
            continue
        grande = 1.15 if expr == "uau" else 1.0
        elipse(ctx, ex, ey, 17 * grande, 21 * grande)
        preencher(ctx, BRANCO, 4)
        circulo(ctx, ex + ox * 6, ey + oy * 8, 10)
        cor(ctx, TINTA)
        ctx.fill()
        circulo(ctx, ex + ox * 6 + 3, ey + oy * 8 - 4, 3.5)
        cor(ctx, BRANCO)
        ctx.fill()
    # sobrancelhas
    for sx in (-1, 1):
        sobe = -10 if (expr == "pensa" and sx == 1) or expr == "uau" else 0
        linha(ctx, [(sx * 20, cy - 22 + sobe), (sx * 42, cy - 18 + sobe)], 6, CABELO)
    # bochechas
    for sx in (-1, 1):
        circulo(ctx, sx * 52, cy + 40, 12)
        cor(ctx, hexc("#FF7A8A", 0.45))
        ctx.fill()
    # boca
    my = cy + 50
    ctx.new_path()
    if expr == "uau":
        elipse(ctx, 0, my + 2, 13, 16)
        preencher(ctx, hexc("#5A1F2B"), 5)
    elif expr == "pensa":
        linha(ctx, [(-14, my + 4), (14, my - 2)], 6, TINTA)
    elif expr == "risada":
        ctx.move_to(-24, my - 4)
        ctx.line_to(24, my - 4)
        ctx.curve_to(22, my + 26, -22, my + 26, -24, my - 4)
        ctx.close_path()
        preencher(ctx, hexc("#5A1F2B"), 5)
    else:
        ctx.arc(0, my - 12, 22, PI * 0.2, PI * 0.8)
        ctx.set_line_width(6)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        cor(ctx, TINTA)
        ctx.stroke()
    if braco == "queixo":
        _braco(ctx, bd, PELE_LUME)
    ctx.restore()


def teco(ctx, x, y, s, t, boca=0.0, olhar=(0.0, 0.0), expr="feliz"):
    """Teco, robozinho voador que narra. (x, y) = centro do corpo."""
    ctx.save()
    ctx.translate(x, y + math.sin(t * 2.2) * 10)
    ctx.scale(s, s)
    # chama de flutuar
    f = 0.8 + 0.2 * math.sin(t * 25)
    elipse(ctx, 0, 112, 22 * f, 34 * f)
    cor(ctx, hexc("#9BE7FF", 0.85))
    ctx.fill()
    elipse(ctx, 0, 106, 11 * f, 18 * f)
    cor(ctx, BRANCO)
    ctx.fill()
    # antena
    linha(ctx, [(0, -84), (0, -128)], 8, TINTA)
    brilho = 0.6 + 0.4 * math.sin(t * 4)
    circulo(ctx, 0, -134, 22)
    cor(ctx, hexc("#FF6B6B", 0.25 * brilho))
    ctx.fill()
    circulo(ctx, 0, -134, 13)
    preencher(ctx, hexc("#FF6B6B"), 5)
    # bracinhos
    for sx in (-1, 1):
        circulo(ctx, sx * 96, 18 + math.sin(t * 3 + sx) * 6, 20)
        preencher(ctx, TECO_ESC, 5)
    # corpo
    circulo(ctx, 0, 0, 88)
    preencher(ctx, TECO, 7)
    ctx.new_path()
    ctx.arc(0, 0, 70, PI * 1.15, PI * 1.45)
    ctx.set_line_width(9)
    cor(ctx, hexc("#FFFFFF", 0.45))
    ctx.stroke()
    # tela
    retarr(ctx, -60, -46, 120, 86, 26)
    preencher(ctx, TELA, 5)
    ox, oy = olhar
    pisca = (t % 4.3) < 0.12
    for sx in (-1, 1):
        ex, ey = sx * 27 + ox * 6, -14 + oy * 5
        if pisca:
            linha(ctx, [(ex - 9, ey), (ex + 9, ey)], 5, CIANO)
        elif expr == "feliz" and boca < 0.05:
            ctx.new_path()
            ctx.arc(ex, ey + 6, 10, PI * 1.15, PI * 1.85)
            ctx.set_line_width(6)
            cor(ctx, CIANO)
            ctx.stroke()
        else:
            retarr(ctx, ex - 9, ey - 13, 18, 26, 9)
            cor(ctx, CIANO)
            ctx.fill()
    if boca < 0.05:
        ctx.new_path()
        ctx.arc(0, 10, 14, PI * 0.2, PI * 0.8)
        ctx.set_line_width(5)
        cor(ctx, CIANO)
        ctx.stroke()
    else:
        elipse(ctx, 0, 20, 15, 3 + 13 * min(boca, 1.0))
        cor(ctx, CIANO)
        ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ cenarios
def ceu(ctx, topo=CEU_TOPO, base=CEU_BASE, y1=H):
    g = cairo.LinearGradient(0, 0, 0, y1)
    g.add_color_stop_rgba(0, *topo)
    g.add_color_stop_rgba(1, *base)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()


def sol(ctx, x, y, r, t, c=SOL, raios=True):
    if raios:
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(t * 0.25)
        for i in range(12):
            a = i * PI / 6
            ctx.new_path()
            ctx.move_to(math.cos(a - 0.12) * r * 1.2, math.sin(a - 0.12) * r * 1.2)
            ctx.line_to(math.cos(a) * r * 1.75, math.sin(a) * r * 1.75)
            ctx.line_to(math.cos(a + 0.12) * r * 1.2, math.sin(a + 0.12) * r * 1.2)
            ctx.close_path()
            cor(ctx, (c[0], c[1], c[2], 0.75))
            ctx.fill()
        ctx.restore()
    g = cairo.RadialGradient(x, y, r * 0.8, x, y, r * 2.4)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], 0.45)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g)
    circulo(ctx, x, y, r * 2.4)
    ctx.fill()
    circulo(ctx, x, y, r)
    preencher(ctx, c, 6)


def _bolhas(ctx, bolhas, c, lw=6):
    for (bx, by, br) in bolhas:
        circulo(ctx, bx, by, br)
        ctx.set_line_width(lw * 2)
        cor(ctx, TINTA)
        ctx.stroke()
    for (bx, by, br) in bolhas:
        circulo(ctx, bx, by, br)
        cor(ctx, c)
        ctx.fill()


def nuvem(ctx, x, y, s=1.0, c=BRANCO):
    b = [(-70, 10, 45), (-20, -20, 60), (40, -10, 52), (85, 15, 38), (10, 20, 45)]
    _bolhas(ctx, [(x + bx * s, y + by * s, br * s) for bx, by, br in b], c)


def arvore(ctx, x, y, s=1.0):
    retarr(ctx, x - 22 * s, y - 170 * s, 44 * s, 175 * s, 14 * s)
    preencher(ctx, hexc("#8B5A3C"), 6)
    b = [(0, -260, 95), (-80, -200, 70), (80, -200, 70), (-40, -320, 65), (50, -310, 60)]
    _bolhas(ctx, [(x + bx * s, y + by * s, br * s) for bx, by, br in b], GRAMA_ESC)


def morros(ctx, c1=GRAMA, c2=GRAMA_ESC, base=860):
    ctx.new_path()
    ctx.move_to(0, base - 40)
    ctx.curve_to(400, base - 140, 800, base - 10, 1200, base - 90)
    ctx.curve_to(1500, base - 150, 1750, base - 80, W, base - 110)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    preencher(ctx, c2, 6)
    ctx.new_path()
    ctx.move_to(0, base + 20)
    ctx.curve_to(500, base - 60, 1100, base + 60, W, base - 10)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    preencher(ctx, c1, 6)
    random.seed(7)
    for _ in range(14):
        fx, fy = random.uniform(60, W - 60), random.uniform(base + 90, H - 30)
        estrela(ctx, fx, fy, 13, pontas=5, interno=0.55)
        preencher(ctx, random.choice([hexc("#FFFFFF"), hexc("#FFD1DC"), hexc("#FFE680")]), 3)


def parque(ctx, t, topo=CEU_TOPO, base=CEU_BASE, sol_pos=(1650, 190), sol_cor=SOL, verde=(GRAMA, GRAMA_ESC)):
    ceu(ctx, topo, base, 900)
    if sol_pos:
        sol(ctx, sol_pos[0], sol_pos[1], 70, t, sol_cor)
    for i, (nx, ny, ns) in enumerate([(300, 200, 1.0), (900, 140, 0.8), (1350, 300, 0.7)]):
        x = (nx + t * (18 + i * 6)) % (W + 400) - 200
        nuvem(ctx, x, ny, ns)
    morros(ctx, *verde)
    arvore(ctx, 230, 900, 1.1)


def logo(ctx, x, y, s, t=0.0, prog=1.0):
    """'Fabrica de PORQUES' com letras coloridas quicando."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    k = pop(prog * 1.6)
    if k > 0:
        ctx.save()
        ctx.scale(k, k)
        texto(ctx, "Fábrica de", 0, -95, 70, BRANCO, TINTA, 14)
        ctx.restore()
    palavra = "PORQUÊS"
    cores = [hexc("#FF6B6B"), hexc("#FFC93C"), hexc("#4CD964"), hexc("#3D8BFF"), hexc("#8E5CFF"), hexc("#FF9F1C"), hexc("#2EC4B6")]
    fonte(ctx, 150)
    larg = [ctx.text_extents(ch).x_advance for ch in palavra]
    total = sum(larg)
    cx = -total / 2
    for i, ch in enumerate(palavra):
        kk = pop(prog * 2.2 - 0.12 * i)
        if kk > 0:
            ctx.save()
            pulo = math.sin(t * 3 + i * 0.7) * 6
            ctx.translate(cx + larg[i] / 2, 40 + pulo)
            ctx.scale(kk, kk)
            texto(ctx, ch, 0, 0, 150, cores[i], TINTA, 22)
            ctx.restore()
        cx += larg[i]
    ctx.restore()
