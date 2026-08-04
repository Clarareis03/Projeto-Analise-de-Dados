"""
Dimensão Curso
"""

from pathlib import Path
import pandas as pd


def criar_dim_curso(path_raw_cursos: Path, path_raw_sedap: Path) -> pd.DataFrame:
    """Cria e enriquece a dimensão Curso para a UFPB (Campus I - João Pessoa),

    cruzando dados do Censo INEP com o SEDAP.
    """
    # 1. Carrega SEDAP
    df_sedap = pd.read_csv(
        path_raw_sedap, sep=None, engine="python", encoding="utf-8-sig"
    )
    df_sedap.columns = df_sedap.columns.str.replace("\ufeff", "").str.strip()
    df_sedap["CO_CURSO"] = df_sedap["CO_CURSO"].astype(str).str.strip()

    # 2. Carrega Censo INEP
    df_censo = pd.read_csv(
        path_raw_cursos,
        sep=";",
        encoding="latin1",
        usecols=["CO_IES", "CO_CURSO", "NO_CURSO", "CO_MUNICIPIO", "NO_MUNICIPIO"],
        dtype=str,
    )

    # 3. Filtra Campus I (UFPB - João Pessoa: CO_IES=579 e CO_MUNICIPIO=2507507)
    cursos_campus_1 = df_censo[
        (df_censo["CO_IES"] == "579") & (df_censo["CO_MUNICIPIO"] == "2507507")
    ][["CO_CURSO", "NO_CURSO", "NO_MUNICIPIO"]].drop_duplicates()

    cursos_campus_1["NO_CURSO_COMPLETO"] = (
        cursos_campus_1["NO_CURSO"].str.strip().str.upper()
    )

    # 4. Merge para resgatar o nome completo do INEP
    df_final = pd.merge(
        df_sedap.drop(columns=["NO_CURSO"], errors="ignore"),
        cursos_campus_1[["CO_CURSO", "NO_CURSO_COMPLETO", "NO_MUNICIPIO"]],
        on="CO_CURSO",
        how="inner",
    ).rename(columns={"NO_CURSO_COMPLETO": "NO_CURSO"})

    # 5. Mapeamentos do INEP
    grau_map = {
        1: "Bacharelado",
        2: "Licenciatura",
        3: "Tecnológico",
        4: "Bacharelado e Licenciatura",
    }
    modalidade_map = {1: "Presencial", 2: "EaD"}

    df_final["TP_GRAU_ACADEMICO"] = pd.to_numeric(
        df_final["TP_GRAU_ACADEMICO"], errors="coerce"
    )
    df_final["TP_MODALIDADE_ENSINO"] = pd.to_numeric(
        df_final["TP_MODALIDADE_ENSINO"], errors="coerce"
    )

    df_final["DS_GRAU_ACADEMICO"] = (
        df_final["TP_GRAU_ACADEMICO"].map(grau_map).fillna("Não Informado")
    )
    df_final["DS_MODALIDADE_ENSINO"] = (
        df_final["TP_MODALIDADE_ENSINO"].map(modalidade_map).fillna("Não Informado")
    )

    # 6. Seleção e limpeza final
    dim_curso = (
        df_final[
            [
                "CO_CURSO",
                "NO_CURSO",
                "CO_CINE_ROTULO",
                "DS_GRAU_ACADEMICO",
                "DS_MODALIDADE_ENSINO",
                "NO_MUNICIPIO",
            ]
        ]
        .drop_duplicates(subset=["CO_CURSO"])
        .sort_values(by=["DS_MODALIDADE_ENSINO", "NO_CURSO"])
        .reset_index(drop=True)
    )

    return dim_curso