"""
Dimensão Modalidade de Ensino
"""

import pandas as pd


def criar_dim_modalidade(dim_curso: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a dimensão Modalidade de Ensino a partir da dimensão Curso.
    """

    dim_modalidade = (
        dim_curso[["MODALIDADE_ENSINO"]]
        .drop_duplicates()
        .sort_values("MODALIDADE_ENSINO")
        .reset_index(drop=True)
    )

    dim_modalidade.insert(
        0,
        "ID_MODALIDADE",
        range(1, len(dim_modalidade) + 1)
    )

    return dim_modalidade