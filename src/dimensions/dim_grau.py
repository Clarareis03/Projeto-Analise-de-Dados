"""
Dimensão Grau Acadêmico
"""

import pandas as pd


def criar_dim_grau(dim_curso: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a dimensão Grau Acadêmico a partir da dimensão Curso.
    """

    dim_grau = (
        dim_curso[["GRAU_ACADEMICO"]]
        .drop_duplicates()
        .sort_values("GRAU_ACADEMICO")
        .reset_index(drop=True)
    )

    dim_grau.insert(
        0,
        "ID_GRAU",
        range(1, len(dim_grau) + 1)
    )

    return dim_grau