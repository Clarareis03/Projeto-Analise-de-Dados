"""
Dimensão Curso-Centro
"""

import pandas as pd

MAPA_CENTRO = {
    # CCSA (ID 5)
    13394: "CCSA", 13395: "CCSA", 13396: "CCSA", 13397: "CCSA",
    113621: "CCSA", 1126958: "CCSA", 1127039: "CCSA", 1203263: "CCSA",
    1363988: "CCSA", 1564470: "CCSA",1125642: "CCSA",
    
    # CE (ID 6)
    13418: "CE", 109950: "CE", 116826: "CE", 122924: "CE",
    122926: "CE", 1162838: "CE",

    # CCJ (ID 8)
    13398: "CCJ",

    # CCM (ID 10)
    13424: "CCM",

    # CCHLA (ID 2)
    13409: "CCHLA", 13413: "CCHLA", 13415: "CCHLA", 13417: "CCHLA",
    107548: "CCHLA", 107549: "CCHLA", 107552: "CCHLA", 107553: "CCHLA",
    109954: "CCHLA", 116830: "CCHLA", 122928: "CCHLA", 122930: "CCHLA",
    1110230: "CCHLA", 1125641: "CCHLA", 1126690: "CCHLA",
    1261910: "CCHLA", 1261913: "CCHLA", 313409: "CCHLA", 13459: "CCHLA",

    # CI (ID 11)
    13401: "CI", 1127164: "CI", 1162837: "CI", 1203266: "CI",
    1503759: "CI",

    # CT (ID 7)
    19563: "CT", 113604: "CT", 113615: "CT", 113617: "CT",
    122934: "CT", 13427: "CT", 13428: "CT", 13429: "CT",
    13430: "CT", 13431: "CT",

    # CCS (ID 4)
    13421: "CCS", 13422: "CCS", 13423: "CCS", 13425: "CCS",
    13426: "CCS", 44258: "CCS", 122288: "CCS", 122918: "CCS",
    1123330: "CCS", 1399139: "CCS",

    # CTDR (ID 13)
    1127165: "CTDR", 1127907: "CTDR", 5001240: "CTDR",

    # CEAR (ID 12)
    113609: "CEAR", 1189063: "CEAR",

    # CCTA (ID 3)
    19562: "CCTA", 26564: "CCTA", 97039: "CCTA", 100220: "CCTA",
    107438: "CCTA", 107440: "CCTA", 107456: "CCTA", 407456: "CCTA",
    1166771: "CCTA", 1191007: "CCTA", 1268219: "CCTA", 1268221: "CCTA",
    1268257: "CCTA",

    # CCEN (ID 1)
    13399: "CCEN", 13400: "CCEN", 13402: "CCEN", 13404: "CCEN",
    13406: "CCEN", 43454: "CCEN", 109948: "CCEN", 313399: "CCEN",
    313400: "CCEN", 313402: "CCEN", 313404: "CCEN", 313406: "CCEN",

    # CBIOTEC (ID 9)
    1189062: "CBIOTEC",
}


def criar_curso_centro(dim_curso: pd.DataFrame, dim_centro: pd.DataFrame) -> pd.DataFrame:
    """Relaciona os cursos com seus respectivos centros de ensino (De/Para)."""

    sigla_to_id = dict(zip(dim_centro["CENTRO"], dim_centro["ID_CENTRO"]))

    col_busca = "CO_CURSO" if "CO_CURSO" in dim_curso.columns else "ID_CURSO"

    cursos_codigos = pd.to_numeric(dim_curso[col_busca], errors="coerce").astype("Int64")

    # Verifica quais cursos estão sem mapeamento
    faltando = set(cursos_codigos.dropna()) - set(MAPA_CENTRO.keys())
    if faltando:
        raise ValueError(f"Cursos sem mapeamento de centro: {sorted(list(faltando))}")

    colunas_preservar = [
        col for col in ["ID_CURSO", "CO_CURSO", "NO_CURSO", "CURSO"] if col in dim_curso.columns
    ]
    curso_centro = dim_curso[colunas_preservar].copy()

    # Mapeamento Sigla -> ID_CENTRO
    curso_centro["ID_CENTRO"] = (
        cursos_codigos.map(MAPA_CENTRO).map(sigla_to_id).astype("Int64")
    )

    return curso_centro