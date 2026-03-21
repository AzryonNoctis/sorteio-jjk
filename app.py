from flask import Flask, request, render_template_string
import random
import html
import re

app = Flask(__name__)

# Elementos reconhecidos
ELEMENTOS = {
    "🔥": "Fogo",
    "💧": "Água",
    "⚡": "Raio",
    "🌪️": "Vento",
    "🌑": "Sombra",
}

# Esquadrões / casas / marcas
ESQUADROES = ["🦚", "🦗", "🦁", "☀️", "🐃", "🦅", "🌹", "💮", "💠"] 

# Emojis numéricos bonitos para o título da luta
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

def limpar_linha(linha):
    linha = linha.strip()

    # remove cabeçalho tipo [21/03, 15:14] Kyomi 🌪️:
    if linha.startswith("[") and "]" in linha and ":" in linha:
        return ""

    # remove * das pontas e espaços extras
    linha = linha.strip("*").strip()

    return linha

def extrair_nome_linha(linha):
    linha = limpar_linha(linha)

    if not linha:
        return None

    # Remove numeração do começo:
    # 01: Nome
    # 1: Nome
    # 0️⃣1️⃣: Nome
    # 1️⃣0️⃣: Nome
    linha = re.sub(r"^\s*(?:\d+|[0-9️⃣⃣]+)\s*:\s*", "", linha).strip()

    # remove * perdidos no final/início
    linha = linha.strip("*").strip()

    return linha if linha else None

def extrair_elementos(nome):
    encontrados = []
    for emoji, tipo in ELEMENTOS.items():
        if emoji in nome:
            encontrados.append(tipo)
    return list(dict.fromkeys(encontrados))

def extrair_esquadroes(nome):
    encontrados = []
    for e in ESQUADROES:
        if e in nome:
            encontrados.append(e)
    return list(dict.fromkeys(encontrados))

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
        jogadores.append({
            "nome": nome,
            "elementos": extrair_elementos(nome),
            "esquadroes": extrair_esquadroes(nome),
        })

    return jogadores

def conflito_esquadrao(p1, p2):
    return bool(set(p1["esquadroes"]) & set(p2["esquadroes"]))

def conflito_elemento(p1, p2):
    elems1 = [e for e in p1["elementos"] if e != "Especial"]
    elems2 = [e for e in p2["elementos"] if e != "Especial"]
    return bool(set(elems1) & set(elems2))

def score_par(p1, p2):
    score = 1000

    # Prioridade máxima: não repetir esquadrão
    if conflito_esquadrao(p1, p2):
        score -= 1000

    # Segunda prioridade: não repetir elemento
    if conflito_elemento(p1, p2):
        score -= 120

    # Pequeno bônus por diversidade geral
    score += random.randint(0, 15)

    return score

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

            # se zerou conflito de esquadrão e elemento, já tá excelente
            conflito_pesado = any(conflito_esquadrao(a, b) for a, b in lutas)
            conflito_leve = any(conflito_elemento(a, b) for a, b in lutas)

            if not conflito_pesado and not conflito_leve:
                break

    return melhor_lutas, melhor_sobra

def numero_estilizado(n):
    return NUMEROS_ESTILO.get(n, str(n))

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

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Sorteador 2000 LGhostt</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, Helvetica, sans-serif;
            color: #f5f5f5;
            background:
                radial-gradient(circle at 20% 20%, rgba(106, 13, 173, 0.18), transparent 25%),
                radial-gradient(circle at 80% 30%, rgba(0, 153, 255, 0.16), transparent 25%),
                radial-gradient(circle at 50% 80%, rgba(220, 20, 60, 0.18), transparent 30%),
                linear-gradient(135deg, #050505 0%, #0a0a0a 45%, #120507 100%);
            overflow-x: hidden;
        }

        .particles {
            position: fixed;
            inset: 0;
            pointer-events: none;
            overflow: hidden;
            z-index: 0;
        }

        .particle {
            position: absolute;
            border-radius: 999px;
            opacity: 0.8;
            filter: blur(1px);
            animation: floatUp linear infinite;
        }

        .p1 { width: 6px; height: 6px; background: #2f7bff; left: 8%; animation-duration: 11s; animation-delay: 0s; }
        .p2 { width: 5px; height: 5px; background: #ff204e; left: 18%; animation-duration: 14s; animation-delay: 2s; }
        .p3 { width: 7px; height: 7px; background: #8b3dff; left: 29%; animation-duration: 13s; animation-delay: 1s; }
        .p4 { width: 4px; height: 4px; background: #2f7bff; left: 40%; animation-duration: 10s; animation-delay: 3s; }
        .p5 { width: 6px; height: 6px; background: #ff204e; left: 52%; animation-duration: 15s; animation-delay: 1s; }
        .p6 { width: 5px; height: 5px; background: #8b3dff; left: 63%; animation-duration: 12s; animation-delay: 4s; }
        .p7 { width: 7px; height: 7px; background: #2f7bff; left: 73%; animation-duration: 16s; animation-delay: 2s; }
        .p8 { width: 4px; height: 4px; background: #ff204e; left: 84%; animation-duration: 11s; animation-delay: 5s; }
        .p9 { width: 6px; height: 6px; background: #8b3dff; left: 92%; animation-duration: 13s; animation-delay: 3s; }

        @keyframes floatUp {
            0% {
                transform: translateY(100vh) scale(0.8);
                opacity: 0;
            }
            10% {
                opacity: 0.85;
            }
            90% {
                opacity: 0.65;
            }
            100% {
                transform: translateY(-12vh) scale(1.2);
                opacity: 0;
            }
        }

        .container {
            position: relative;
            z-index: 1;
            width: min(1100px, 92%);
            margin: 40px auto;
        }

        .card {
            background: linear-gradient(180deg, rgba(20,20,20,0.92), rgba(10,10,10,0.95));
            border: 1px solid rgba(255, 40, 80, 0.35);
            box-shadow:
                0 0 18px rgba(255, 30, 70, 0.18),
                0 0 60px rgba(90, 20, 160, 0.10),
                inset 0 0 20px rgba(255,255,255,0.02);
            border-radius: 22px;
            padding: 26px;
            backdrop-filter: blur(6px);
        }

        h1 {
            margin: 0 0 10px 0;
            text-align: center;
            color: #ffffff;
            font-size: clamp(28px, 5vw, 44px);
            text-shadow:
                0 0 10px rgba(255, 30, 70, 0.45),
                0 0 24px rgba(100, 40, 255, 0.25);
        }

        .subtitle {
            text-align: center;
            color: #d0d0d0;
            margin-bottom: 24px;
            font-size: 15px;
        }

        .highlight {
            color: #ff315f;
            font-weight: bold;
        }

        .blue {
            color: #57a6ff;
            font-weight: bold;
        }

        .purple {
            color: #9e62ff;
            font-weight: bold;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #f0f0f0;
        }

        textarea {
            width: 100%;
            min-height: 360px;
            resize: vertical;
            border-radius: 18px;
            border: 1px solid rgba(255, 40, 80, 0.35);
            background:
                linear-gradient(180deg, rgba(8,8,8,0.97), rgba(16,16,16,0.97));
            color: #ffffff;
            padding: 18px;
            font-size: 15px;
            outline: none;
            box-shadow:
                inset 0 0 18px rgba(255, 40, 80, 0.06),
                0 0 20px rgba(50, 100, 255, 0.06);
        }

        textarea:focus {
            border-color: rgba(255, 60, 95, 0.75);
            box-shadow:
                0 0 0 2px rgba(255, 45, 85, 0.18),
                0 0 26px rgba(255, 25, 75, 0.18);
        }

        .actions {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin-top: 18px;
        }

        button {
            border: none;
            border-radius: 14px;
            padding: 14px 20px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
        }

        .btn-main {
            background: linear-gradient(135deg, #8a0f2d, #ff244f);
            color: white;
            box-shadow: 0 0 18px rgba(255, 36, 79, 0.35);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #18213a, #314b8f);
            color: white;
            box-shadow: 0 0 18px rgba(47, 123, 255, 0.25);
        }

        .btn-tertiary {
            background: linear-gradient(135deg, #38185e, #7041c9);
            color: white;
            box-shadow: 0 0 18px rgba(139, 61, 255, 0.25);
        }

        button:hover {
            transform: translateY(-2px) scale(1.01);
            opacity: 0.97;
        }

        .result-box {
            margin-top: 26px;
            background:
                linear-gradient(180deg, rgba(7,7,7,0.98), rgba(16,16,16,0.98));
            border: 1px solid rgba(255, 40, 80, 0.28);
            border-radius: 18px;
            padding: 18px;
            box-shadow:
                inset 0 0 18px rgba(255,255,255,0.015),
                0 0 28px rgba(255, 20, 70, 0.08);
        }

        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: Consolas, monospace;
            margin: 0;
            color: #f5f5f5;
            font-size: 15px;
            line-height: 1.7;
        }

        .tips {
            margin-top: 16px;
            color: #d1d1d1;
            font-size: 14px;
            line-height: 1.6;
            background: rgba(255,255,255,0.02);
            border-left: 4px solid rgba(255, 36, 79, 0.75);
            padding: 14px 16px;
            border-radius: 12px;
        }

        .footer {
            margin-top: 18px;
            text-align: center;
            color: #999;
            font-size: 13px;
        }

        @media (max-width: 700px) {
            .container {
                width: 94%;
                margin: 20px auto;
            }

            .card {
                padding: 18px;
            }

            textarea {
                min-height: 280px;
            }

            .actions {
                flex-direction: column;
            }

            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="particles">
        <div class="particle p1"></div>
        <div class="particle p2"></div>
        <div class="particle p3"></div>
        <div class="particle p4"></div>
        <div class="particle p5"></div>
        <div class="particle p6"></div>
        <div class="particle p7"></div>
        <div class="particle p8"></div>
        <div class="particle p9"></div>
    </div>

    <div class="container">
        <div class="card">
            <h1>😁 🔥 Sorteador 2000! 💮 😝</h1>
            <div class="subtitle">
                Cole <span class="highlight">uma lista só</span> com todos os participantes.
                O sistema tenta evitar primeiro <span class="highlight">esquadrão igual</span>,
                depois <span class="blue">elemento igual</span>,
                com um brilho <span class="purple">roxamente suspeito</span>.
            </div>

            <form method="post">
                <label for="lista">Lista dos participantes</label>
                <textarea id="lista" name="lista" placeholder="Cole aqui a lista inteira...">{{ lista_texto }}</textarea>

                <div class="actions">
                    <button class="btn-main" type="submit">🥋 Sortear lutas</button>
                    <button class="btn-secondary" type="button" onclick="copiarResultado()">📋 Copiar resultado</button>
                    <button class="btn-tertiary" type="button" onclick="limparTudo()">🧹 Limpar</button>
                </div>
            </form>

            <div class="tips">
                <strong>Regras do sorteio:</strong><br>
                1. Evita <span class="highlight">esquadrão x mesmo esquadrão</span> primeiro.<br>
                2. Depois tenta evitar <span class="blue">elemento x mesmo elemento</span>.<br>
                3. Se a quantidade for ímpar, alguém fica sem par.
            </div>

            <div class="result-box">
                <pre id="resultado">{{ resultado }}</pre>
            </div>

            <div class="footer">
    preto no pano, escarlate no impacto, azul e roxo flutuando no caos.
</div>

<div style="
    margin-top: 10px;
    text-align: center;
    color: #cfcfcf;
    font-size: 14px;
    text-shadow: 0 0 8px rgba(255, 36, 79, 0.25);
">
    Por: LGhostt :D
</div>
        </div>
    </div>

    <script>
        function copiarResultado() {
            const texto = document.getElementById("resultado").innerText;
            navigator.clipboard.writeText(texto)
                .then(() => alert("Resultado copiado."))
                .catch(() => alert("Não consegui copiar automaticamente."));
        }

        function limparTudo() {
            document.getElementById("lista").value = "";
            document.getElementById("resultado").innerText = "";
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    resultado = "Cole a lista e clique em “Sortear lutas”."
    lista_texto = ""

    if request.method == "POST":
        lista_texto = request.form.get("lista", "")
        jogadores = parse_lista(lista_texto)

        if len(jogadores) < 2:
            resultado = "Adicione pelo menos 2 participantes válidos."
        else:
            lutas, sobra = gerar_emparelhamento(jogadores)
            resultado = formatar_resultado(lutas, sobra)

    return render_template_string(
        HTML,
        resultado=resultado,
        lista_texto=lista_texto
    )

if __name__ == "__main__":
    app.run(debug=True)