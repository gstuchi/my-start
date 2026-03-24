"""
Geração de dicas e insights personalizados com base nos dados calculados.
"""

import random


DICAS = {
    "perder": [
        "Distribua a proteína em pelo menos 4 refeições para preservar a massa muscular durante o déficit.",
        "Beba pelo menos 35ml de água por kg de peso ao dia — a hidratação acelera a queima de gordura.",
        "Prefira carboidratos de baixo índice glicêmico (batata-doce, aveia, arroz integral) para manter a saciedade.",
    ],
    "recomp": [
        "Concentre a maior parte dos carboidratos no pré e pós-treino para maximizar a recomposição corporal.",
        "Durma 7–9 horas por noite — é durante o sono que ocorre a síntese proteica e queima de gordura.",
        "Na recomposição, consistência é tudo: siga o plano por pelo menos 8 semanas antes de ajustar.",
    ],
    "ganhar": [
        "Não pule refeições — o superávit calórico precisa ser consistente para estimular o ganho muscular.",
        "Priorize o pós-treino: consuma proteína + carboidratos em até 1 hora após o treino.",
        "Se estiver difícil bater as calorias, adicione azeite, pasta de amendoim e abacate às refeições.",
    ],
}


def gerar_dica(objetivo: str) -> str:
    """Retorna uma dica aleatória baseada no objetivo."""
    return random.choice(DICAS.get(objetivo, DICAS["recomp"]))


def gerar_insight(kcal: int, objetivo: str, tmb: float, tdee: float) -> str:
    """Retorna um insight personalizado com os dados calculados."""
    if objetivo == "perder":
        deficit  = round(tdee - kcal)
        kg_mes   = round(deficit * 30 / 7700, 1)
        return (f"Com déficit de {deficit} kcal/dia sobre seu TDEE de {round(tdee)} kcal, "
                f"você pode perder aproximadamente {kg_mes}kg por mês de forma saudável.")

    elif objetivo == "ganhar":
        superavit = round(kcal - tdee)
        return (f"O superávit de {superavit} kcal sobre seu TDEE de {round(tdee)} kcal "
                f"é suficiente para ganho muscular limpo com mínimo acúmulo de gordura.")

    else:  # recomp
        deficit = round(tdee - kcal)
        return (f"Com TDEE de {round(tdee)} kcal e plano de {kcal} kcal, o leve déficit de "
                f"{deficit} kcal/dia favorece a perda de gordura sem sacrificar o ganho muscular.")
