import pandas as pd

dados_auxilio = {
    'codigo_auxilio': [1, 2, 3, 4, 5, 6],
    'descricao': [
        'Auxílio Alimentação / RU', 
        'Auxílio Moradia', 
        'Auxílio Transporte', 
        'Auxílio Material Didático', 
        'Bolsa Permanência',
        'Bolsa Trabalho'
    ],
    'tipo_auxilio': [
        'IN_APOIO_ALIMENTACAO', 
        'IN_APOIO_MORADIA', 
        'IN_APOIO_TRANSPORTE', 
        'IN_APOIO_MATERIAL_DIDATICO', 
        'IN_APOIO_BOLSA_PERMANENCIA',
        'IN_APOIO_BOLSA_TRABALHO'
    ]
}

df_auxilio = pd.DataFrame(dados_auxilio)

df_auxilio.to_csv('data/processed/Dimensões/dim_auxilio.csv', index=False, encoding='utf-8')