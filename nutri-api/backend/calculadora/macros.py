"""
Distribuição de macronutrientes baseada em evidências científicas.

Proteína varia por objetivo:
  - Perda de gordura : 2.0 g/kg  (preservar massa magra)
  - Recomposição     : 2.2 g/kg  (ganho + perda simultâneos)
  - Ganho de massa   : 1.8 g/kg  (superávit favorece síntese)

Gordura  : 25% das calorias totais
Carboidrato: restante das calorias
"""

PROTEINA_POR_KG = {
    "perder": 2.0,
    "recomp": 2.2,
    "ganhar": 1.8,
}


def calcular_macros(kcal: int, peso: float, objetivo: str) -> dict:
    """Retorna gramas e percentuais de proteína, carboidrato e gordura."""
    fator = PROTEINA_POR_KG.get(objetivo, 2.0)

    prot      = round(peso * fator)
    prot_kcal = prot * 4

    gord_kcal = round(kcal * 0.25)
    gord      = round(gord_kcal / 9)

    carb_kcal = kcal - prot_kcal - gord_kcal
    carb      = round(carb_kcal / 4)

    total     = prot_kcal + gord_kcal + carb_kcal

    return {
        "prot":     prot,
        "carb":     carb,
        "gord":     gord,
        "prot_pct": round(prot_kcal / total * 100),
        "carb_pct": round(carb_kcal / total * 100),
        "gord_pct": round(gord_kcal / total * 100),
    }
