"""
Dimensão Sexo
"""

import pandas as pd


def criar_dim_sexo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a dimensão Sexo a partir dos dados extraídos do SEDAP.
    """

    sexo = {
        1: "Masculino",
        2: "Feminino"
    }

    dim_sexo = df.copy()

    dim_sexo["DESCRICAO"] = dim_sexo["TP_SEXO"].map(sexo)

    dim_sexo = dim_sexo.rename(columns={
        "TP_SEXO": "ID_SEXO"
    })

    dim_sexo = dim_sexo.sort_values("ID_SEXO").reset_index(drop=True)

    return dim_sexo