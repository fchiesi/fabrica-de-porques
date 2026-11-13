#!/usr/bin/env bash
# Baixa o modelo de voz de rascunho (Piper, pt-BR) para motor/voz/
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p voz
curl -sSL https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-pt-br-edresson-low.tar.gz | tar xz -C voz
ls voz
