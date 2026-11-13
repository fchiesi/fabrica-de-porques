"""Cenas do episodio 01. Cada cena: f(ctx, t, D, c, b)
t = tempo local (s), D = duracao da cena, c = [(inicio, fim)] de cada fala da
cena, b = abertura da boca do Teco (0..1, vem do audio).
"""
import math, random
from functools import lru_cache
import cairo
from desenho import *


def _entra(t, t0, dur=0.6):
    return suave(janela(t, t0, t0 + dur))


# ------------------------------------------------------------------ gancho
def gancho(ctx, t, D, c, b):
    parque(ctx, t)
    lume(ctx, 1300, 980, 1.05, t, "pensa", (0.2, -1.0), "queixo")
    for i in range(3):
        k = (t * 0.45 + i / 3) % 1
        a = 1 - abs(k * 2 - 1)
        texto(ctx, "?", 1390 + math.sin(k * 6 + i) * 40 + i * 40, 520 - k * 260, 70 + i * 18,
              hexc("#FFFFFF", a), hexc("#1D2A4A", a), 12)
    x = lerp(-250, 560, suave(janela(t, 0.2, 1.6)))
    teco(ctx, x, 470, 0.95, t, b, (1, 0))
    pilula(ctx, "Por que o céu é azul?", 960, 120, 64, hexc("#FFFFFF"), TINTA, janela(t, c[0][0] + 1.5, c[0][0] + 2.0))


# ---------------------------------------------------------------- abertura
def _raios(ctx, t, c1, c2):
    cor(ctx, c1)
    ctx.paint()
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.rotate(t * 0.15)
    for i in range(0, 24, 2):
        a0, a1 = i * PI / 12, (i + 1) * PI / 12
        ctx.new_path()
        ctx.move_to(0, 0)
        ctx.arc(0, 0, 1500, a0, a1)
        ctx.close_path()
        cor(ctx, c2)
        ctx.fill()
    ctx.restore()


def abertura(ctx, t, D, c, b):
    _raios(ctx, t, hexc("#4FA9F5"), hexc("#6BB8F7"))
    logo(ctx, 960, 330, 1.25, t, janela(t, 0.1, 1.3))
    k1 = pop(janela(t, c[0][0] + 0.9, c[0][0] + 1.4))
    k2 = pop(janela(t, c[0][0] + 1.6, c[0][0] + 2.1))
    if k1 > 0:
        teco(ctx, 560, 730, 0.95 * k1, t, b, (1, 0))
    if k2 > 0:
        lume(ctx, 1380, 1030, 0.95 * k2, t, "risada", (-0.5, 0), "acena")
    pilula(ctx, "Episódio 1: Por que o céu é azul?", 960, 560, 52, AMARELO, TINTA, janela(t, c[1][0], c[1][0] + 0.5))


# -------------------------------------------------------------------- mito
def _mar(ctx, t):
    ceu(ctx, CEU_TOPO, CEU_BASE, 650)
    sol(ctx, 1500, 200, 65, t)
    nuvem(ctx, 400 + t * 15, 220, 0.8)
    ctx.new_path()
    ctx.move_to(0, 640)
    for x in range(0, W + 40, 40):
        ctx.line_to(x, 640 + math.sin(x * 0.02 + t * 2) * 10)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    preencher(ctx, hexc("#2F80ED"), 6)
    for j in range(5):
        y = 720 + j * 70
        linha(ctx, [(x, y + math.sin(x * 0.03 + t * 2 + j) * 8) for x in range(80 + j * 60, 1900, 30)][:12], 6, hexc("#FFFFFF", 0.5))
    ctx.new_path()
    ctx.move_to(0, 900)
    ctx.curve_to(400, 860, 900, 940, 1100, H)
    ctx.line_to(0, H)
    ctx.close_path()
    preencher(ctx, hexc("#F2D492"), 6)


def _deserto(ctx, t):
    ceu(ctx, CEU_TOPO, CEU_BASE, 800)
    sol(ctx, 1500, 200, 65, t)
    ctx.new_path()
    ctx.move_to(0, 760)
    ctx.curve_to(500, 640, 900, 800, 1300, 720)
    ctx.curve_to(1600, 660, 1800, 720, W, 700)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    preencher(ctx, hexc("#E9B65C"), 6)
    ctx.new_path()
    ctx.move_to(0, 880)
    ctx.curve_to(600, 800, 1200, 960, W, 860)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    preencher(ctx, hexc("#F5CF7C"), 6)
    for (cx, cy, s) in [(420, 900, 1.0), (1500, 820, 0.7)]:
        retarr(ctx, cx - 30 * s, cy - 260 * s, 60 * s, 270 * s, 30 * s)
        preencher(ctx, hexc("#4CAF50"), 6)
        retarr(ctx, cx - 110 * s, cy - 190 * s, 40 * s, 100 * s, 20 * s)
        preencher(ctx, hexc("#4CAF50"), 6)
        retarr(ctx, cx - 110 * s, cy - 110 * s, 90 * s, 36 * s, 18 * s)
        preencher(ctx, hexc("#4CAF50"), 6)
        retarr(ctx, cx + 70 * s, cy - 230 * s, 40 * s, 100 * s, 20 * s)
        preencher(ctx, hexc("#4CAF50"), 6)
        retarr(ctx, cx + 20 * s, cy - 150 * s, 90 * s, 36 * s, 18 * s)
        preencher(ctx, hexc("#4CAF50"), 6)


def mito(ctx, t, D, c, b):
    k = suave(janela(t, c[1][0] - 0.2, c[1][0] + 0.8))
    off = k * W
    for desenhar, x0 in ((_mar, -off), (_deserto, W - off)):
        if -W < x0 < W:
            ctx.save()
            ctx.rectangle(x0, 0, W, H)
            ctx.clip()
            ctx.translate(x0, 0)
            desenhar(ctx, t)
            ctx.restore()
    pilula(ctx, "O céu reflete o mar?", 960, 130, 60, BRANCO, TINTA, janela(t, c[0][0] + 0.4, c[0][0] + 0.9))
    pilula(ctx, "Deserto: longe do mar... e o céu azul!", 960, 260, 46, AMARELO, TINTA, janela(t, c[1][0] + 2.0, c[1][0] + 2.5))
    kx = pop(janela(t, c[2][0], c[2][0] + 0.5))
    if kx > 0:
        ctx.save()
        ctx.translate(960, 130)
        ctx.scale(kx, kx)
        for s in (1, -1):
            linha(ctx, [(-45, -45 * s), (45, 45 * s)], 34, TINTA)
            linha(ctx, [(-45, -45 * s), (45, 45 * s)], 22, VERMELHO)
        ctx.restore()
    teco(ctx, 260, 560, 0.85, t, b, (1, -0.3))


# ------------------------------------------------------------------ prisma
def _fundo_escuro(ctx, t):
    ceu(ctx, hexc("#0E1A33"), hexc("#1E3260"))
    random.seed(3)
    for _ in range(70):
        x, y = random.uniform(0, W), random.uniform(0, H)
        a = 0.3 + 0.3 * math.sin(t * 2 + x)
        circulo(ctx, x, y, random.uniform(1.5, 3.5))
        cor(ctx, hexc("#FFFFFF", a))
        ctx.fill()


def prisma(ctx, t, D, c, b):
    _fundo_escuro(ctx, t)
    sol(ctx, 230, 420, 90, t)
    px, py, ps = 960, 540, 230
    A = (px, py - ps)
    B = (px - ps * 0.95, py + ps * 0.7)
    C = (px + ps * 0.95, py + ps * 0.7)
    entrada = (lerp(A[0], B[0], 0.5), lerp(A[1], B[1], 0.5))
    saida = (lerp(A[0], C[0], 0.55), lerp(A[1], C[1], 0.55))
    kb = suave(janela(t, c[0][0] + 0.3, c[0][0] + 1.3))
    if kb > 0:
        x1 = lerp(320, entrada[0], kb)
        y1 = lerp(430, entrada[1], kb)
        linha(ctx, [(320, 430), (x1, y1)], 34, hexc("#FFFFFF", 0.25))
        linha(ctx, [(320, 430), (x1, y1)], 16, BRANCO)
    ke = suave(janela(t, c[1][0] + 1.0, c[1][0] + 3.0))
    if ke > 0:
        comp = 900 * ke
        for i, cc in enumerate(ESPECTRO):
            a0 = -0.06 + i * 0.075
            a1 = a0 + 0.075
            ctx.new_path()
            ctx.move_to(*saida)
            ctx.line_to(saida[0] + math.cos(a0) * comp, saida[1] + math.sin(a0) * comp)
            ctx.line_to(saida[0] + math.cos(a1) * comp, saida[1] + math.sin(a1) * comp)
            ctx.close_path()
            cor(ctx, (cc[0], cc[1], cc[2], 0.92))
            ctx.fill()
    # prisma de vidro
    ctx.new_path()
    ctx.move_to(*A)
    ctx.line_to(*B)
    ctx.line_to(*C)
    ctx.close_path()
    preencher(ctx, hexc("#BFE9FF", 0.55), 8, hexc("#FFFFFF"))
    linha(ctx, [(A[0] - 30, A[1] + 90), (A[0] - 90, A[1] + 230)], 10, hexc("#FFFFFF", 0.7))
    pilula(ctx, "Luz do Sol = todas as cores juntas", 960, 120, 54, BRANCO, TINTA, janela(t, c[0][0] + 1.6, c[0][0] + 2.1))
    # arco-iris no canto
    kr = suave(janela(t, c[1][1] - 2.4, c[1][1] - 1.2))
    if kr > 0:
        ctx.save()
        ctx.translate(1630, 980)
        for i, cc in enumerate(ESPECTRO):
            ctx.new_path()
            ctx.arc(0, 0, 250 - i * 22, PI, PI + PI * kr)
            ctx.set_line_width(22)
            cor(ctx, cc)
            ctx.stroke()
        ctx.restore()
        pilula(ctx, "arco-íris!", 1630, 1010, 44, BRANCO, TINTA, janela(t, c[1][1] - 1.4, c[1][1] - 0.9))
    teco(ctx, 300, 820, 0.75, t, b, (1, -0.5))


# ---------------------------------------------------------------------- ar
def ar(ctx, t, D, c, b):
    parque(ctx, t)
    ctx.rectangle(0, 0, W, H)
    cor(ctx, hexc("#FFFFFF", 0.25))
    ctx.fill()
    cx, cy, r = 1060, 470, 320
    k = pop(janela(t, 0.1, 0.8))
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(k, k)
    # cabo
    linha(ctx, [(r * 0.7, r * 0.7), (r * 1.25, r * 1.25)], 70, TINTA)
    linha(ctx, [(r * 0.72, r * 0.72), (r * 1.23, r * 1.23)], 52, hexc("#8B5A3C"))
    circulo(ctx, 0, 0, r)
    ctx.save()
    ctx.clip()
    ceu(ctx, hexc("#9FD6FF"), hexc("#DDF2FF"))
    kp = janela(t, c[1][0] + 0.2, c[1][0] + 2.5)
    random.seed(11)
    n = int(160 * kp)
    for i in range(160):
        x0, y0 = random.uniform(-r, r), random.uniform(-r, r)
        rr = random.uniform(6, 13)
        fase = random.uniform(0, 6)
        if i >= n:
            continue
        x = x0 + math.sin(t * 3 + fase) * 10
        y = y0 + math.cos(t * 2.6 + fase * 1.3) * 10
        circulo(ctx, x, y, rr)
        preencher(ctx, random.choice([hexc("#FFFFFF"), hexc("#E3F3FF"), hexc("#CDE8FF")]), 3)
    ctx.restore()
    circulo(ctx, 0, 0, r)
    ctx.set_line_width(26)
    cor(ctx, TINTA)
    ctx.stroke()
    circulo(ctx, 0, 0, r)
    ctx.set_line_width(14)
    cor(ctx, hexc("#B0BEC5"))
    ctx.stroke()
    ctx.new_path()
    ctx.arc(0, 0, r - 40, PI * 1.1, PI * 1.35)
    ctx.set_line_width(14)
    cor(ctx, hexc("#FFFFFF", 0.7))
    ctx.stroke()
    ctx.restore()
    pilula(ctx, "Vazio?", cx, 90, 60, BRANCO, TINTA, janela(t, c[0][0] + 1.6, c[0][0] + 2.0) * (1 - janela(t, c[1][0], c[1][0] + 0.3)))
    pilula(ctx, "partículas do ar (bem pequenininhas!)", cx, 90, 50, AMARELO, TINTA, janela(t, c[1][0] + 2.0, c[1][0] + 2.5))
    teco(ctx, 330, 470, 0.9, t, b, (1, 0))
    lume(ctx, 1650, 1040, 0.75, t, "uau" if t > c[1][0] + 1 else "feliz", (-1, -0.3), "baixo")


# ------------------------------------------------------------------ espalha
@lru_cache(maxsize=4)
def _sim_fotons(D, t_azul, t_verm):
    """Simulacao deterministica: fotons vermelhos passam direto, azuis quicam."""
    rnd = random.Random(5)
    parts = [(rnd.uniform(520, 1880), rnd.uniform(160, 1000)) for _ in range(46)]
    fps = 30
    n = int(D * fps) + 2
    fotons = []
    for i in range(10):
        fotons.append(dict(cor=ESPECTRO[i % 2], t0=t_verm + i * 0.28, y=rnd.uniform(380, 700), azul=False))
    for i in range(26):
        fotons.append(dict(cor=ESPECTRO[4], t0=t_azul + i * 0.16, y=rnd.uniform(330, 750), azul=True))
    pos = []
    for f in fotons:
        x, y = 260.0, f["y"]
        vx, vy = 14.0, 0.0
        cool = 0
        traj = []
        for k in range(n):
            tk = k / fps
            if tk < f["t0"]:
                traj.append(None)
                continue
            x += vx
            y += vy
            if f["azul"] and cool == 0:
                for (qx, qy) in parts:
                    if (x - qx) ** 2 + (y - qy) ** 2 < 26 ** 2:
                        a = rnd.uniform(0, 2 * PI)
                        vx, vy = 13 * math.cos(a), 13 * math.sin(a)
                        cool = 6
                        break
            cool = max(0, cool - 1)
            traj.append((x, y))
        pos.append(traj)
    return parts, fotons, pos


def espalha(ctx, t, D, c, b):
    ceu(ctx, hexc("#1B2B57"), hexc("#2C4A86"))
    parts, fotons, pos = _sim_fotons(round(D, 3), round(c[2][0] + 0.3, 3), round(c[1][0] + 0.2, 3))
    for i, (qx, qy) in enumerate(parts):
        circulo(ctx, qx + math.sin(t * 2 + i) * 4, qy + math.cos(t * 1.7 + i) * 4, 13)
        preencher(ctx, hexc("#E3F3FF"), 4)
    sol(ctx, 130, 540, 110, t)
    fr = int(t * 30)
    for f, traj in zip(fotons, pos):
        pts = [p for p in traj[max(0, fr - 9):fr + 1] if p] if fr < len(traj) else []
        if len(pts) >= 2:
            linha(ctx, pts, 10, (f["cor"][0], f["cor"][1], f["cor"][2], 0.45))
        if pts:
            x, y = pts[-1]
            circulo(ctx, x, y, 17)
            cor(ctx, (f["cor"][0], f["cor"][1], f["cor"][2], 0.3))
            ctx.fill()
            circulo(ctx, x, y, 10)
            preencher(ctx, f["cor"], 4, BRANCO)
    pilula(ctx, "Cada cor se comporta de um jeito", 960, 90, 52, BRANCO, TINTA, janela(t, c[0][0] + 0.8, c[0][0] + 1.3) * (1 - janela(t, c[1][0], c[1][0] + 0.3)))
    pilula(ctx, "vermelho e laranja: passam direto", 960, 90, 52, hexc("#FFB3A7"), TINTA, janela(t, c[1][0] + 0.6, c[1][0] + 1.1) * (1 - janela(t, c[2][0], c[2][0] + 0.3)))
    pilula(ctx, "azul: se espalha pra todo lado!", 960, 90, 52, hexc("#9CC8FF"), TINTA, janela(t, c[2][0] + 1.0, c[2][0] + 1.5))


# --------------------------------------------------------------------- olho
def olho(ctx, t, D, c, b):
    k = suave(janela(t, c[1][0], c[1][0] + 1.0))
    parque(ctx, t, mistura(hexc("#6FB5EE"), hexc("#2E8FEA"), k), CEU_BASE)
    lx, ly = 960, 640
    random.seed(21)
    origens = [(random.uniform(80, 1840), random.uniform(60, 380)) for _ in range(16)]
    for i, (ox, oy) in enumerate(origens):
        p = janela(t, 0.4 + i * 0.22, 1.4 + i * 0.22)
        if p <= 0:
            continue
        dx, dy = lx - ox, ly - oy
        dd = math.hypot(dx, dy)
        x1, y1 = ox + dx * 0.85 * suave(p), oy + dy * 0.85 * suave(p)
        if math.hypot(x1 - ox, y1 - oy) > 30:
            seta(ctx, ox, oy, x1, y1, hexc("#1F63D6", 0.85), 9, 26)
        circulo(ctx, ox, oy, 10)
        preencher(ctx, ESPECTRO[4], 4, BRANCO)
    lume(ctx, 960, 1060, 0.9, t, "uau", (0, -1), "alto" if t > c[1][0] else "baixo")
    pilula(ctx, "o azul chega de todo lado", 960, 470, 50, BRANCO, TINTA, janela(t, c[0][0] + 2.5, c[0][0] + 3.0) * (1 - janela(t, c[1][0], c[1][0] + 0.3)))
    pilula(ctx, "o céu todo fica azul!", 960, 470, 60, AMARELO, TINTA, janela(t, c[1][0] + 0.4, c[1][0] + 0.9))
    teco(ctx, 1600, 520, 0.8, t, b, (-1, 0))


# --------------------------------------------------------------- por do sol
CENTRO = (960, 2700)
R_TERRA, R_AR = 2000, 2220


def _dentro_ar(x, y):
    return math.hypot(x - CENTRO[0], y - CENTRO[1]) <= R_AR


def _diagrama(ctx, t, c, b):
    ceu(ctx, hexc("#0E1A33"), hexc("#22396E"))
    circulo(ctx, CENTRO[0], CENTRO[1], R_AR)
    cor(ctx, hexc("#6FC3FF", 0.35))
    ctx.fill()
    circulo(ctx, CENTRO[0], CENTRO[1], R_TERRA)
    preencher(ctx, hexc("#4CAF50"), 8)
    ox, oy = 960, CENTRO[1] - R_TERRA  # observadora no topo da Terra
    texto(ctx, "ar", 1500, 610, 46, hexc("#CFEAFF"))
    # sol alto -> sol baixo
    m = suave(janela(t, c[0][0] + 2.2, c[0][0] + 4.0))
    sx, sy = lerp(960, 120, m), lerp(130, 560, m)
    n = 60
    pts = [(lerp(sx, ox, i / n), lerp(sy, oy, i / n)) for i in range(n + 1)]
    dentro = [p for p in pts if _dentro_ar(*p)]
    linha(ctx, [(sx, sy), (ox, oy)], 6, hexc("#FFFFFF", 0.35))
    if len(dentro) >= 2:
        avermelha = janela(t, c[1][0] + 0.5, c[1][0] + 3.0) * m
        for i in range(len(dentro) - 1):
            k = i / max(1, len(dentro) - 2)
            cc = mistura(BRANCO, hexc("#FF8A3D"), k * avermelha)
            linha(ctx, [dentro[i], dentro[i + 1]], 18, cc)
        # azul se despedindo pelo caminho
        if avermelha > 0:
            for i in range(0, len(dentro) - 1, 3):
                fase = (t * 0.8 + i * 0.13) % 1
                x, y = dentro[i]
                circulo(ctx, x + (fase * 70) * (1 if i % 2 else -1) * 0.4, y - fase * 90, 9)
                cor(ctx, hexc("#3D8BFF", (1 - fase) * avermelha))
                ctx.fill()
    sol(ctx, sx, sy, 60, t, mistura(SOL, hexc("#FF9F1C"), m))
    lume(ctx, ox, oy + 6, 0.32, t, "uau", (-1, -1), "baixo")
    rot = "caminho curto" if m < 0.5 else "caminho LONGO pelo ar"
    pilula(ctx, rot, 960, 90, 52, AMARELO if m >= 0.5 else BRANCO, TINTA, janela(t, c[0][0] + 0.8, c[0][0] + 1.3))
    teco(ctx, 1640, 300, 0.75, t, b, (-1, 0))


def por_do_sol(ctx, t, D, c, b):
    k = suave(janela(t, c[2][0] - 0.4, c[2][0] + 0.6))
    if k < 1:
        _diagrama(ctx, t, c, b)
    if k > 0:
        ctx.push_group()
        parque(ctx, t, hexc("#FF7E5F"), hexc("#FFD38A"), (1500, 640), hexc("#FF9F1C"),
               (hexc("#6BAF4E"), hexc("#4E8F3A")))
        lume(ctx, 900, 1000, 1.0, t, "risada", (1, -0.4), "aponta")
        teco(ctx, 520, 520, 0.85, t, b, (1, 0))
        pilula(ctx, "pôr do sol alaranjado!", 960, 110, 60, BRANCO, TINTA, janela(t, c[2][0] + 0.8, c[2][0] + 1.3))
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(k)


# --------------------------------------------------------------- experimento
def experimento(ctx, t, D, c, b):
    cor(ctx, hexc("#FCE8C8"))
    ctx.paint()
    ctx.rectangle(0, 800, W, H - 800)
    preencher(ctx, hexc("#C98B5A"), 6)
    gx, gy, gw, gh = 860, 420, 220, 380
    # gotas de leite
    leite = janela(t, c[0][0] + 2.5, c[0][0] + 4.5)
    if 0 < leite < 1 or (t < c[1][0] and leite >= 1 and t < c[0][1] + 0.3):
        retarr(ctx, gx + 60, 170, 100, 130, 24)
        preencher(ctx, BRANCO, 6)
        texto(ctx, "LEITE", gx + 110, 250, 30, hexc("#3D6FD8"))
        for i in range(3):
            f = (t * 1.6 + i / 3) % 1
            if leite < 1:
                elipse(ctx, gx + 110, 310 + f * 180, 9, 13)
                preencher(ctx, BRANCO, 3)
    # lanterna e feixe
    kl = suave(janela(t, c[1][0] + 0.3, c[1][0] + 1.2))
    if kl > 0:
        lx = lerp(-200, 380, kl)
        luz = janela(t, c[1][0] + 1.4, c[1][0] + 1.8)
        if luz > 0:
            ctx.new_path()
            ctx.move_to(lx + 200, 570)
            ctx.line_to(gx + 10, gy + 80)
            ctx.line_to(gx + 10, gy + 300)
            ctx.line_to(lx + 200, 650)
            ctx.close_path()
            cor(ctx, hexc("#FFF6B0", 0.55 * luz))
            ctx.fill()
        retarr(ctx, lx, 575, 160, 70, 18)
        preencher(ctx, hexc("#5C6B80"), 6)
        ctx.new_path()
        ctx.move_to(lx + 150, 560)
        ctx.line_to(lx + 205, 540)
        ctx.line_to(lx + 205, 680)
        ctx.line_to(lx + 150, 660)
        ctx.close_path()
        preencher(ctx, hexc("#FFD93D"), 6)
    # copo com agua
    turvo = suave(leite)
    azulado = suave(janela(t, c[2][0] + 0.3, c[2][0] + 1.5))
    agua = mistura(hexc("#CDEBFF", 0.55), hexc("#F2F6FA", 0.85), turvo)
    agua = mistura(agua, hexc("#9CC8FF", 0.9), azulado)
    retarr(ctx, gx + 10, gy + 70, gw - 20, gh - 80, 18)
    cor(ctx, agua)
    ctx.fill()
    if azulado > 0:
        g = cairo.RadialGradient(gx + gw / 2, gy + 220, 10, gx + gw / 2, gy + 220, 300)
        g.add_color_stop_rgba(0, 0.4, 0.6, 1, 0.35 * azulado)
        g.add_color_stop_rgba(1, 0.4, 0.6, 1, 0)
        ctx.set_source(g)
        circulo(ctx, gx + gw / 2, gy + 220, 300)
        ctx.fill()
    retarr(ctx, gx, gy, gw, gh, 22)
    preencher(ctx, hexc("#FFFFFF", 0.18), 8)
    linha(ctx, [(gx + 35, gy + 50), (gx + 35, gy + 300)], 12, hexc("#FFFFFF", 0.7))
    # luz que atravessa: laranja na parede
    sai = suave(janela(t, c[2][0] + 3.0, c[2][0] + 4.2))
    if sai > 0:
        ctx.new_path()
        ctx.move_to(gx + gw - 10, gy + 120)
        ctx.line_to(1580, 470)
        ctx.line_to(1580, 750)
        ctx.line_to(gx + gw - 10, gy + 280)
        ctx.close_path()
        cor(ctx, hexc("#FFB45C", 0.35 * sai))
        ctx.fill()
        elipse(ctx, 1600, 610, 70, 140)
        cor(ctx, hexc("#FF9F1C", 0.8 * sai))
        ctx.fill()
    pilula(ctx, "água + gotas de leite", 960, 90, 52, BRANCO, TINTA, janela(t, c[0][0] + 1.2, c[0][0] + 1.7) * (1 - janela(t, c[1][0], c[1][0] + 0.3)))
    pilula(ctx, "peça ajuda a um adulto", 960, 90, 52, AMARELO, TINTA, janela(t, c[1][0] + 0.3, c[1][0] + 0.8) * (1 - janela(t, c[2][0], c[2][0] + 0.3)))
    pilula(ctx, "de lado: azulado", gx + gw / 2, 900, 46, hexc("#9CC8FF"), TINTA, janela(t, c[2][0] + 1.2, c[2][0] + 1.7))
    pilula(ctx, "atravessou: alaranjado", 1600, 860, 46, hexc("#FFC48A"), TINTA, janela(t, c[2][0] + 4.0, c[2][0] + 4.5))
    teco(ctx, 1600, 260, 0.75, t, b, (-1, 0.3))


# -------------------------------------------------------------------- resumo
def _icone(ctx, i, x, y, t):
    if i == 0:
        sol(ctx, x - 40, y, 45, t, raios=False)
        for j, cc in enumerate(ESPECTRO):
            linha(ctx, [(x + 10, y - 50 + j * 20), (x + 110, y - 50 + j * 20)], 14, cc)
    elif i == 1:
        random.seed(4)
        for _ in range(9):
            a = random.uniform(0, 2 * PI)
            seta(ctx, x, y, x + math.cos(a) * 90, y + math.sin(a) * 75, ESPECTRO[4], 7, 18)
        circulo(ctx, x, y, 16)
        preencher(ctx, BRANCO, 4)
    else:
        ctx.save()
        retarr(ctx, x - 120, y - 70, 240, 140, 20)
        ctx.clip()
        ceu(ctx, hexc("#FF7E5F"), hexc("#FFD38A"))
        sol(ctx, x, y + 50, 40, t, hexc("#FF9F1C"), raios=False)
        ctx.restore()
        retarr(ctx, x - 120, y - 70, 240, 140, 20)
        preencher(ctx, hexc("#FFFFFF", 0), 6)


def resumo(ctx, t, D, c, b):
    _raios(ctx, t, hexc("#EAF6FF"), hexc("#DDEFFF"))
    texto(ctx, "Resumindo!", 960, 150, 90, AMARELO, TINTA, 18)
    cards = [("A luz do Sol tem", "todas as cores"), ("O azul se espalha:", "céu azul!"), ("Caminho longo:", "pôr do sol laranja")]
    for i, (l1, l2) in enumerate(cards):
        k = pop(janela(t, c[i][0], c[i][0] + 0.5))
        if k <= 0:
            continue
        x = 380 + i * 580
        ctx.save()
        ctx.translate(x, 560)
        ctx.scale(k, k)
        retarr(ctx, -250 + 8, -260 + 10, 500, 520, 40)
        cor(ctx, hexc("#000000", 0.15))
        ctx.fill()
        retarr(ctx, -250, -260, 500, 520, 40)
        preencher(ctx, BRANCO, 7)
        circulo(ctx, -195, -205, 36)
        preencher(ctx, TECO, 5)
        texto(ctx, str(i + 1), -195, -190, 44, BRANCO)
        _icone(ctx, i, 0, -70, t)
        texto(ctx, l1, 0, 110, 42, TINTA)
        texto(ctx, l2, 0, 175, 46, hexc("#3D6FD8"))
        ctx.restore()
    teco(ctx, 1780, 960, 0.6, t, b, (-1, -0.5))


# --------------------------------------------------------------------- final
def final(ctx, t, D, c, b):
    parque(ctx, t)
    lume(ctx, 1450, 1000, 1.0, t, "risada", (-0.6, 0), "acena")
    teco(ctx, 1080, 560, 0.9, t, b, (1, 0))
    k = pop(janela(t, c[0][0] + 0.3, c[0][0] + 0.9))
    if k > 0:
        ctx.save()
        ctx.translate(470, 430)
        ctx.scale(k, k)
        retarr(ctx, -330, -230, 660, 460, 40)
        preencher(ctx, hexc("#1B2B57"), 7)
        texto(ctx, "Próximo episódio", 0, -150, 48, AMARELO)
        circulo(ctx, 0, 10, 95)
        preencher(ctx, hexc("#FFF3B0"), 6)
        circulo(ctx, 45, -15, 85)
        cor(ctx, hexc("#1B2B57"))
        ctx.fill()
        texto(ctx, "Por que a Lua", 0, 170, 50, BRANCO)
        texto(ctx, "muda de forma?", 0, 225, 50, BRANCO)
        ctx.restore()
    kf = janela(t, c[0][1] + 0.3, c[0][1] + 1.0)
    if kf > 0:
        ctx.rectangle(0, 0, W, H)
        cor(ctx, hexc("#4FA9F5", suave(kf)))
        ctx.fill()
        logo(ctx, 960, 520, 1.2, t, kf)


CENAS = dict(gancho=gancho, abertura=abertura, mito=mito, prisma=prisma, ar=ar, espalha=espalha,
             olho=olho, por_do_sol=por_do_sol, experimento=experimento, resumo=resumo, final=final)
