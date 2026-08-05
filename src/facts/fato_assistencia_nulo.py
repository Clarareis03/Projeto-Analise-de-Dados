"""
Tabela Fato - Assistência Estudantil (versão NULO)

Mesma construção de `fato_assistencia.py`, mas as colunas de auxílio
específico (IN_APOIO_ALIMENTACAO, IN_APOIO_MORADIA etc.) NÃO são
preenchidas com 0 — ficam como NaN quando IN_APOIO_SOCIAL = 0.

Comparar com a versão que preenche 0 (`fato_assistencia.py`) antes de
decidir qual vai pro modelo final. Ver discussão no notebook/relatório
sobre o tratamento desses nulos (são "não se aplica", não "não
respondido" — mas isso não significa que preencher com 0 seja
obrigatoriamente a melhor escolha de representação pro seu caso de uso).

Efeitos práticos de manter NaN aqui, pra ter em mente na comparação:
- As colunas de auxílio específico deixam de ser `int` e viram `float`
  (pandas não tem NaN em coluna inteira nativa, só em float ou no tipo
  nullable `Int64`). Isso pode exigir ajuste em quem for consumir esses
  dados a jusante (SQL/BI, groupby, etc.).
- `SUM()` continua funcionando igual (SQL ignora NULL em soma).
- `AVG()`/proporção calculada direto na coluna muda de significado: o
  denominador passa a ser só as linhas não-nulas (quem tem
  IN_APOIO_SOCIAL=1), não a população toda.
- No Power BI/Metabase, a coluna aparece com uma categoria "(Blank)" ao
  lado de 0/1 em tabelas e filtros.
- RECEBE_AUXILIO e IDPNA não mudam nada — os dois já são calculados a
  partir de IN_APOIO_SOCIAL/IN_RESERVA_VAGAS, não das colunas de
  auxílio específico.
"""

import pandas as pd


def criar_fato_assistencia_nulo(
    fato_raw: pd.DataFrame,
    dim_curso_campus1: pd.DataFrame,
    dim_curso_centro: pd.DataFrame,
    dim_grau: pd.DataFrame,
    dim_modalidade: pd.DataFrame,
) -> pd.DataFrame:
    """
    Constrói a tabela fato da assistência estudantil (schema 2023).

    Parameters
    ----------
    fato_raw : saída da consulta SQL "4.2 Construção Fato" (01_extracao_sedap.ipynb)
    dim_curso_campus1 : saída de `dim_curso_campus1.criar_dim_curso` (94 cursos, Campus I)
    dim_curso_centro : saída de `dim_curso_centro.criar_curso_centro`
    dim_grau : saída de `dim_grau.criar_dim_grau`
    dim_modalidade : saída de `dim_modalidade.criar_dim_modalidade`
    """

    fato = fato_raw.copy()

    # -------------------------------------------------
    # 1. Filtrar apenas cursos do Campus I (whitelist)
    # -------------------------------------------------
    # Antes: lista manual `cursos_fora` (blacklist). Agora: semi-join contra
    # a dimensão Curso já validada (INEP x SEDAP), sem lista hardcoded.
    cursos_campus1 = set(dim_curso_campus1["CO_CURSO"].astype(int))

    fato["CO_CURSO"] = fato["CO_CURSO"].astype(int)
    fato = fato[fato["CO_CURSO"].isin(cursos_campus1)].copy()

    # -------------------------------------------------
    # 2. Renomear chaves (mantendo CO_CURSO como está)
    # -------------------------------------------------
    fato = fato.rename(columns={
        "TP_SEXO": "ID_SEXO",
        "TP_COR_RACA": "ID_RACA",
        "TP_TURNO": "ID_TURNO",
    })

    # -------------------------------------------------
    # 3. Turno não informado
    # -------------------------------------------------
    fato["ID_TURNO"] = (
        fato["ID_TURNO"]
        .fillna(0)
        .astype(int)
    )

    # -------------------------------------------------
    # 4. Auxílios específicos
    # -------------------------------------------------
    # DIFERENÇA em relação a fato_assistencia.py: aqui NÃO preenchemos
    # com 0 — o nulo é preservado como está na extração bruta.
    colunas_auxilio = [
        "IN_APOIO_ALIMENTACAO",
        "IN_APOIO_MORADIA",
        "IN_APOIO_TRANSPORTE",
        "IN_APOIO_MATERIAL_DIDATICO",
        "IN_APOIO_BOLSA_PERMANENCIA",
        "IN_APOIO_BOLSA_TRABALHO",
    ]
    # (nenhum tratamento aplicado — mantido só pra documentar quais são)

    # -------------------------------------------------
    # 5. Recebe auxílio?
    # -------------------------------------------------
    fato["RECEBE_AUXILIO"] = (
        fato["IN_APOIO_SOCIAL"]
        .fillna(0)
        .astype(int)
    )

    # -------------------------------------------------
    # 6. Indicador de Demanda Potencial Não Atendida
    # -------------------------------------------------
    # Usa IN_RESERVA_VAGAS (agora disponível na extração 2023 do SEDAP+).
    # Antes usávamos IN_ACAO_AFIRMATIVA como substituta, porque
    # IN_RESERVA_VAGAS vinha vazia na extração 2024 — não é mais necessário.
    fato["IDPNA"] = (
        (fato["IN_RESERVA_VAGAS"] == 1) &
        (fato["RECEBE_AUXILIO"] == 0)
    ).astype(int)

    # -------------------------------------------------
    # 7. Quantidade de estudantes classificados
    # -------------------------------------------------
    fato["TOTAL_IDPNA"] = (
        fato["TOTAL_ALUNOS"] * fato["IDPNA"]
    )

    # -------------------------------------------------
    # 8. Acrescentar Centro (merge único, chave CO_CURSO)
    # -------------------------------------------------
    curso_centro_dedup = (
        dim_curso_centro[["CO_CURSO", "ID_CENTRO"]]
        .assign(CO_CURSO=lambda df: df["CO_CURSO"].astype(int))
        .drop_duplicates(subset="CO_CURSO")
    )

    fato = fato.merge(
        curso_centro_dedup,
        on="CO_CURSO",
        how="left",
        validate="m:1",
    )

    sem_centro = fato.loc[fato["ID_CENTRO"].isna(), "CO_CURSO"].unique()
    if len(sem_centro) > 0:
        raise ValueError(
            f"Cursos sem ID_CENTRO mapeado em dim_curso_centro: {sorted(sem_centro)}"
        )
    fato["ID_CENTRO"] = fato["ID_CENTRO"].astype(int)

    # -------------------------------------------------
    # 9. Acrescentar Grau e Modalidade (via texto -> ID)
    # -------------------------------------------------
    # Grau: dim_grau.py é DERIVADA da própria dim_curso_campus1 (extrai os
    # valores únicos de DS_GRAU_ACADEMICO), então o texto sempre bate por
    # construção — join direto por DESCRICAO é seguro aqui.
    #
    # Modalidade: dim_modalidade.py é uma dimensão ESTÁTICA independente,
    # com DESCRICAO = "Educação a Distância", enquanto dim_curso_campus1.py
    # gera DS_MODALIDADE_ENSINO = "EaD" — os textos NÃO batem (bug entre os
    # dois módulos, sinalizado separadamente). Pra não depender da redação
    # exata do texto, unimos por CD_MODALIDADE (PRES/EAD), normalizando a
    # DS_MODALIDADE_ENSINO pra esse código antes do merge.
    normaliza_modalidade = {"Presencial": "PRES", "EaD": "EAD"}

    curso_atributos = (
        dim_curso_campus1[["CO_CURSO", "DS_GRAU_ACADEMICO", "DS_MODALIDADE_ENSINO"]]
        .assign(CO_CURSO=lambda df: df["CO_CURSO"].astype(int))
        .assign(CD_MODALIDADE=lambda df: df["DS_MODALIDADE_ENSINO"].map(normaliza_modalidade))
        .merge(dim_grau, left_on="DS_GRAU_ACADEMICO", right_on="DESCRICAO", how="left")
        .merge(dim_modalidade[["ID_MODALIDADE", "CD_MODALIDADE"]], on="CD_MODALIDADE", how="left")
        [["CO_CURSO", "ID_GRAU", "ID_MODALIDADE"]]
        .drop_duplicates(subset="CO_CURSO")
    )

    fato = fato.merge(curso_atributos, on="CO_CURSO", how="left", validate="m:1")

    sem_grau_modalidade = fato.loc[
        fato["ID_GRAU"].isna() | fato["ID_MODALIDADE"].isna(), "CO_CURSO"
    ].unique()
    if len(sem_grau_modalidade) > 0:
        raise ValueError(
            f"Cursos sem Grau/Modalidade mapeado na fato: {sorted(sem_grau_modalidade)}"
        )
    fato["ID_GRAU"] = fato["ID_GRAU"].astype(int)
    fato["ID_MODALIDADE"] = fato["ID_MODALIDADE"].astype(int)

    # -------------------------------------------------
    # 10. Organizar colunas
    # -------------------------------------------------
    fato = fato[
        [
            "CO_CURSO",
            "ID_CENTRO",
            "ID_GRAU",
            "ID_MODALIDADE",
            "ID_SEXO",
            "ID_RACA",
            "ID_TURNO",
            "IN_RESERVA_VAGAS",
            "IN_APOIO_SOCIAL",
            "IN_APOIO_ALIMENTACAO",
            "IN_APOIO_MORADIA",
            "IN_APOIO_TRANSPORTE",
            "IN_APOIO_MATERIAL_DIDATICO",
            "IN_APOIO_BOLSA_PERMANENCIA",
            "IN_APOIO_BOLSA_TRABALHO",
            "TOTAL_ALUNOS",
            "RECEBE_AUXILIO",
            "IDPNA",
            "TOTAL_IDPNA",
        ]
    ]

    return fato
