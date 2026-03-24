from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from calculadora import (
    calcular_tmb,
    calcular_tdee,
    calcular_imc,
    calcular_macros,
    gerar_cardapio,
    gerar_dica,
    gerar_insight,
)
from calculadora.tmb import calcular_kcal_alvo

app = FastAPI(title="NutriCalc API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserData(BaseModel):
    peso:      float
    altura:    float
    idade:     float
    sexo:      str    # 'm' ou 'f'
    atividade: float  # fator de atividade
    objetivo:  str    # 'perder', 'recomp' ou 'ganhar'


@app.post("/api/calcular")
def calcular(data: UserData):
    # Validações
    if not (30 <= data.peso <= 300):
        raise HTTPException(400, "Peso fora do intervalo permitido (30–300 kg)")
    if not (100 <= data.altura <= 250):
        raise HTTPException(400, "Altura fora do intervalo permitido (100–250 cm)")
    if not (10 <= data.idade <= 100):
        raise HTTPException(400, "Idade fora do intervalo permitido (10–100 anos)")
    if data.objetivo not in ("perder", "recomp", "ganhar"):
        raise HTTPException(400, "Objetivo inválido")

    # Cálculos
    tmb    = calcular_tmb(data.peso, data.altura, data.idade, data.sexo)
    tdee   = calcular_tdee(tmb, data.atividade)
    kcal   = calcular_kcal_alvo(tdee, data.objetivo)
    imc    = calcular_imc(data.peso, data.altura)
    macros = calcular_macros(kcal, data.peso, data.objetivo)
    meals  = gerar_cardapio(data.peso, kcal, data.objetivo)
    tip    = gerar_dica(data.objetivo)
    insight = gerar_insight(kcal, data.objetivo, tmb, tdee)

    return {
        "tmb":      round(tmb),
        "tdee":     round(tdee),
        "kcal":     kcal,
        "imc":      imc["imc"],
        "imc_label": imc["label"],
        "imc_desc":  imc["desc"],
        "imc_pct":   imc["pct"],
        **macros,
        "meals":    meals,
        "tip":      tip,
        "insight":  insight,
    }


# Frontend — deve ficar DEPOIS das rotas da API
app.mount("/", StaticFiles(directory="static", html=True), name="static")
