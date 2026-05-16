from flask import Flask, request, render_template_string
import random
import re

app = Flask(__name__)

# =========================
# ELEMENTOS
# =========================

ELEMENTOS = {
    "🔥": "Fogo",
    "💧": "Água",
    "⚡": "Raio",
    "🌪️": "Vento",
    "🌑": "Sombra",
    "🌀": "Ciclone",
    "💨": "Fumaça",
    "💎": "Diamante",
}

# =========================
# REINOS POR ELEMENTO
# =========================

REINOS_POR_ELEMENTO = {
    "Fogo": "Clover",
    "Água": "Clover",
    "Raio": "Clover",
    "Vento": "Clover",
    "Sombra": "Clover",

    "Ciclone": "Diamond",
    "Fumaça": "Diamond",
    "Diamante": "Diamond",
}

# =========================
# ESQUADRÕES
# =========================

ESQUADROES = [
    "🦚", "🦗", "🦁", "☀️", "🐃",
    "🦅", "🌹", "💮", "💠",
    "🌠", "🎇", "💫", "🌅"
]

# =========================
# NUMERAÇÃO BONITA
# =========================

NUMEROS_ESTILO = {
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
    10: "1️⃣0️⃣",
    11: "1️⃣1️⃣",
    12: "1️⃣2️⃣",
    13: "1️⃣3️⃣",
    14: "1️⃣4️⃣",
    15: "1️⃣5️⃣",
    16: "1️⃣6️⃣",
    17: "1️⃣7️⃣",
    18: "1️⃣8️⃣",
    19: "1️⃣9️⃣",
    20: "2️⃣0️⃣",
    21: "2️⃣1️⃣",
    22: "2️⃣2️⃣",
    23: "2️⃣3️⃣",
    24: "2️⃣4️⃣",
    25: "2️⃣5️⃣",
    26: "2️⃣6️⃣",
    27: "2️⃣7️⃣",
    28: "2️⃣8️⃣",
    29: "2️⃣9️⃣",
    30: "3️⃣0️⃣",
}

# =========================
# LIMPEZA
# =========================

def limpar_linha(linha):
    linha = linha.strip()

    # remove mensagens estilo whatsapp
    if linha.startswith("[") and "]" in linha and ":" in linha:
        return ""

    linha = linha.strip("*").strip()

    return linha

# =========================
# EXTRAIR NOME
# =========================

def extrair_nome_linha(linha):
    linha = limpar_linha(linha)

    if not linha:
        return None

    linha = re.sub(
        r"^\s*(?:\d+|[0-9️⃣⃣]+)\s*:\s*",
        "",
        linha
    ).strip()

    linha = linha.strip("*").strip()

    return linha if linha else None

# =========================
# ELEMENTOS
# =========================

def extrair_elementos(nome):
    encontrados = []

    for emoji, tipo in ELEMENTOS.items():
        if emoji in nome:
            encontrados.append(tipo)

    return list(dict.fromkeys(encontrados))

# =========================
# ESQUADRÕES
# =========================

def extrair_esquadroes(nome):
    encontrados = []

    for e in ESQUADROES:
        if e in nome:
            encontrados.append(e)

    return list(dict.fromkeys(encontrados))

# =========================
# REINOS
# =========================

def descobrir_reino(jogador):
    reinos = set()

    for elemento in jogador["elementos"]:
        reino = REINOS_POR_ELEMENTO.get(elemento)

        if reino:
            reinos.add(reino)

    return list(reinos)

# =========================
# PARSE DA LISTA
# =========================

def parse_lista(texto):
    jogadores = []
    nomes_vistos = set()

    for linha in texto.splitlines():
        nome = extrair_nome_linha(linha)

        if not nome:
            continue

        if nome in nomes_vistos:
            continue

        nomes_vistos.add(nome)

        jogador = {
            "nome": nome,
            "elementos": extrair_elementos(nome),
            "esquadroes": extrair_esquadroes(nome),
        }

        jogador["reinos"] = descobrir_reino(jogador)

        jogadores.append(jogador)

    return jogadores

# =========================
# CONFLITOS
# =========================

def conflito_reino(p1, p2):
    return bool(set(p1["reinos"]) & set(p2["reinos"]))

def conflito_esquadrao(p1, p2):
    return bool(set(p1["esquadroes"]) & set(p2["esquadroes"]))

def conflito_elemento(p1, p2):
    return bool(set(p1["elementos"]) & set(p2["elementos"]))

# =========================
# SCORE
# =========================

def score_par(p1, p2):
    score = 1000

    # prioridade máxima
    if conflito_reino(p1, p2):
        score -= 2000

    # prioridade secundária
    if conflito_esquadrao(p1, p2):
        score -= 1000

    # prioridade leve
    if conflito_elemento(p1, p2):
        score -= 120

    # aleatório leve
    score += random.randint(0, 15)

    return score

# =========================
# EMPARELHAMENTO
# =========================

def gerar_emparelhamento(jogadores, tentativas=4000):
    if len(jogadores) < 2:
        return [], None

    melhor_lutas = None
    melhor_sobra = None
    melhor_score_total = -10**9

    for _ in range(tentativas):
        pool = jogadores[:]
        random.shuffle(pool)

        lutas = []
        score_total = 0

        while len(pool) >= 2:
            p1 = pool.pop(0)

            melhor_idx = None
            melhor_score = -10**9

            for i, p2 in enumerate(pool):
                s = score_par(p1, p2)

                if s > melhor_score:
                    melhor_score = s
                    melhor_idx = i

            p2 = pool.pop(melhor_idx)

            lutas.append((p1, p2))
            score_total += melhor_score

        sobra = pool[0] if pool else None

        if score_total > melhor_score_total:
            melhor_score_total = score_total
            melhor_lutas = lutas
            melhor_sobra = sobra

    return melhor_lutas, melhor_sobra

# =========================
# NUMERAÇÃO
# =========================

def numero_estilizado(n):
    return NUMEROS_ESTILO.get(n, str(n))

# =========================
# RESULTADO
# =========================

def formatar_resultado(lutas, sobra=None):
    blocos = []

    for i, (p1, p2) in enumerate(lutas, 1):
        num = numero_estilizado(i)

        blocos.append(
            f"🥋 Luta ꪶ-{num}-ꫂ\n"
            f"{p1['nome']}\n"
            f"🆚\n"
            f"{p2['nome']}"
        )

    if sobra:
        blocos.append(
            f"⚠️ Sem par\n"
            f"{sobra['nome']}"
        )

    return "\n\n".join(blocos)

# =========================
# HTML
# =========================

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Sorteador 2000 LGhostt</title>

<style>
body{
    background:#0a0a0a;
    color:white;
    font-family:Arial;
    padding:20px;
}

textarea{
    width:100%;
    height:350px;
    background:#111;
    color:white;
    border:1px solid #333;
    padding:15px;
    border-radius:10px;
}

button{
    margin-top:10px;
    padding:12px 18px;
    border:none;
    border-radius:10px;
    background:#ff2d55;
    color:white;
    font-weight:bold;
    cursor:pointer;
}

pre{
    background:#111;
    padding:15px;
    border-radius:10px;
    margin-top:20px;
    white-space:pre-wrap;
}
</style>
</head>

<body>

<h1>😁🔥 Sorteador 2000 💮😝</h1>

<form method="post">

<textarea
name="lista"
placeholder="Cole aqui a lista..."
>{{ lista_texto }}</textarea>

<br>

<button type="submit">
🥋 Sortear lutas
</button>

</form>

<pre>{{ resultado }}</pre>

</body>
</html>
"""

# =========================
# ROTA
# =========================

@app.route("/", methods=["GET", "POST"])
def home():
    resultado = "Cole a lista e clique em sortear."
    lista_texto = ""

    if request.method == "POST":
        lista_texto = request.form.get("lista", "")

        jogadores = parse_lista(lista_texto)

        if len(jogadores) < 2:
            resultado = "Adicione pelo menos 2 participantes."
        else:
            lutas, sobra = gerar_emparelhamento(jogadores)
            resultado = formatar_resultado(lutas, sobra)

    return render_template_string(
        HTML,
        resultado=resultado,
        lista_texto=lista_texto
    )

# =========================
# START
# =========================

if __name__ == "__main__":
    app.run(debug=True)
