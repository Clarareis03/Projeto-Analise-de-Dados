# Dicionário de Dados - Assistência Estudantil UFPB

Este documento descreve a estrutura das Tabelas Dimensão e da Tabela Fato utilizadas no projeto de Análise do Perfil Discente e Demanda Potencial por Assistência Estudantil.

## 1. Tabelas Dimensão

### 1.1 Dimensão Centro (`dim_centro.csv`)
Tabela que armazena os Centros de Ensino da UFPB.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_CENTRO** | Inteiro | Código identificador único do(a) centro | `1` |
| **CENTRO** | Texto | Informa o dado de CENTRO | `CCEN` |

### 1.2 Dimensão Auxilio (`dim_auxilio.csv`)
Tabela que categoriza os tipos de auxílios e bolsas mapeados.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_AUXILIO** | Inteiro | Código identificador único do(a) auxilio | `1` |
| **TIPO_AUXILIO** | Texto | Informa o dado de TIPO_AUXILIO | `IN_APOIO_ALIMENTACAO` |
| **DESCRICAO** | Texto | Nome ou descrição referente a DESCRICAO | `Auxílio Alimentação / RU` |

### 1.3 Dimensão Curso (`dim_curso.csv`)
Tabela com as informações descritivas dos cursos de graduação.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_CURSO** | Inteiro | Código identificador único do(a) curso | `1160314` |
| **NO_CURSO** | Texto | Informa o dado de NO_CURSO | `Artes Visuais` |

### 1.4 Dimensão Curso Centro (`dim_curso_centro.csv`)
Tabela de relacionamento entre os cursos e os centros de ensino.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **CO_CURSO** | Inteiro | Informa o dado de CO_CURSO | `1203263` |
| **NO_CURSO** | Texto | Informa o dado de NO_CURSO | `ADMINISTRAÇÃO PÚBLICA` |
| **ID_CENTRO** | Inteiro | Código identificador único do(a) curso centro | `5` |

### 1.5 Dimensão Curso UFPB Campus 1 (`dim_curso_ufpb_campus_1.csv`)
Tabela com informações específicas dos cursos do Campus 1 da UFPB.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **CO_CURSO** | Inteiro | Informa o dado de CO_CURSO | `1203263` |
| **NO_CURSO** | Texto | Informa o dado de NO_CURSO | `ADMINISTRAÇÃO PÚBLICA` |
| **CO_CINE_ROTULO** | Texto | Informa o dado de CO_CINE_ROTULO | `0413A02` |
| **DS_GRAU_ACADEMICO** | Texto | Informa o dado de DS_GRAU_ACADEMICO | `Bacharelado` |
| **DS_MODALIDADE_ENSINO** | Texto | Informa o dado de DS_MODALIDADE_ENSINO | `EaD` |
| **NO_MUNICIPIO** | Texto | Informa o dado de NO_MUNICIPIO | `João Pessoa` |

### 1.6 Dimensão Grau (`dim_grau.csv`)
Tabela que descreve os graus acadêmicos (ex: Bacharelado, Licenciatura).

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_GRAU** | Inteiro | Código identificador único do(a) grau | `1` |
| **DESCRICAO** | Texto | Nome ou descrição referente a DESCRICAO | `Bacharelado` |

### 1.7 Dimensão Modalidade (`dim_modalidade.csv`)
Tabela que descreve as modalidades de ensino (ex: Presencial, EAD).

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_MODALIDADE** | Inteiro | Código identificador único do(a) modalidade | `1` |
| **CD_MODALIDADE** | Texto | Informa o dado de CD_MODALIDADE | `PRES` |
| **DESCRICAO** | Texto | Nome ou descrição referente a DESCRICAO | `Presencial` |

### 1.8 Dimensão Raca (`dim_raca.csv`)
Tabela com as categorias de raça/cor ou etnia declaradas.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_RACA** | Inteiro | Código identificador único do(a) raca | `1` |
| **DESCRICAO** | Texto | Nome ou descrição referente a DESCRICAO | `Branca` |

### 1.9 Dimensão Sexo (`dim_sexo.csv`)
Tabela com as categorias de sexo.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_SEXO** | Inteiro | Código identificador único do(a) sexo | `1` |
| **CD_SEXO** | Texto | Informa o dado de CD_SEXO | `M` |
| **DESCRICAO** | Texto | Nome ou descrição referente a DESCRICAO | `Masculino` |

### 1.10 Dimensão Turno (`dim_turno.csv`)
Tabela com os turnos de funcionamento dos cursos.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **ID_TURNO** | Inteiro | Código identificador único do(a) turno | `1` |
| **CD_TURNO** | Texto | Informa o dado de CD_TURNO | `MAT` |
| **DESCRICAO** | Texto | Nome ou descrição referente a DESCRICAO | `Matutino` |

## 2. Tabelas Fato

### 2.1 Fato Assistencia (`fato_assistencia.csv`)
Tabela fato contendo as métricas e relacionamentos das análises de assistência estudantil.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| **CO_CURSO** | Inteiro | Métrica ou indicador: CO_CURSO | `13394` |
| **ID_CENTRO** | Inteiro | Código identificador único do(a) fato assistencia | `5` |
| **ID_GRAU** | Inteiro | Código identificador único do(a) fato assistencia | `1` |
| **ID_MODALIDADE** | Inteiro | Código identificador único do(a) fato assistencia | `1` |
| **ID_SEXO** | Inteiro | Código identificador único do(a) fato assistencia | `1` |
| **ID_RACA** | Inteiro | Código identificador único do(a) fato assistencia | `3` |
| **ID_TURNO** | Inteiro | Código identificador único do(a) fato assistencia | `4` |
| **IN_RESERVA_VAGAS** | Inteiro | Métrica ou indicador: IN_RESERVA_VAGAS | `0` |
| **IN_APOIO_SOCIAL** | Inteiro | Métrica ou indicador: IN_APOIO_SOCIAL | `0` |
| **IN_APOIO_ALIMENTACAO** | Inteiro | Métrica ou indicador: IN_APOIO_ALIMENTACAO | `0` |
| **IN_APOIO_MORADIA** | Inteiro | Métrica ou indicador: IN_APOIO_MORADIA | `0` |
| **IN_APOIO_TRANSPORTE** | Inteiro | Métrica ou indicador: IN_APOIO_TRANSPORTE | `0` |
| **IN_APOIO_MATERIAL_DIDATICO** | Inteiro | Métrica ou indicador: IN_APOIO_MATERIAL_DIDATICO | `0` |
| **IN_APOIO_BOLSA_PERMANENCIA** | Inteiro | Métrica ou indicador: IN_APOIO_BOLSA_PERMANENCIA | `0` |
| **IN_APOIO_BOLSA_TRABALHO** | Inteiro | Métrica ou indicador: IN_APOIO_BOLSA_TRABALHO | `0` |
| **TOTAL_ALUNOS** | Inteiro | Métrica ou indicador: TOTAL_ALUNOS | `12` |
| **RECEBE_AUXILIO** | Inteiro | Métrica ou indicador: RECEBE_AUXILIO | `0` |
| **IDPNA** | Inteiro | Métrica ou indicador: IDPNA | `0` |
| **TOTAL_IDPNA** | Inteiro | Métrica ou indicador: TOTAL_IDPNA | `0` |
