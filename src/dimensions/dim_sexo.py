"""
Dimensão Sexo
"""
import pandas as pd

def criar_dim_sexo() -> pd.DataFrame:
    """Cria a dimensão estática de Sexo."""
    dados_sexo = {
        "ID_SEXO": [1, 2],
        "CD_SEXO": ["M", "F"],
        "DESCRICAO": ["Masculino", "Feminino"],
    }
    return pd.DataFrame(dados_sexo)