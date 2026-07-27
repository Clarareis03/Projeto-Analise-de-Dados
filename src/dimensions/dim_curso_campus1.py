"""
Dimensão Curso - Campus I
"""

import pandas as pd


def criar_dim_curso_campus1(dim_curso: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra a dimensão de cursos, mantendo apenas os cursos
    pertencentes ao Campus I da UFPB.
    """

    cursos_fora = [
        13403, 13454, 13455, 13457,
        80589, 97767, 98976, 98980,
        98982, 98984, 99045,
        107348, 107352, 107356, 107360,
        109626, 1110415, 113699, 113701,
        113709, 1161324, 1167933,
        1440696, 397767,
        5000897, 5000898
    ]

    dim_curso_campus1 = (
        dim_curso[
            ~dim_curso["ID_CURSO"].isin(cursos_fora)
        ]
        .copy()
        .sort_values("ID_CURSO")
        .reset_index(drop=True)
    )

    return dim_curso_campus1