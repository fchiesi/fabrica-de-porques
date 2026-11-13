# Fábrica de Porquês

Canal de desenhos educativos de ciências e matemática para crianças de 6 a 9
anos, alinhado à BNCC. Cada episódio responde uma pergunta de criança em 2 a
4 minutos.

## Identidade
- **Teco**: robozinho voador azul-turquesa. **Narra tudo** (é a sua voz). Explica e mostra diagramas.
- **Lume**: menina de 8 anos, curiosa, de puffs no cabelo e presilha de estrela. **Não fala**: pergunta e reage com expressões. Por isso uma voz só basta para o episódio inteiro.
- **Visual**: vetor chapado, contorno azul-marinho grosso, fonte Fredoka.
- **Fórmula de cada episódio**: pergunta (gancho em 5 s) → vinheta → derrubar um mito → explicação em 3 passos visuais → experimento em casa → resumo em 3 cartões → próximo episódio.

## Como produzir um episódio
```
python3 motor/voz.py ep01        # voz de rascunho para o que ainda não foi gravado
python3 motor/render.py ep01     # vídeo final em ep01/saida/
python3 motor/render.py ep01 --quadros 10,45   # só imagens para conferir
```
Gravações reais vão em `ep01/falas/gravadas/01.m4a`, `02.m4a` etc. Elas
substituem o rascunho e o vídeo se re-sincroniza sozinho, inclusive a boca do Teco.

Preparação (uma vez):
```
pip install -r requirements.txt   # + ffmpeg instalado no sistema
motor/baixar_voz.sh               # voz de rascunho pt-BR (63 MB, fora do git)
```
Fonte: Fredoka (Google Fonts), instalada no sistema.

O vídeo `.mp4` não fica no git (é pesado e se refaz em ~2 min). A miniatura
e a legenda `.srt` ficam em `ep01/saida/`.

## Pauta (12 episódios)
1. Por que o céu é azul? ✅ piloto
2. Por que a Lua muda de forma?
3. Por que temos dia e noite?
4. Para onde vai a água da chuva? (ciclo da água)
5. O que é uma fração? (pizza)
6. Por que o gelo boia?
7. Como as plantas comem?
8. Por que a sombra muda de tamanho durante o dia?
9. Como funciona o ímã?
10. Por que multiplicar é somar rápido?
11. Para onde vai a comida que a gente come?
12. Por que o arco-íris aparece depois da chuva?
