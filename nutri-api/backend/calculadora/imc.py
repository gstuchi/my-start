"""
Cálculo e classificação do Índice de Massa Corporal (IMC).
"""


def calcular_imc(peso: float, altura: float) -> dict:
    """Retorna IMC, classificação, descrição personalizada e percentual para a barra."""
    altura_m = altura / 100
    imc = round(peso / (altura_m ** 2), 1)

    if imc < 18.5:
        return {
            "imc":      imc,
            "label":    "Abaixo do peso",
            "desc":     (f"Seu IMC de {imc} indica abaixo do peso ideal. "
                         "Priorize um superávit calórico com alimentos nutritivos e proteína adequada."),
            "pct":      18,
        }
    elif imc < 25:
        return {
            "imc":      imc,
            "label":    "Peso saudável",
            "desc":     (f"Ótimo! Seu IMC de {imc} está na faixa ideal. "
                         "Foque em manter a composição corporal e melhorar a performance nos treinos."),
            "pct":      52,
        }
    elif imc < 30:
        return {
            "imc":      imc,
            "label":    "Sobrepeso",
            "desc":     (f"Seu IMC de {imc} indica sobrepeso. "
                         "Reduzir a gordura corporal vai melhorar sua saúde e desempenho nos treinos."),
            "pct":      72,
        }
    else:
        return {
            "imc":      imc,
            "label":    "Obesidade",
            "desc":     (f"Seu IMC de {imc} merece atenção. "
                         "Um déficit calórico moderado combinado com treino resistido é o caminho mais seguro."),
            "pct":      90,
        }
