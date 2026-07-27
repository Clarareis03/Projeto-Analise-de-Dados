"""
Dimensão Raça/Cor
"""

import pandas as pd


def criar_dim_raca(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a dimensão de raça/cor a partir dos dados extraídos do SEDAP.
    """

    raca = {
        0: "Não declarada",
        1: "Branca",
        2: "Preta",
        3: "Parda",
        4: "Amarela",
        5: "Indígena"
    }

    dim_raca = df.copy()

    dim_raca["DESCRICAO"] = dim_raca["TP_COR_RACA"].map(raca)

    dim_raca = dim_raca.rename(
        columns={
            "TP_COR_RACA": "ID_RACA"
        }
    )

    dim_raca = (
        dim_raca
        .sort_values("ID_RACA")
        .reset_index(drop=True)
    )

    return dim_raca