# Dicionário de Dados - Assistência Estudantil UFPB

Este documento descreve a estrutura das Tabelas Dimensão e da Tabela Fato utilizadas no projeto de Análise do Perfil Discente e Demanda Potencial por Assistência Estudantil.

## 1. Tabelas Dimensão

### 1.1 Dimensão Centro (`dim_centro.csv`)
Tabela que armazena os Centros de Ensino da UFPB.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_CENTRO** | Inteiro | Código identificador único do centro de ensino | `2` |
| **CENTRO** | Texto | Sigla do centro de ensino | `CCHLA` |

### 1.2 Dimensão Auxílio (`dim_auxilio.csv`)
Tabela que categoriza os tipos de auxílios e bolsas mapeados.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_AUXILIO** | Inteiro | Código identificador único do auxílio | `1` |
| **AUXILIO** | Texto | Nome descritivo do auxílio | `Auxílio Alimentação / RU` |
| **TIPO_AUXILIO** | Texto | Nome da variável original correspondente nos microdados do INEP | `IN_APOIO_ALIMENTACAO` |

### 1.3 Dimensão Curso (`dim_curso.csv`)
Tabela com as informações descritivas dos cursos de graduação.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_CURSO** | Inteiro | Código oficial do curso no INEP | `13418` |
| **CURSO** | Texto | Nome completo do curso de graduação | `PEDAGOGIA` |
| **CO_CINE_ROTULO** | Texto | Código de classificação do curso no padrão CINE | `0113P01` |
| **GRAU_ACADEMICO** | Texto | Tipo de grau conferido | `Licenciatura` |
| **MODALIDADE_ENSINO** | Texto | Modalidade do curso | `Presencial` |
| **TOTAL_ALUNOS** | Inteiro | Quantidade total de alunos matriculados no curso | `1382` |

---
*Nota: A documentação da Tabela Fato será adicionada a este dicionário assim que sua construção for finalizada.*