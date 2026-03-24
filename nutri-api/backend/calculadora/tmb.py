"""
Cálculo de Taxa Metabólica Basal (TMB) e Gasto Energético Diário (TDEE).
Fórmula: Mifflin-St Jeor (mais precisa que Harris-Benedict).
"""

FATORES_ATIVIDADE = {
    1.2:   "Sedentário",
    1.375: "Levemente ativo",
    1.55:  "Moderadamente ativo",
    1.725: "Muito ativo",
    1.9:   "Extremamente ativo",
}

AJUSTE_OBJETIVO = {
    "perder": -500,
    "recomp": -200,
    "ganhar": +300,
}


def calcular_tmb(peso: float, altura: float, idade: float, sexo: str) -> float:
    """Retorna a TMB em kcal/dia."""
    base = (10 * peso) + (6.25 * altura) - (5 * idade)
    return base + 5 if sexo == "m" else base - 161


def calcular_tdee(tmb: float, fator_atividade: float) -> float:
    """Retorna o gasto calórico diário total (TDEE)."""
    return tmb * fator_atividade


def calcular_kcal_alvo(tdee: float, objetivo: str) -> int:
    """Ajusta as calorias com base no objetivo do usuário."""
    ajuste = AJUSTE_OBJETIVO.get(objetivo, 0)
    return round(tdee + ajuste)
