# Episodio 01 - Por que o ceu e azul?
# Cada fala vira um arquivo de audio: falas/gravadas/NN.wav (sua voz) tem
# prioridade sobre falas/rascunho/NN.wav (voz sintetica). O video se
# re-sincroniza sozinho pela duracao de cada arquivo.

TITULO = "Por que o céu é azul?"
PROXIMO = "Por que a Lua muda de forma?"

# (cena, texto da fala)
FALAS = [
    ("gancho",    "Você já olhou pro céu e se perguntou: por que ele é azul?"),
    ("abertura",  "Eu sou o Teco, e essa é a Lume. Bem-vindos à Fábrica de Porquês!"),
    ("abertura",  "Hoje a gente vai descobrir o segredo da cor do céu."),
    ("mito",      "Tem gente que diz que o céu é azul porque ele reflete o mar."),
    ("mito",      "Mas pensa comigo: no meio do deserto, bem longe do mar, o céu também é azul!"),
    ("mito",      "Então não pode ser isso. O segredo está na luz do Sol."),
    ("prisma",    "A luz do Sol parece branquinha. Mas ela é uma mistura de todas as cores!"),
    ("prisma",    "Quando ela passa por um prisma, ou pelas gotinhas de chuva, as cores se separam. É assim que nasce o arco-íris."),
    ("ar",        "Agora, olha o ar com a minha lupa. Parece vazio, né?"),
    ("ar",        "Mas ele está cheio de partículas minúsculas, pequenas demais pra gente enxergar."),
    ("espalha",   "Quando a luz do Sol chega no ar, cada cor se comporta de um jeito."),
    ("espalha",   "O vermelho e o laranja passam quase direto."),
    ("espalha",   "Já o azul esbarra nas partículas e se espalha pra todo lado, igual bolinha de pinball!"),
    ("olho",      "Como o azul se espalhou pelo céu inteiro, pra onde você olha chega um pouquinho de azul nos seus olhos."),
    ("olho",      "Por isso o céu todo parece azul!"),
    ("por_do_sol","E no fim da tarde? O Sol fica baixinho, e a luz precisa atravessar muito mais ar até chegar em você."),
    ("por_do_sol","No caminho, o azul vai se espalhando e ficando pra trás. Quem chega são o laranja e o vermelho."),
    ("por_do_sol","Por isso o pôr do sol é alaranjado!"),
    ("experimento","Quer ver isso em casa? Pegue um copo de vidro com água e pingue umas gotas de leite."),
    ("experimento","Com a ajuda de um adulto, ilumine o copo com uma lanterna."),
    ("experimento","Olhando de lado, a água fica azulada. E a luz que atravessa o copo sai alaranjada. É um céu dentro do copo!"),
    ("resumo",    "Resumindo: a luz do Sol tem todas as cores."),
    ("resumo",    "O azul é a cor que mais se espalha no ar, e por isso o céu é azul."),
    ("resumo",    "E no pôr do sol, o azul fica pelo caminho e sobra o laranja."),
    ("final",     "No próximo episódio: por que a Lua muda de forma? Até lá, continue perguntando porquê!"),
]

# Titulos de capitulo (descricao do YouTube)
CAPITULOS = {
    "gancho": "A pergunta",
    "mito": "O céu reflete o mar?",
    "prisma": "A luz do Sol tem todas as cores",
    "ar": "O que tem no ar",
    "espalha": "O azul se espalha",
    "por_do_sol": "E o pôr do sol?",
    "experimento": "Experimento em casa",
    "resumo": "Resumo",
}
