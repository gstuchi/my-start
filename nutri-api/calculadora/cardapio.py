"""
Geração de cardápio personalizado.
Porções calculadas dinamicamente com base no peso do usuário.
"""

# Distribuição calórica por refeição (% do total diário)
DISTRIBUICAO = {
    "perder": [0.22, 0.10, 0.15, 0.28, 0.18, 0.07],
    "recomp": [0.20, 0.10, 0.17, 0.27, 0.19, 0.07],
    "ganhar": [0.20, 0.12, 0.18, 0.28, 0.17, 0.05],
}


def _porcoes(peso: float) -> dict:
    """Calcula porções base de cada alimento pelo peso corporal."""
    return {
        "arroz":    round(peso * 1.2),
        "frango":   round(peso * 1.5),
        "ovos":     max(3, round(peso / 20)),
        "batata":   round(peso * 0.8),
        "iogurte":  200 if peso < 80 else 250,
        "pasta_am": 1   if peso < 70 else 2,
        "cottage":  150 if peso < 80 else 200,
        "fruta":    "média" if peso < 80 else "grande",
    }


def _refeicoes_perder(p: dict) -> list:
    return [
        {"time": "07H", "name": "Café da manhã",
         "items": f"{p['ovos']} ovos mexidos + 1 fatia pão integral + 1 fruta {p['fruta']} + café preto"},
        {"time": "10H", "name": "Lanche",
         "items": f"{p['iogurte']}g iogurte grego natural + {p['pasta_am']} col. pasta de amendoim sem açúcar"},
        {"time": "PRÉ", "name": "Pré-treino",
         "items": f"{p['batata']}g batata-doce + {round(p['frango'] * 0.6)}g frango grelhado + salada verde"},
        {"time": "PÓS", "name": "Pós-treino",
         "items": f"{round(p['arroz'] * 0.8)}g arroz branco + {p['frango']}g frango/carne magra + legumes"},
        {"time": "19H", "name": "Jantar",
         "items": f"{round(p['frango'] * 0.9)}g peixe ou frango + salada à vontade + {round(p['batata'] * 0.5)}g abobrinha"},
        {"time": "CEIA", "name": "Ceia",
         "items": f"{p['cottage']}g cottage ou clara de ovo + 1 fruta pequena"},
    ]


def _refeicoes_ganhar(p: dict) -> list:
    return [
        {"time": "07H", "name": "Café da manhã",
         "items": f"{p['ovos'] + 1} ovos mexidos + 2 fatias pão integral + 1 banana + 1 col. azeite"},
        {"time": "10H", "name": "Lanche reforçado",
         "items": f"{p['iogurte']}g iogurte grego + {p['pasta_am'] + 1} col. pasta de amendoim + 1 fruta {p['fruta']}"},
        {"time": "PRÉ", "name": "Pré-treino reforçado",
         "items": f"{p['arroz']}g arroz + {round(p['frango'] * 0.8)}g frango grelhado + salada"},
        {"time": "PÓS", "name": "Pós-treino",
         "items": f"{round(p['arroz'] * 1.2)}g arroz branco + {p['frango']}g carne/frango + legumes + azeite"},
        {"time": "19H", "name": "Jantar",
         "items": f"{round(p['frango'] * 0.9)}g proteína + {p['batata']}g batata-doce ou macarrão + salada"},
        {"time": "CEIA", "name": "Ceia",
         "items": f"{p['iogurte']}g iogurte grego + 30g granola + 1 banana"},
    ]


def _refeicoes_recomp(p: dict) -> list:
    return [
        {"time": "07H", "name": "Café da manhã",
         "items": f"{p['ovos']} ovos + 1 fatia pão integral + 1 fruta {p['fruta']} + café"},
        {"time": "10H", "name": "Lanche",
         "items": f"{p['iogurte']}g iogurte grego + {p['pasta_am']} col. pasta de amendoim + 1 maçã"},
        {"time": "PRÉ", "name": "Pré-treino",
         "items": f"{p['batata']}g batata-doce + {round(p['frango'] * 0.7)}g frango grelhado + café"},
        {"time": "PÓS", "name": "Pós-treino",
         "items": f"{p['arroz']}g arroz + {p['frango']}g frango ou carne + legumes refogados no azeite"},
        {"time": "19H", "name": "Jantar",
         "items": f"{round(p['frango'] * 0.9)}g proteína + {round(p['batata'] * 0.6)}g carboidrato + salada"},
        {"time": "CEIA", "name": "Ceia",
         "items": f"{p['cottage']}g cottage ou iogurte natural + 1 fruta pequena"},
    ]


TEMPLATES = {
    "perder": _refeicoes_perder,
    "ganhar": _refeicoes_ganhar,
    "recomp": _refeicoes_recomp,
}


def gerar_cardapio(peso: float, kcal: int, objetivo: str) -> list:
    """Retorna lista de refeições com horário, nome, itens e kcal estimadas."""
    porcoes   = _porcoes(peso)
    pcts      = DISTRIBUICAO.get(objetivo, DISTRIBUICAO["recomp"])
    refeicoes = TEMPLATES[objetivo](porcoes)

    for i, refeicao in enumerate(refeicoes):
        refeicao["kcal"] = round(kcal * pcts[i])

    return refeicoes
