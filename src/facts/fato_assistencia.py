"""
Tabela Fato Assistência Estudantil
"""

from pathlib import Path
import pandas as pd


def criar_fato_assistencia(
    path_raw_sedap: Path,
    dim_curso: pd.DataFrame,
    dim_sexo: pd.DataFrame = None,
    dim_raca: pd.DataFrame = None,
    dim_turno: pd.DataFrame = None,
) -> pd.DataFrame:
    """Cria a Fato Assistência vinculada às Dimensões e filtrada estritamente para o Campus I."""
    # 1. Carrega dados brutos do SEDAP
    df_sedap = pd.read_csv(
        path_raw_sedap, sep=None, engine="python", encoding="utf-8-sig"
    )
    df_sedap.columns = df_sedap.columns.str.replace("\ufeff", "").str.strip()

    # 2. Tratamento para ligação com dim_curso (prioriza NO_CURSO/DS_CURSO se CO_CURSO for incompatível)
    dim_curso_clean = dim_curso.copy()

    # Tenta relacionar pelo Nome do Curso
    col_nome_sedap = next(
        (c for c in ["NO_CURSO", "DS_CURSO", "NOME_CURSO"] if c in df_sedap.columns),
        None,
    )
    col_nome_dim = next(
        (c for c in ["NO_CURSO", "DS_CURSO", "NOME_CURSO"] if c in dim_curso_clean.columns),
        None,
    )

    if col_nome_sedap and col_nome_dim:
        # Padroniza texto (maiúsculo sem espaços extras)
        df_sedap["NOME_CURSO_NORM"] = (
            df_sedap[col_nome_sedap].astype(str).str.strip().str.upper()
        )
        dim_curso_clean["NOME_CURSO_NORM"] = (
            dim_curso_clean[col_nome_dim].astype(str).str.strip().str.upper()
        )

        # Merge para obter a FK verdadeira da dim_curso (CO_CURSO do INEP)
        df_filtered = pd.merge(
            df_sedap,
            dim_curso_clean[["NOME_CURSO_NORM", "CO_CURSO"]].drop_duplicates(),
            on="NOME_CURSO_NORM",
            how="inner",
            suffixes=("_SEDAP", ""),
        )
    else:
        # Se não houver nome de curso no SEDAP, filtra apenas pelos CO_CURSO conhecidos
        df_sedap["CO_CURSO_STR"] = (
            df_sedap["CO_CURSO"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
        )
        dim_curso_clean["CO_CURSO_STR"] = (
            dim_curso_clean["CO_CURSO"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
        )

        df_filtered = pd.merge(
            df_sedap,
            dim_curso_clean[["CO_CURSO_STR"]].drop_duplicates(),
            left_on="CO_CURSO_STR",
            right_on="CO_CURSO_STR",
            how="inner",
        )

    # 3. Identifica e despivota (Melt) as colunas de auxílio
    cols_apoio = [col for col in df_filtered.columns if col.startswith("IN_APOIO_")]

    id_vars = [
        col
        for col in [
            "CO_CURSO",
            "TP_SEXO",
            "TP_COR_RACA",
            "TP_TURNO",
            "IN_ACAO_AFIRMATIVA",
            "TOTAL_ALUNOS",
        ]
        if col in df_filtered.columns
    ]

    fato_melt = df_filtered.melt(
        id_vars=id_vars,
        value_vars=cols_apoio,
        var_name="DS_AUXILIO",
        value_name="IN_RECEBEU",
    )

    # 4. Filtra apenas concessões ativas (= 1)
    fato_melt["IN_RECEBEU_NUM"] = pd.to_numeric(
        fato_melt["IN_RECEBEU"], errors="coerce"
    )
    fato = fato_melt[fato_melt["IN_RECEBEU_NUM"] == 1].copy()

    # 5. Mapeamento das Chaves Estrangeiras (FKs)
    auxilio_map = {
        nome: idx + 1
        for idx, nome in enumerate(sorted(fato["DS_AUXILIO"].unique()))
    }
    fato["ID_AUXILIO"] = fato["DS_AUXILIO"].map(auxilio_map)

    fato["ID_SEXO"] = fato["TP_SEXO"]
    fato["ID_RACA"] = fato["TP_COR_RACA"]
    fato["ID_TURNO"] = fato["TP_TURNO"]

    # 6. Métrica Quantitativa
    fato["QT_BENEFICIARIOS"] = fato.get("TOTAL_ALUNOS", 1)

    cols_final = [
        "CO_CURSO",
        "ID_SEXO",
        "ID_RACA",
        "ID_TURNO",
        "IN_ACAO_AFIRMATIVA",
        "ID_AUXILIO",
        "QT_BENEFICIARIOS",
    ]

    cols_existentes = [c for c in cols_final if c in fato.columns]
    return fato[cols_existentes].reset_index(drop=True)