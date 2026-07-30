"""
Tabela Fato - Assistência Estudantil

Constrói a tabela fato utilizada no modelo estrela,
a partir da extração agregada do SEDAP+.
"""

import pandas as pd


def criar_fato_assistencia(
    fato: pd.DataFrame,
    curso_centro: pd.DataFrame
) -> pd.DataFrame:
    """
    Constrói a tabela fato da assistência estudantil.
    """

    # -------------------------------------------------
    # 1. Filtrar apenas cursos do Campus I
    # -------------------------------------------------
    cursos_fora = [
        13403, 13454, 13455, 13457, 80589, 97767,
        98976, 98980, 98982, 98984, 99045,
        107348, 107352, 107356, 107360,
        109626, 113709, 397767, 1161324,
        1167933, 1440696, 5000897,
        5000898, 113699, 1110415,
        113701
    ]

    fato = fato[
        ~fato["CO_CURSO"].isin(cursos_fora)
    ].copy()

    # -------------------------------------------------
    # 2. Renomear chaves (CO_CURSO vira ID_CURSO)
    # -------------------------------------------------
    fato = fato.rename(columns={
        "CO_CURSO": "ID_CURSO",
        "TP_SEXO": "ID_SEXO",
        "TP_COR_RACA": "ID_RACA",
        "TP_TURNO": "ID_TURNO"
    })

    # -------------------------------------------------
    # 3. Turno não informado
    # -------------------------------------------------
    fato["ID_TURNO"] = (
        fato["ID_TURNO"]
        .fillna(0)
        .astype(int)
    )

    # -------------------------------------------------
    # 4. Auxílios específicos
    # -------------------------------------------------
    colunas_auxilio = [
        "IN_APOIO_ALIMENTACAO",
        "IN_APOIO_MORADIA",
        "IN_APOIO_TRANSPORTE",
        "IN_APOIO_MATERIAL_DIDATICO",
        "IN_APOIO_BOLSA_PERMANENCIA",
        "IN_APOIO_BOLSA_TRABALHO"
    ]

    fato[colunas_auxilio] = (
        fato[colunas_auxilio]
        .fillna(0)
        .astype(int)
    )

    # -------------------------------------------------
    # 5. Recebe auxílio?
    # -------------------------------------------------
    fato["RECEBE_AUXILIO"] = (
        fato["IN_APOIO_SOCIAL"]
        .fillna(0)
        .astype(int)
    )

    # -------------------------------------------------
    # 6. Indicador de Demanda Potencial Não Atendida
    # -------------------------------------------------
    fato["IDPNA"] = (
        (fato["IN_ACAO_AFIRMATIVA"] == 1) &
        (fato["RECEBE_AUXILIO"] == 0)
    ).astype(int)

    # -------------------------------------------------
    # 7. Quantidade de estudantes classificados
    # -------------------------------------------------
    fato["TOTAL_IDPNA"] = (
        fato["TOTAL_ALUNOS"] * fato["IDPNA"]
    )

    # -------------------------------------------------
    # 8. Acrescentar Centro
    # -------------------------------------------------
    fato = fato.merge(
        curso_centro[["ID_CURSO", "ID_CENTRO"]],
        on="ID_CURSO",
        how="left"
    )

    # -------------------------------------------------
    # 9. Organizar colunas
    # -------------------------------------------------
    fato = fato[
        [
            "ID_CURSO",
            "ID_CENTRO",
            "ID_SEXO",
            "ID_RACA",
            "ID_TURNO",
            "IN_ACAO_AFIRMATIVA",
            "IN_APOIO_SOCIAL",
            "IN_APOIO_ALIMENTACAO",
            "IN_APOIO_MORADIA",
            "IN_APOIO_TRANSPORTE",
            "IN_APOIO_MATERIAL_DIDATICO",
            "IN_APOIO_BOLSA_PERMANENCIA",
            "IN_APOIO_BOLSA_TRABALHO",
            "TOTAL_ALUNOS",
            "RECEBE_AUXILIO",
            "IDPNA",
            "TOTAL_IDPNA"
        ]
    ]
    # -------------------------------------------------
    # 8. Acrescentar Centro (Garantindo o mesmo tipo para a chave)
    # -------------------------------------------------
    fato["ID_CURSO"] = fato["ID_CURSO"].astype(int)
    curso_centro_copy = curso_centro.copy()
    curso_centro_copy["ID_CURSO"] = curso_centro_copy["ID_CURSO"].astype(int)

    fato = fato.merge(
        curso_centro_copy[["ID_CURSO", "ID_CENTRO"]],
        on="ID_CURSO",
        how="left"
    )

    return fato