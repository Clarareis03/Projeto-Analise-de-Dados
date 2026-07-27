"""
Dimensão Turno
"""

import pandas as pd


def criar_dim_turno(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a dimensão Turno, adicionando o registro
    'Não informado' para cursos EaD ou registros sem turno.
    """

    dim_turno = df.copy()

    # Registro adicional
    novo = pd.DataFrame({
        "ID_TURNO": [0],
        "TOTAL_ALUNOS": [0],
        "DESCRICAO": ["Não informado"]
    })

    dim_turno = pd.concat(
        [novo, dim_turno],
        ignore_index=True
    )

    dim_turno = (
        dim_turno
        .drop_duplicates(subset="ID_TURNO")
        .sort_values("ID_TURNO")
        .reset_index(drop=True)
    )

    return dim_turno