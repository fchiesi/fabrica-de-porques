"""Renderiza um episodio: audio das falas -> linha do tempo -> video + legendas.

Uso:
  python3 motor/render.py ep01                 # video final (1080p)
  python3 motor/render.py ep01 --quadros 3,40  # so PNGs de conferencia
  python3 motor/render.py ep01 --rapido        # 540p, para revisar timing

Falas: <ep>/falas/gravadas/NN.(wav|m4a|mp3|ogg|aac|opus) tem prioridade sobre
<ep>/falas/rascunho/NN.wav (voz sintetica gerada por motor/voz.py).
"""
import argparse, glob, importlib.util, json, math, os, subprocess, sys
from multiprocessing import get_context

import numpy as np
import cairo

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "motor"))
import desenho as d  # noqa: E402

FPS, SR = 30, 48000
GAP, PAD_INI, PAD_FIM = 0.45, 0.5, 0.7
PRE = {"abertura": 1.6}           # vinheta antes da primeira fala
POS = {"final": 3.2}              # logo no fim
TRANS = 0.35                      # crossfade entre cenas


def _mod(caminho, nome):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def carregar_audio(caminho, gravada):
    filtros = ["highpass=f=70"]
    if gravada:  # corta silencio do comeco/fim da sua gravacao
        filtros = ["silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05",
                   "areverse", "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08",
                   "areverse"] + filtros
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", caminho, "-af", ",".join(filtros),
                          "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], check=True, capture_output=True).stdout
    a = np.frombuffer(out, dtype=np.float32).copy()
    pico = np.max(np.abs(a)) or 1.0
    return a / pico * 0.89


def achar_fala(ep_dir, i):
    for ext in ("wav", "m4a", "mp3", "ogg", "aac", "opus", "webm"):
        p = os.path.join(ep_dir, "falas", "gravadas", f"{i:02d}.{ext}")
        if os.path.exists(p):
            return p, True
    return os.path.join(ep_dir, "falas", "rascunho", f"{i:02d}.wav"), False


def linha_do_tempo(ep_dir, rot):
    falas = []
    for i, (cena, txt) in enumerate(rot.FALAS, 1):
        p, grav = achar_fala(ep_dir, i)
        falas.append(dict(n=i, cena=cena, texto=txt, arquivo=p, gravada=grav, audio=carregar_audio(p, grav)))
    cenas, t = [], 0.0
    for f in falas:
        if not cenas or cenas[-1]["nome"] != f["cena"]:
            if cenas:
                cenas[-1]["fim"] = t = t + PAD_FIM
            cenas.append(dict(nome=f["cena"], ini=t, falas=[]))
            t += PAD_INI + PRE.get(f["cena"], 0)
        else:
            t += GAP
        f["ini"] = t
        f["fim"] = t + len(f["audio"]) / SR
        t = f["fim"]
        cenas[-1]["falas"].append(f)
    cenas[-1]["fim"] = t + PAD_FIM + POS.get(cenas[-1]["nome"], 0)
    for c in cenas:
        c["D"] = c["fim"] - c["ini"]
        c["cues"] = [(f["ini"] - c["ini"], f["fim"] - c["ini"]) for f in c["falas"]]
    return falas, cenas


# ------------------------------------------------------------------ audio
def _pluck(freq, dur, decai=3.0):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * decai) * np.minimum(1, t * 200)
    return (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) + 0.1 * np.sin(6 * np.pi * freq * t)) * env


def _nota(n):  # n = semitons a partir do Do4
    return 261.63 * 2 ** (n / 12)


def montar_audio(falas, cenas, total):
    n = int(total * SR) + SR
    voz = np.zeros(n, np.float32)
    for f in falas:
        i0 = int(f["ini"] * SR)
        voz[i0:i0 + len(f["audio"])] += f["audio"]
    # envelope para a boca do Teco
    hop = SR // FPS
    nq = int(total * FPS) + 2
    rms = np.array([np.sqrt(np.mean(voz[k * hop:(k + 1) * hop] ** 2) + 1e-12) for k in range(nq)])
    ref = np.percentile(rms[rms > 0.01], 90) if np.any(rms > 0.01) else 1.0
    boca = np.clip((rms / ref - 0.12) * 1.3, 0, 1)
    boca = np.convolve(boca, [0.25, 0.5, 0.25], mode="same")

    # trilha: arpejo suave (Do - Sol - Lam - Fa), 100 bpm
    musica = np.zeros(n, np.float32)
    acordes = [[0, 4, 7, 12], [-5, -1, 2, 7], [-3, 0, 4, 9], [-7, -3, 0, 5]]
    passo = 0.3
    k = 0
    while k * passo < total:
        ac = acordes[(k // 8) % 4]
        nota = ac[[0, 1, 2, 3, 2, 1, 2, 3][k % 8]]
        s = _pluck(_nota(nota + 12), 0.9, 4.0) * 0.5
        if k % 8 == 0:
            s = s + _pluck(_nota(ac[0] - 12), 2.4, 1.2)[: len(s)] * 0.6
        i0 = int(k * passo * SR)
        musica[i0:i0 + len(s)] += s[: max(0, n - i0)]
        k += 1
    # abaixa a trilha quando ha fala (ducking)
    fala_on = np.repeat(np.clip(rms / ref * 3, 0, 1), hop)[:n]
    fala_on = np.convolve(fala_on, np.ones(SR // 4) / (SR // 4), mode="same")
    fala_on = np.pad(fala_on, (0, max(0, n - len(fala_on))))[:n]
    musica *= (0.075 - 0.045 * np.clip(fala_on * 2, 0, 1))

    efeitos = np.zeros(n, np.float32)
    for c in cenas:
        if c["nome"] == "abertura":  # vinheta
            i0 = int((c["ini"] + 0.1) * SR)
            for j, nt in enumerate([12, 16, 19, 24]):
                s = _pluck(_nota(nt), 0.8, 3.0) * 0.28
                a = i0 + int(j * 0.14 * SR)
                efeitos[a:a + len(s)] += s
            for nt in (12, 16, 19, 24):
                s = _pluck(_nota(nt), 1.6, 1.8) * 0.16
                a = i0 + int(0.62 * SR)
                efeitos[a:a + len(s)] += s
        if c["ini"] > 0:  # whoosh na troca de cena
            m = int(0.35 * SR)
            ruido = np.random.default_rng(int(c["ini"] * 10)).standard_normal(m)
            ruido = np.convolve(ruido, np.ones(30) / 30, mode="same")
            env = np.sin(np.linspace(0, np.pi, m)) ** 2
            a = int((c["ini"] - 0.15) * SR)
            efeitos[a:a + m] += (ruido * env * 0.18).astype(np.float32)
    mix = voz + musica + efeitos
    return mix, boca


# ------------------------------------------------------------------ video
_ESTADO = {}


def _init(ep_dir, cenas_json, boca, escala):
    sys.path.insert(0, ep_dir)
    m = _mod(os.path.join(ep_dir, "cenas.py"), "cenas")
    _ESTADO.update(cenas=cenas_json, boca=boca, escala=escala, funcs=m.CENAS)


def desenhar_quadro(ctx, q):
    T = q / FPS
    cenas, funcs, boca = _ESTADO["cenas"], _ESTADO["funcs"], _ESTADO["boca"]
    i = 0
    while i < len(cenas) - 1 and T >= cenas[i + 1]["ini"]:
        i += 1
    c = cenas[i]
    t = T - c["ini"]
    b = float(boca[min(q, len(boca) - 1)])
    if i > 0 and t < TRANS:
        p = cenas[i - 1]
        funcs[p["nome"]](ctx, p["D"] + t, p["D"], p["cues"], 0.0)
        ctx.push_group()
        funcs[c["nome"]](ctx, t, c["D"], c["cues"], b)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(d.suave(t / TRANS))
    else:
        funcs[c["nome"]](ctx, t, c["D"], c["cues"], b)


def _superficie():
    e = _ESTADO["escala"]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(d.W * e), int(d.H * e))
    return s


def _ctx(s):
    ctx = cairo.Context(s)
    ctx.scale(_ESTADO["escala"], _ESTADO["escala"])
    return ctx


def render_trecho(args):
    q0, q1, saida = args
    s = _superficie()
    w, h = s.get_width(), s.get_height()
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                           "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                           "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", saida],
                          stdin=subprocess.PIPE)
    for q in range(q0, q1):
        ctx = _ctx(s)
        ctx.set_source_rgb(1, 1, 1)
        ctx.paint()
        desenhar_quadro(ctx, q)
        s.flush()
        ff.stdin.write(bytes(s.get_data()))
    ff.stdin.close()
    ff.wait()
    return saida


def _tc(t, sep=","):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)) % 1000:03d}"


def _quebrar(txt, maxc=42):
    if len(txt) <= maxc:
        return [txt]
    pal, linhas, cur = txt.split(), [], ""
    for p in pal:
        if len(cur) + len(p) + 1 > maxc and cur:
            linhas.append(cur)
            cur = p
        else:
            cur = (cur + " " + p).strip()
    linhas.append(cur)
    return linhas


def escrever_legendas(falas, caminho):
    blocos = []
    n = 1
    for f in falas:
        partes = _quebrar(f["texto"], 84)
        dur = f["fim"] - f["ini"]
        total = sum(len(p) for p in partes)
        t = f["ini"]
        for p in partes:
            dt = dur * len(p) / total
            blocos.append(f"{n}\n{_tc(t)} --> {_tc(t + dt)}\n" + "\n".join(_quebrar(p)) + "\n")
            n += 1
            t += dt
    open(caminho, "w", encoding="utf-8").write("\n".join(blocos))


def capitulos(cenas, rot):
    caps = []
    for c in cenas:
        nome = getattr(rot, "CAPITULOS", {}).get(c["nome"])
        if nome:
            caps.append([max(0.0, c["ini"]), nome])
    caps[0][0] = 0.0
    # YouTube: cada capitulo >= 10 s; junta os curtos ao anterior
    ok = [caps[0]]
    for i in range(1, len(caps)):
        if caps[i][0] - ok[-1][0] < 10:
            continue
        ok.append(caps[i])
    return [f"{int(t // 60)}:{int(t % 60):02d} {n}" for t, n in ok]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("--quadros", help="segundos separados por virgula -> PNGs")
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()

    ep_dir = os.path.join(RAIZ, a.ep)
    rot = _mod(os.path.join(ep_dir, "roteiro.py"), "roteiro")
    falas, cenas = linha_do_tempo(ep_dir, rot)
    total = cenas[-1]["fim"]
    saida = os.path.join(ep_dir, "saida")
    os.makedirs(saida, exist_ok=True)
    mix, boca = montar_audio(falas, cenas, total)
    cj = [dict(nome=c["nome"], ini=c["ini"], fim=c["fim"], D=c["D"], cues=c["cues"]) for c in cenas]
    json.dump(dict(total=total, cenas=cj,
                   falas=[dict(n=f["n"], cena=f["cena"], ini=round(f["ini"], 2), fim=round(f["fim"], 2),
                               gravada=f["gravada"], texto=f["texto"]) for f in falas]),
              open(os.path.join(saida, "linha_do_tempo.json"), "w"), ensure_ascii=False, indent=1)
    gravadas = sum(f["gravada"] for f in falas)
    print(f"duracao {total:.1f}s | {len(cenas)} cenas | falas gravadas: {gravadas}/{len(falas)}")

    escala = 0.5 if a.rapido else 1.0
    if a.quadros:
        _init(ep_dir, cj, boca, escala)
        for seg in a.quadros.split(","):
            q = int(float(seg) * FPS)
            s = _superficie()
            ctx = _ctx(s)
            desenhar_quadro(ctx, q)
            p = os.path.join(saida, f"quadro_{float(seg):06.1f}.png")
            s.write_to_png(p)
            print(p)
        return

    nq = int(math.ceil(total * FPS))
    k = max(1, a.procs)
    lim = [round(nq * i / k) for i in range(k + 1)]
    trechos = [(lim[i], lim[i + 1], os.path.join(saida, f"_trecho{i}.mp4")) for i in range(k)]
    with get_context("fork").Pool(k, initializer=_init, initargs=(ep_dir, cj, boca, escala)) as pool:
        feitos = pool.map(render_trecho, trechos)
    lista = os.path.join(saida, "_lista.txt")
    open(lista, "w").write("".join(f"file '{p}'\n" for p in feitos))
    wav = os.path.join(saida, "_mix.wav")
    pcm = np.clip(mix, -1, 1)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), wav],
                   input=pcm.astype(np.float32).tobytes(), check=True)
    final = os.path.join(saida, f"{a.ep}{'_rapido' if a.rapido else ''}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista, "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final],
                   check=True)
    for p in feitos + [lista, wav]:
        os.remove(p)
    escrever_legendas(falas, os.path.join(saida, f"{a.ep}.srt"))
    open(os.path.join(saida, "capitulos.txt"), "w").write("\n".join(capitulos(cenas, rot)) + "\n")
    print(final)


if __name__ == "__main__":
    main()
