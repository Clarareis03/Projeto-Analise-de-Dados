"""
Dimensão Auxílio
"""

import pandas as pd


def criar_dim_auxilio() -> pd.DataFrame:
    """
    Cria a dimensão dos tipos de auxílio estudantil.
    """

    dados_auxilio = {
        "ID_AUXILIO": [1, 2, 3, 4, 5, 6],
        "AUXILIO": [
            "Auxílio Alimentação / RU",
            "Auxílio Moradia",
            "Auxílio Transporte",
            "Auxílio Material Didático",
            "Bolsa Permanência",
            "Bolsa Trabalho"
        ],
        "TIPO_AUXILIO": [
            "IN_APOIO_ALIMENTACAO",
            "IN_APOIO_MORADIA",
            "IN_APOIO_TRANSPORTE",
            "IN_APOIO_MATERIAL_DIDATICO",
            "IN_APOIO_BOLSA_PERMANENCIA",
            "IN_APOIO_BOLSA_TRABALHO"
        ]
    }

    dim_auxilio = pd.DataFrame(dados_auxilio)

    return dim_auxilio