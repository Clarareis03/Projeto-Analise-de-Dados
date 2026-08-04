"""
Dimensão Turno
"""

import pandas as pd


def criar_dim_turno() -> pd.DataFrame:
    """Cria a dimensão estática de Turno padronizada pelo INEP (incluindo 0 para EaD/Não informado)."""

    dados_turno = {
        "ID_TURNO": [0, 1, 2, 3, 4],
        "CD_TURNO": ["NI", "MAT", "VESP", "NOT", "INT"],
        "DESCRICAO": [
            "Não informado",
            "Matutino",
            "Vespertino",
            "Noturno",
            "Integral",
        ],
    }

    dim_turno = pd.DataFrame(dados_turno)

    return dim_turno