"""
Dimensão Grau Acadêmico
"""

import pandas as pd


def criar_dim_grau(dim_curso: pd.DataFrame) -> pd.DataFrame:
    """Cria a dimensão Grau Acadêmico a partir dos valores únicos da dimensão Curso."""

    dim_grau = (
        dim_curso[["DS_GRAU_ACADEMICO"]]
        .drop_duplicates()
        .dropna()
        .sort_values("DS_GRAU_ACADEMICO")
        .reset_index(drop=True)
    )

    # Renomeia a coluna para manter o padrão descritivo das dimensões
    dim_grau = dim_grau.rename(columns={"DS_GRAU_ACADEMICO": "DESCRICAO"})

    # Cria a chave primária sequencial
    dim_grau.insert(0, "ID_GRAU", range(1, len(dim_grau) + 1))

    return dim_grau