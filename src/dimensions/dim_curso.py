"""
Dimensão Curso (Campus I - João Pessoa)
"""

import pandas as pd
from src.dimensions.dim_centro import criar_dim_centro

# Código IBGE de João Pessoa (Campus I)
CODIGO_MUNICIPIO_JP = 2507507


def identificar_centro_sigla(nome_curso: str) -> str:
    """
    Mapeia o nome do curso para a sigla do Centro Acadêmico do Campus I.
    """
    nome = str(nome_curso).upper()

    if any(k in nome for k in ["CIÊNCIAS SOCIAIS", "FILOSOFIA", "HISTÓRIA", "GEOGRAFIA", "LETRAS", "PSICOLOGIA", "TRADUÇÃO", "LIBRAS", "CIÊNCIAS DA RELIGIÃO"]):
        return "CCHLA"
    elif any(k in nome for k in ["ADMINISTRAÇÃO", "DIREITO", "CIÊNCIAS CONTÁBEIS", "ECONOMIA", "BIBLIOTECONOMIA", "ARQUIVONOMIA", "GESTÃO PÚBLICA", "TURISMO", "SECRETARIADO"]):
        return "CCSA"
    elif any(k in nome for k in ["ENGENHARIA", "ARQUITETURA"]):
        return "CT"
    elif any(k in nome for k in ["MEDICINA", "ENFERMAGEM", "FARMÁCIA", "ODONTOLOGIA", "FISIOTERAPIA", "EDUCAÇÃO FÍSICA", "NUTRIÇÃO", "FONOAUDIOLOGIA", "TERAPIA OCUPACIONAL", "BIOMEDICINA"]):
        return "CCS"
    elif any(k in nome for k in ["MATEMÁTICA", "FÍSICA", "QUÍMICA", "ESTATÍSTICA", "CIÊNCIAS BIOLÓGICAS", "GEOLOGIA", "OCEANOGRAFIA"]):
        return "CCEN"
    elif any(k in nome for k in ["COMPUTAÇÃO", "SISTEMAS DE INFORMAÇÃO", "MÍDIAS DIGITAIS"]):
        return "CI"
    elif any(k in nome for k in ["MÚSICA", "TEATRO", "CINEMA", "DANÇA", "ARTES VISUAIS", "COMUNICAÇÃO", "JORNALISMO", "RADIALISMO", "RELAÇÕES PÚBLICAS", "EXPRESSÃO GRÁFICA"]):
        return "CCTA"
    elif any(k in nome for k in ["PEDAGOGIA", "EDUCAÇÃO DO CAMPO", "EDUCAÇÃO INTERCULTURAL", "CIÊNCIAS DA EDUCAÇÃO"]):
        return "CE"
    elif "ENERGIA" in nome:
        return "CEAR"
    elif any(k in nome for k in ["SUCROALCOOLEIRA", "GASTRONOMIA", "TECNOLOGIA EM ALIMENTOS", "HOTELARIA"]):
        return "CTDR"
    elif "BIOTECNOLOGIA" in nome:
        return "CBIOTEC"
    else:
        return "OUTRO"


def criar_dim_curso(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a dimensão de cursos filtrada para o Campus I (João Pessoa), 
    mapeando o grau acadêmico, modalidade e atribuindo o ID_CENTRO.
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

    # 1. Filtro estrito: Apenas Campus I (João Pessoa) se a coluna existir no DF
    dim_curso = df.copy()
    if "CO_MUNICIPIO" in dim_curso.columns:
        dim_curso = dim_curso[dim_curso["CO_MUNICIPIO"] == CODIGO_MUNICIPIO_JP]

    # 2. Mapeamento de atributos do curso
    if "TP_GRAU_ACADEMICO" in dim_curso.columns:
        dim_curso["TP_GRAU_ACADEMICO"] = dim_curso["TP_GRAU_ACADEMICO"].map(grau)

    if "TP_MODALIDADE_ENSINO" in dim_curso.columns:
        dim_curso["TP_MODALIDADE_ENSINO"] = dim_curso["TP_MODALIDADE_ENSINO"].map(modalidade)

    # 3. Mapeamento da Sigla do Centro
    dim_curso["CENTRO"] = dim_curso["NO_CURSO"].apply(identificar_centro_sigla)

    # 4. Merge para resgatar o ID_CENTRO numérico
    dim_centro = criar_dim_centro()
    dim_curso = dim_curso.merge(dim_centro, on="CENTRO", how="left")

    # 5. Remoção de duplicatas
    dim_curso = dim_curso.drop_duplicates()

    # 6. Padronização dos nomes de colunas
    renomeio = {
        "CO_CURSO": "ID_CURSO",
        "NO_CURSO": "CURSO",
        "TP_GRAU_ACADEMICO": "GRAU_ACADEMICO",
        "TP_MODALIDADE_ENSINO": "MODALIDADE_ENSINO"
    }
    dim_curso = dim_curso.rename(columns=renomeio)

    # Seleção final de colunas
    cols_finais = [col for col in ["ID_CURSO", "CURSO", "GRAU_ACADEMICO", "MODALIDADE_ENSINO", "ID_CENTRO"] if col in dim_curso.columns]

    return dim_curso[cols_finais].sort_values(by="CURSO").reset_index(drop=True)