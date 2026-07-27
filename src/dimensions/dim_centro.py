"""
Dimensão Centro
"""

import pandas as pd


def criar_dim_centro() -> pd.DataFrame:
    """
    Cria a dimensão dos Centros Acadêmicos da UFPB Campus I.
    """

    dados_centro = {
        "ID_CENTRO": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        "CENTRO": [
            "CCEN",
            "CCHLA",
            "CCTA",
            "CCS",
            "CCSA",
            "CE",
            "CT",
            "CCJ",
            "CBIOTEC",
            "CCM",
            "CI",
            "CEAR",
            "CTDR"
        ]
    }

    dim_centro = pd.DataFrame(dados_centro)

    return dim_centro