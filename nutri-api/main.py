import math
import random
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="NutriCalc API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── MODELOS ────────────────────────────────────
class UserData(BaseModel):
    peso: float
    altura: float
    idade: float
    sexo: str        # 'm' ou 'f'
    atividade: float
    objetivo: str    # 'perder', 'recomp', 'ganhar'


# ── MOTOR NUTRICIONAL ──────────────────────────

def calcular_tmb(peso, altura, idade, sexo):
    """Harris-Benedict revisado (Mifflin-St Jeor — mais preciso)"""
    if sexo == 'm':
        return (10 * peso) + (6.25 * altura) - (5 * idade) + 5
    else:
        return (10 * peso) + (6.25 * altura) - (5 * idade) - 161


def calcular_imc(peso, altura):
    altura_m = altura / 100
    imc = peso / (altura_m ** 2)

    if imc < 18.5:
        label = "Abaixo do peso"
        desc  = (f"Seu IMC de {imc:.1f} indica abaixo do peso ideal. "
                 f"Priorize um superávit calórico com alimentos nutritivos e proteína adequada para ganhar massa de forma saudável.")
        pct   = 18
    elif imc < 25:
        label = "Peso saudável"
        desc  = (f"Ótimo! Seu IMC de {imc:.1f} está na faixa ideal. "
                 f"Foque em manter a composição corporal e melhorar a performance nos treinos.")
        pct   = 52
    elif imc < 30:
        label = "Sobrepeso"
        desc  = (f"Seu IMC de {imc:.1f} indica sobrepeso. "
                 f"Reduzir a gordura corporal vai melhorar sua saúde, energia e desempenho nos treinos.")
        pct   = 72
    else:
        label = "Obesidade"
        desc  = (f"Seu IMC de {imc:.1f} merece atenção. "
                 f"Um déficit calórico moderado combinado com treino resistido é o caminho mais seguro.")
        pct   = 90

    return round(imc, 1), label, desc, pct


def calcular_macros(kcal, peso, objetivo):
    """Distribui macros baseado em evidências científicas."""
    # Proteína: 2.0g/kg (perda) | 2.2g/kg (recomp) | 1.8g/kg (ganho)
    fator_prot = {"perder": 2.0, "recomp": 2.2, "ganhar": 1.8}.get(objetivo, 2.0)
    prot = round(peso * fator_prot)
    prot_kcal = prot * 4

    # Gordura: 25% das calorias
    gord_kcal = round(kcal * 0.25)
    gord = round(gord_kcal / 9)

    # Carboidratos: restante
    carb_kcal = kcal - prot_kcal - gord_kcal
    carb = round(carb_kcal / 4)

    total = prot_kcal + gord_kcal + carb_kcal
    prot_pct = round(prot_kcal / total * 100)
    carb_pct = round(carb_kcal / total * 100)
    gord_pct = round(gord_kcal / total * 100)

    return prot, carb, gord, prot_pct, carb_pct, gord_pct


def gerar_cardapio(peso, kcal, objetivo, sexo):
    """
    Gera cardápio com porções calculadas dinamicamente
    com base no peso, calorias totais e objetivo.
    """
    # Distribuição calórica por refeição (% do total diário)
    dist = {
        "perder": [0.22, 0.10, 0.15, 0.28, 0.18, 0.07],
        "recomp": [0.20, 0.10, 0.17, 0.27, 0.19, 0.07],
        "ganhar": [0.20, 0.12, 0.18, 0.28, 0.17, 0.05],
    }
    pcts = dist.get(objetivo, dist["recomp"])
    kcals = [round(kcal * p) for p in pcts]

    # Porções calculadas por peso (g)
    arroz      = round(peso * 1.2)   # ~1.2g arroz por kg
    frango     = round(peso * 1.5)   # ~1.5g proteína por kg no pós-treino
    ovo_qtd    = max(3, round(peso / 20))
    batata     = round(peso * 0.8)
    iogurte    = 200 if peso < 80 else 250
    pasta_am   = 1 if peso < 70 else 2  # colheres
    cottage    = 150 if peso < 80 else 200
    fruta_tam  = "média" if peso < 80 else "grande"

    # Templates por objetivo
    if objetivo == "perder":
        refeicoes = [
            {"time": "07H", "name": "Café da manhã",
             "items": f"{ovo_qtd} ovos mexidos + 1 fatia pão integral + 1 fruta {fruta_tam} + café preto"},
            {"time": "10H", "name": "Lanche",
             "items": f"{iogurte}g iogurte grego natural + {pasta_am} col. pasta de amendoim sem açúcar"},
            {"time": "PRÉ", "name": "Pré-treino",
             "items": f"{batata}g batata-doce + {round(frango*0.6)}g frango grelhado + salada verde"},
            {"time": "PÓS", "name": "Pós-treino",
             "items": f"{round(arroz*0.8)}g arroz branco + {frango}g frango/carne magra + legumes refogados"},
            {"time": "19H", "name": "Jantar",
             "items": f"{round(frango*0.9)}g peixe ou frango + salada à vontade + {round(batata*0.5)}g abobrinha"},
            {"time": "CEIA", "name": "Ceia",
             "items": f"{cottage}g cottage ou clara de ovo + 1 fruta pequena"},
        ]

    elif objetivo == "ganhar":
        refeicoes = [
            {"time": "07H", "name": "Café da manhã",
             "items": f"{ovo_qtd+1} ovos mexidos + 2 fatias pão integral + 1 banana + 1 col. azeite"},
            {"time": "10H", "name": "Lanche reforçado",
             "items": f"1 iogurte grego + {pasta_am+1} col. pasta de amendoim + 1 fruta {fruta_tam}"},
            {"time": "PRÉ", "name": "Pré-treino reforçado",
             "items": f"{arroz}g arroz + {round(frango*0.8)}g frango grelhado + salada"},
            {"time": "PÓS", "name": "Pós-treino",
             "items": f"{round(arroz*1.2)}g arroz branco + {frango}g carne/frango + legumes + 1 fio de azeite"},
            {"time": "19H", "name": "Jantar",
             "items": f"{round(frango*0.9)}g proteína + {batata}g batata-doce ou macarrão + salada"},
            {"time": "CEIA", "name": "Ceia",
             "items": f"{iogurte}g iogurte grego + 30g granola + 1 banana"},
        ]

    else:  # recomp
        refeicoes = [
            {"time": "07H", "name": "Café da manhã",
             "items": f"{ovo_qtd} ovos + 1 fatia pão integral + 1 fruta {fruta_tam} + café"},
            {"time": "10H", "name": "Lanche",
             "items": f"{iogurte}g iogurte grego + {pasta_am} col. pasta de amendoim + 1 maçã"},
            {"time": "PRÉ", "name": "Pré-treino",
             "items": f"{batata}g batata-doce + {round(frango*0.7)}g frango grelhado + café"},
            {"time": "PÓS", "name": "Pós-treino",
             "items": f"{arroz}g arroz + {frango}g frango ou carne + legumes refogados no azeite"},
            {"time": "19H", "name": "Jantar",
             "items": f"{round(frango*0.9)}g proteína + {round(batata*0.6)}g carboidrato + salada à vontade"},
            {"time": "CEIA", "name": "Ceia",
             "items": f"{cottage}g cottage ou iogurte natural + 1 fruta pequena"},
        ]

    # Associa as kcal calculadas a cada refeição
    for i, r in enumerate(refeicoes):
        r["kcal"] = kcals[i]

    return refeicoes


def gerar_dica(objetivo, peso, kcal, sexo):
    dicas = {
        "perder": [
            f"Distribua as {round(peso * 2)}g de proteína em pelo menos 4 refeições para preservar a massa muscular durante o déficit.",
            "Beba pelo menos 35ml de água por kg de peso ao dia — a hidratação acelera a queima de gordura.",
            "Prefira carboidratos de baixo índice glicêmico (batata-doce, aveia, arroz integral) para manter a saciedade.",
        ],
        "recomp": [
            "Concentre a maior parte dos carboidratos no pré e pós-treino para maximizar a recomposição corporal.",
            "Durma 7–9 horas por noite — é durante o sono que ocorre a síntese proteica e queima de gordura.",
            f"Com {round(kcal)} kcal e {round(peso * 2.2)}g de proteína, você está no ponto ideal para recomposição.",
        ],
        "ganhar": [
            "Não pule refeições — o superávit calórico precisa ser consistente para estimular o ganho muscular.",
            "Priorize o pós-treino: consuma proteína + carboidratos em até 1 hora após o treino.",
            f"Se estiver difícil atingir {round(kcal)} kcal, adicione azeite, pasta de amendoim e abacate às refeições.",
        ],
    }
    return random.choice(dicas.get(objetivo, dicas["recomp"]))


def gerar_insight(peso, kcal, objetivo, tmb, tdee):
    insights = {
        "perder": (
            f"Seu metabolismo basal de {round(tmb)} kcal consome energia mesmo em repouso — "
            f"com o déficit de {round(tdee - kcal)} kcal/dia você pode perder ~{round((tdee - kcal) * 30 / 7700, 1)}kg por mês."
        ),
        "recomp": (
            f"Com TDEE de {round(tdee)} kcal e plano de {round(kcal)} kcal, o leve déficit de "
            f"{round(tdee - kcal)} kcal diários favorece a perda de gordura sem sacrificar o ganho muscular."
        ),
        "ganhar": (
            f"O superávit de {round(kcal - tdee)} kcal sobre seu TDEE de {round(tdee)} kcal "
            f"é suficiente para ganho muscular limpo com mínimo acúmulo de gordura."
        ),
    }
    return insights.get(objetivo, "")


# ── ENDPOINT ───────────────────────────────────
@app.post("/api/calcular")
def calcular(data: UserData):
    if not (30 <= data.peso <= 300):
        raise HTTPException(400, "Peso fora do intervalo permitido (30–300 kg)")
    if not (100 <= data.altura <= 250):
        raise HTTPException(400, "Altura fora do intervalo permitido (100–250 cm)")
    if not (10 <= data.idade <= 100):
        raise HTTPException(400, "Idade fora do intervalo permitido (10–100 anos)")
    if data.objetivo not in ("perder", "recomp", "ganhar"):
        raise HTTPException(400, "Objetivo inválido")

    # Cálculos principais
    tmb  = calcular_tmb(data.peso, data.altura, data.idade, data.sexo)
    tdee = tmb * data.atividade

    ajuste = {"perder": -500, "recomp": -200, "ganhar": +300}
    kcal   = round(tdee + ajuste[data.objetivo])

    prot, carb, gord, prot_pct, carb_pct, gord_pct = calcular_macros(kcal, data.peso, data.objetivo)
    imc, imc_label, imc_desc, imc_pct = calcular_imc(data.peso, data.altura)
    meals   = gerar_cardapio(data.peso, kcal, data.objetivo, data.sexo)
    tip     = gerar_dica(data.objetivo, data.peso, kcal, data.sexo)
    insight = gerar_insight(data.peso, kcal, data.objetivo, tmb, tdee)

    return {
        "tmb":      round(tmb),
        "tdee":     round(tdee),
        "kcal":     kcal,
        "prot":     prot,
        "carb":     carb,
        "gord":     gord,
        "prot_pct": prot_pct,
        "carb_pct": carb_pct,
        "gord_pct": gord_pct,
        "imc":      imc,
        "imc_label": imc_label,
        "imc_desc":  imc_desc,
        "imc_pct":   imc_pct,
        "meals":     meals,
        "tip":       tip,
        "insight":   insight,
    }


# Serve o frontend — deve ficar DEPOIS das rotas da API
app.mount("/", StaticFiles(directory="static", html=True), name="static")
