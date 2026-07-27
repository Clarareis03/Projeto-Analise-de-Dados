"""
Dimensão Curso
"""

import pandas as pd


def criar_dim_curso(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a dimensão de cursos a partir da extração do SEDAP.
    """

    grau = {
        1: "Bacharelado",
        2: "Licenciatura",
        3: "Tecnológico"
    }

    modalidade = {
        1: "Presencial",
        2: "EaD"
    }

    dim_curso = df.copy()

    dim_curso["TP_GRAU_ACADEMICO"] = (
        dim_curso["TP_GRAU_ACADEMICO"]
        .map(grau)
    )

    dim_curso["TP_MODALIDADE_ENSINO"] = (
        dim_curso["TP_MODALIDADE_ENSINO"]
        .map(modalidade)
    )

    dim_curso = dim_curso.drop_duplicates()

    dim_curso = dim_curso.rename(columns={
        "CO_CURSO": "ID_CURSO",
        "NO_CURSO": "CURSO",
        "TP_GRAU_ACADEMICO": "GRAU_ACADEMICO",
        "TP_MODALIDADE_ENSINO": "MODALIDADE_ENSINO"
    })

    return dim_curso