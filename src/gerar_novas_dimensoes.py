""" # foi gerado pelo Claude para produção
build_dimensions.py
--------------------
Gera os arquivos de dimensão processados (data/processed/) a partir dos
arquivos brutos do SEDAP+ (data/raw/) e do mapeamento curso -> centro
definido manualmente com base na estrutura oficial da UFPB.

Uso:
    python src/build_dimensions.py
"""

import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)

# Curso que não deve compor o escopo do Campus I: Ciências Agrárias EaD
# (113701) pertence administrativamente ao CCHSA / Campus III (Bananeiras),
# sem vínculo presencial com nenhum dos 13 centros do Campus I.
CURSO_FORA_ESCOPO = 113701


# ---------------------------------------------------------------------------
# dim_centro: nome completo + sigla dos 13 centros do Campus I
# ---------------------------------------------------------------------------
def build_dim_centro():
    nomes_centro = {
        "CCEN": "Centro de Ciências Exatas e da Natureza",
        "CCHLA": "Centro de Ciências Humanas, Letras e Artes",
        "CCTA": "Centro de Comunicação, Turismo e Artes",
        "CCS": "Centro de Ciências da Saúde",
        "CCSA": "Centro de Ciências Sociais Aplicadas",
        "CE": "Centro de Educação",
        "CT": "Centro de Tecnologia",
        "CCJ": "Centro de Ciências Jurídicas",
        "Cbiotec": "Centro de Biotecnologia",
        "CCM": "Centro de Ciências Médicas",
        "CI": "Centro de Informática",
        "CEAR": "Centro de Energias Alternativas e Renováveis",
        "CTDR": "Centro de Tecnologia e Desenvolvimento Regional",
    }

    dim_centro = pd.read_csv(RAW / "dim_centro_bruto.csv")
    dim_centro = dim_centro.rename(columns={"CENTRO": "SIGLA_CENTRO"})
    dim_centro["NOME_CENTRO"] = dim_centro["SIGLA_CENTRO"].map(nomes_centro)
    dim_centro = dim_centro[["ID_CENTRO", "NOME_CENTRO", "SIGLA_CENTRO"]]

    dim_centro.to_csv(
        PROCESSED / "dim_centro.csv", index=False, encoding="utf-8-sig"
    )
    return dim_centro


# ---------------------------------------------------------------------------
# dim_curso_completo / curso_centro: cursos do Campus I + centro associado
# ---------------------------------------------------------------------------
def build_dim_curso(dim_centro: pd.DataFrame):
    dim_curso = pd.read_csv(RAW / "dim_curso_campus1_bruto.csv")

    # Remove Ciências Agrárias EaD (113701) — fora do escopo do Campus I
    dim_curso = dim_curso[dim_curso["ID_CURSO"] != CURSO_FORA_ESCOPO].copy()

    sigla_to_id = dict(zip(dim_centro["SIGLA_CENTRO"], dim_centro["ID_CENTRO"]))

    # Mapeamento curso -> sigla do centro (validado com a estrutura oficial
    # da UFPB: Estatuto/Regimento, relatório CIA em Números 2024 e páginas
    # oficiais dos centros ci.ufpb.br / ccsa.ufpb.br)
    mapa = {
        13397: "CCSA", 13418: "CE", 13398: "CCJ", 13424: "CCM",
        107548: "CCHLA", 13395: "CCSA", 107549: "CCHLA", 13413: "CCHLA",
        13401: "CI", 13417: "CCHLA", 113621: "CCSA", 13396: "CCSA",
        1127164: "CI", 13430: "CT", 13415: "CCHLA", 44258: "CCS",
        13429: "CT", 1127907: "CTDR", 122924: "CE", 122926: "CE",
        13421: "CCS", 13394: "CCSA", 113609: "CEAR", 19562: "CCTA",
        1268219: "CCTA", 13427: "CT", 13422: "CCS", 13426: "CCS",
        13399: "CCEN", 13402: "CCEN", 1126958: "CCSA", 1189063: "CEAR",
        5001240: "CTDR", 122288: "CCS", 1127039: "CCSA", 113615: "CT",
        13425: "CCS", 13423: "CCS", 1110230: "CCHLA", 1125641: "CCHLA",
        116830: "CCHLA", 113604: "CT", 1503759: "CI", 1363988: "CCSA",
        113617: "CT", 1127165: "CTDR", 100220: "CCTA", 13428: "CT",
        1189062: "Cbiotec", 122934: "CT", 1123330: "CCS", 13404: "CCEN",
        13459: "CCHLA", 116826: "CE", 313399: "CCEN", 1399139: "CCS",
        122918: "CCS", 97039: "CCTA", 1268221: "CCTA", 13406: "CCEN",
        1162838: "CE", 19563: "CT", 1268257: "CCTA", 13431: "CT",
        122928: "CCHLA", 13400: "CCEN", 43454: "CCEN", 109948: "CCEN",
        313406: "CCEN", 26564: "CCTA", 107553: "CCHLA", 313400: "CCEN",
        13409: "CCHLA", 109954: "CCHLA", 122930: "CCHLA", 1126690: "CCHLA",
        1191007: "CCTA", 107438: "CCTA", 107440: "CCTA", 313404: "CCEN",
        313409: "CCHLA", 1261910: "CCHLA", 109950: "CE", 107456: "CCTA",
        1166771: "CCTA", 1261913: "CCHLA", 107552: "CCHLA", 1564470: "CCSA",
        407456: "CCTA", 313402: "CCEN", 1203263: "CCSA", 1162837: "CI",
        1203266: "CI",
    }

    faltando = set(dim_curso["ID_CURSO"]) - set(mapa.keys())
    if faltando:
        raise ValueError(f"Cursos sem mapeamento de centro: {sorted(faltando)}")

    dim_curso["ID_CENTRO"] = dim_curso["ID_CURSO"].map(mapa).map(sigla_to_id)
    dim_curso["ID_CENTRO"] = dim_curso["ID_CENTRO"].astype("Int64")

    dim_curso.to_csv(
        PROCESSED / "dim_curso_completo.csv", index=False, encoding="utf-8-sig"
    )

    curso_centro = dim_curso[["ID_CURSO", "CURSO", "ID_CENTRO"]]
    curso_centro.to_csv(
        PROCESSED / "curso_centro.csv", index=False, encoding="utf-8-sig"
    )
    return dim_curso


# ---------------------------------------------------------------------------
# dim_sexo
# ---------------------------------------------------------------------------
def build_dim_sexo():
    dim_sexo = pd.read_csv(RAW / "sexo.csv")

    sexo = {1: "Masculino", 2: "Feminino"}
    dim_sexo["DESCRICAO"] = dim_sexo["TP_SEXO"].map(sexo)
    dim_sexo = dim_sexo.rename(columns={"TP_SEXO": "ID_SEXO"})

    dim_sexo.to_csv(
        PROCESSED / "dim_sexo.csv", index=False, encoding="utf-8-sig"
    )
    return dim_sexo


# ---------------------------------------------------------------------------
# dim_raca
# ---------------------------------------------------------------------------
def build_dim_raca():
    dim_raca = pd.read_csv(RAW / "raca.csv")

    raca = {
        0: "Não declarada", 1: "Branca", 2: "Preta",
        3: "Parda", 4: "Amarela", 5: "Indígena",
    }
    dim_raca["DESCRICAO"] = dim_raca["TP_COR_RACA"].map(raca)
    dim_raca = dim_raca.rename(columns={"TP_COR_RACA": "ID_RACA"})

    dim_raca.to_csv(
        PROCESSED / "dim_raca.csv", index=False, encoding="utf-8-sig"
    )
    return dim_raca


# ---------------------------------------------------------------------------
# dim_turno (com o registro "Não informado")
# ---------------------------------------------------------------------------
def build_dim_turno():
    dim_turno = pd.read_csv(RAW / "dim_turno.csv")

    novo = pd.DataFrame({
        "ID_TURNO": [0],
        "TOTAL_ALUNOS": [0],
        "DESCRICAO": ["Não informado"],
    })
    dim_turno = pd.concat([novo, dim_turno], ignore_index=True)
    dim_turno = dim_turno.sort_values("ID_TURNO").reset_index(drop=True)

    dim_turno.to_csv(
        PROCESSED / "dim_turno.csv", index=False, encoding="utf-8-sig"
    )
    return dim_turno


if __name__ == "__main__":
    dim_centro = build_dim_centro()
    dim_curso = build_dim_curso(dim_centro)
    dim_sexo = build_dim_sexo()
    dim_raca = build_dim_raca()
    dim_turno = build_dim_turno()

    print("Dimensões geradas em data/processed/:")
    print(f"  dim_centro.csv         -> {len(dim_centro)} linhas")
    print(f"  dim_curso_completo.csv -> {len(dim_curso)} linhas")
    print(f"  curso_centro.csv       -> {len(dim_curso)} linhas")
    print(f"  dim_sexo.csv           -> {len(dim_sexo)} linhas")
    print(f"  dim_raca.csv           -> {len(dim_raca)} linhas")
    print(f"  dim_turno.csv          -> {len(dim_turno)} linhas")
