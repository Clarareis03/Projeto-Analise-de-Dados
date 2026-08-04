"""
Dimensão Raça/Cor
"""

import pandas as pd


def criar_dim_raca() -> pd.DataFrame:
    """Cria a dimensão estática de Raça/Cor padronizada pelo IBGE/INEP."""

    dados_raca = {
        "ID_RACA": [0, 1, 2, 3, 4, 5],
        "DESCRICAO": [
            "Não informado",
            "Branca",
            "Preta",
            "Parda",
            "Amarela",
            "Indígena",
        ],
    }

    dim_raca = pd.DataFrame(dados_raca)

    return dim_raca