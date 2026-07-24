import pandas as pd

dados_centro = {
    'ID_Centro': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    'Centro': [
        'CCEN', 'CCHLA', 'CCTA', 'CCS', 'CCSA', 
        'CE', 'CT', 'CCJ', 'Cbiotec', 'CCM', 
        'CI', 'CEAR', 'CTDR'
    ]
}

df_centro = pd.DataFrame(dados_centro)

df_centro.to_csv('data/processed/Dimensões/dim_centro.csv', index=False, encoding='utf-8')