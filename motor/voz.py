"""Gera a voz de rascunho (Piper TTS) para as falas que ainda nao foram gravadas.

Uso: python3 motor/voz.py ep01
"""
import importlib.util, os, subprocess, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = os.environ.get("PIPER_MODELO", os.path.join(RAIZ, "motor", "voz", "pt-br-edresson-low.onnx"))


def carregar_roteiro(ep):
    p = os.path.join(RAIZ, ep, "roteiro.py")
    spec = importlib.util.spec_from_file_location("roteiro", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main(ep):
    rot = carregar_roteiro(ep)
    pasta = os.path.join(RAIZ, ep, "falas", "rascunho")
    os.makedirs(pasta, exist_ok=True)
    os.makedirs(os.path.join(RAIZ, ep, "falas", "gravadas"), exist_ok=True)
    for i, (_, texto) in enumerate(rot.FALAS, 1):
        destino = os.path.join(pasta, f"{i:02d}.wav")
        marca = destino + ".txt"
        if os.path.exists(destino) and os.path.exists(marca) and open(marca).read() == texto:
            continue
        bruto = destino + ".raw.wav"
        subprocess.run([sys.executable, "-m", "piper", "-m", MODELO, "-f", bruto,
                        "--length-scale", "1.05", "--sentence-silence", "0.25"],
                       input=texto.encode(), check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", bruto, "-ar", "48000", "-ac", "1", destino], check=True)
        os.remove(bruto)
        open(marca, "w").write(texto)
        print("voz", f"{i:02d}", texto[:50])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ep01")
