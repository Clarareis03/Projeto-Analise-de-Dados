"""
Dimensão Modalidade de Ensino
"""

import pandas as pd


def criar_dim_modalidade() -> pd.DataFrame:
    return pd.DataFrame({
        "ID_MODALIDADE": [1, 2],
        "CD_MODALIDADE": ["PRES", "EAD"],
        "DESCRICAO": ["Presencial", "Educação a Distância"]
    })

    