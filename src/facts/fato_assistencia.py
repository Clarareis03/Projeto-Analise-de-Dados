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
    # ATENÇÃO: aqui RECEBE_AUXILIO é definido apenas por IN_APOIO_SOCIAL.
    # Na versão anterior (notebook), esse indicador era um OR entre TODOS
    # os auxílios específicos (colunas_auxilio). Se IN_APOIO_SOCIAL não for
    # o agregador oficial de todos os auxílios, confirme se não é o caso de
    # usar: fato[colunas_auxilio + ["IN_APOIO_SOCIAL"]].any(axis=1)
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
    # 8. Acrescentar Centro (chave normalizada + merge único)
    # -------------------------------------------------
    # BUG CORRIGIDO: antes havia DOIS merges com curso_centro. Como o
    # primeiro já criava a coluna ID_CENTRO, o segundo merge duplicava
    # a chave e o pandas renomeava para ID_CENTRO_x / ID_CENTRO_y — a
    # coluna "ID_CENTRO" simplesmente deixava de existir no resultado
    # final (daí o erro ao referenciá-la depois). Mantido só um merge.
    fato["ID_CURSO"] = fato["ID_CURSO"].astype(int)

    curso_centro_dedup = (
        curso_centro[["ID_CURSO", "ID_CENTRO"]]
        .assign(ID_CURSO=lambda df: df["ID_CURSO"].astype(int))
        .drop_duplicates(subset="ID_CURSO")
    )

    fato = fato.merge(
        curso_centro_dedup,
        on="ID_CURSO",
        how="left",
        validate="m:1"
    )

    # Validação: todo curso do Campus I precisa ter Centro mapeado.
    # Se isso disparar, há curso na fato que não está em dim_curso_centro.
    sem_centro = fato.loc[fato["ID_CENTRO"].isna(), "ID_CURSO"].unique()
    if len(sem_centro) > 0:
        raise ValueError(
            f"Cursos sem ID_CENTRO mapeado em dim_curso_centro: {sorted(sem_centro)}"
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

    return fato