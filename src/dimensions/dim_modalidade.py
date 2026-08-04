"""
Dimensão Modalidade de Ensino
"""

import pandas as pd


def criar_dim_modalidade() -> pd.DataFrame:
    return pd.DataFrame({
        "ID_MODALIDADE": [1, 2],
        "CD_MODALIDADE": ["PRES", "EAD"],
        "DESCRICAO": ["Presencial", "Educação a Distância"]
    })

    # Renomeia para o padrão de atributo descritivo
    dim_modalidade = dim_modalidade.rename(columns={"CD_MODALIDADE": "DESCRICAO"})

    # Cria a chave primária sequencial
    dim_modalidade.insert(0, "ID_MODALIDADE", range(1, len(dim_modalidade) + 1))

    return dim_modalidade