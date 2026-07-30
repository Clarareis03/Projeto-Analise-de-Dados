import pandas as pd

MAPA_CENTRO = {
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
    1189062: "CBIOTEC", 122934: "CT", 1123330: "CCS", 13404: "CCEN",
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


def criar_curso_centro(dim_curso: pd.DataFrame, dim_centro: pd.DataFrame) -> pd.DataFrame:
    sigla_to_id = dict(zip(dim_centro["CENTRO"], dim_centro["ID_CENTRO"]))

    # 1. Verifica cursos mapeados usando CO_CURSO (código MEC)
    col_busca = "CO_CURSO" if "CO_CURSO" in dim_curso.columns else "ID_CURSO"
    
    faltando = set(dim_curso[col_busca]) - set(MAPA_CENTRO.keys())
    if faltando:
        raise ValueError(f"Cursos sem mapeamento de centro: {sorted(faltando)}")

    # 2. Mantém CO_CURSO e ID_CURSO na tabela resultante
    colunas_preservar = [col for col in ["ID_CURSO", "CO_CURSO", "CURSO"] if col in dim_curso.columns]
    curso_centro = dim_curso[colunas_preservar].copy()

    # 3. Mapeia a partir de CO_CURSO para a sigla e depois para o ID_CENTRO
    curso_centro["ID_CENTRO"] = (
        dim_curso[col_busca].map(MAPA_CENTRO).map(sigla_to_id).astype("Int64")
    )

    return curso_centro
