# app.py
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="Dashboard Assistência Estudantil — UFPB Campus I",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Mapeamento de Caminhos Relativos
BASE_DIR = Path(__file__).parent.resolve() if "__file__" in locals() else Path.cwd()
PATH_FATO = BASE_DIR / "data" / "processed" / "Fato" / "fato_assistencia.csv"
PATH_DIM_CURSO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_curso_ufpb_campus_1.csv"
PATH_DIM_CENTRO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_centro.csv"
PATH_DIM_RACA = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_raca.csv"
PATH_DIM_SEXO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_sexo.csv"
PATH_DIM_TURNO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_turno.csv"


# 3. Carregamento e Tratamento de Dados (Com Cache)
@st.cache_data
def load_data():
    if not PATH_FATO.exists():
        st.error(f"Arquivo de fatos não encontrado em: {PATH_FATO}")
        st.stop()

    df_fato = pd.read_csv(PATH_FATO, sep=";")

    # Cruzamento com Dimensões
    if PATH_DIM_CURSO.exists():
        df_c = pd.read_csv(PATH_DIM_CURSO, sep=";")
        df_fato = df_fato.merge(df_c[["CO_CURSO", "NO_CURSO"]], on="CO_CURSO", how="left")
        df_fato.rename(columns={"NO_CURSO": "CURSO"}, inplace=True)

    if PATH_DIM_CENTRO.exists():
        df_cent = pd.read_csv(PATH_DIM_CENTRO, sep=";")
        df_fato = df_fato.merge(df_cent, on="ID_CENTRO", how="left")

    if PATH_DIM_RACA.exists():
        df_r = pd.read_csv(PATH_DIM_RACA, sep=";").rename(columns={"DESCRICAO": "RACA_DESCRICAO"})
        df_fato = df_fato.merge(df_r[["ID_RACA", "RACA_DESCRICAO"]], on="ID_RACA", how="left")

    if PATH_DIM_SEXO.exists():
        df_s = pd.read_csv(PATH_DIM_SEXO, sep=";").rename(columns={"DESCRICAO": "SEXO_DESCRICAO"})
        df_fato = df_fato.merge(df_s[["ID_SEXO", "SEXO_DESCRICAO"]], on="ID_SEXO", how="left")

    if PATH_DIM_TURNO.exists():
        df_t = pd.read_csv(PATH_DIM_TURNO, sep=";").rename(columns={"DESCRICAO": "TURNO_DESCRICAO"})
        df_fato = df_fato.merge(df_t[["ID_TURNO", "TURNO_DESCRICAO"]], on="ID_TURNO", how="left")

    # Mapeamento do Grupo de Turno (Diurno x Noturno)
    mapa_turno = {
        "Matutino": "Diurno",
        "Vespertino": "Diurno",
        "Integral": "Diurno",
        "Noturno": "Noturno",
    }
    df_fato["GRUPO_TURNO"] = df_fato["TURNO_DESCRICAO"].map(mapa_turno).fillna("Não informado")

    return df_fato


df_raw = load_data()

# 4. Barra Lateral (Filtros Interativos)
st.sidebar.title("Filtros de Análise")
st.sidebar.markdown("---")

centros_disponiveis = ["Todos"] + sorted(list(df_raw["CENTRO"].dropna().unique()))
centro_sel = st.sidebar.selectbox("Centro de Ensino:", centros_disponiveis)

turnos_disponiveis = ["Todos"] + sorted(list(df_raw["GRUPO_TURNO"].unique()))
turno_sel = st.sidebar.selectbox("Grupo de Turno:", turnos_disponiveis)

# Aplicar Filtros Dinâmicos
df_filtered = df_raw.copy()

if centro_sel != "Todos":
    df_filtered = df_filtered[df_filtered["CENTRO"] == centro_sel]

if turno_sel != "Todos":
    df_filtered = df_filtered[df_filtered["GRUPO_TURNO"] == turno_sel]

# Cursos dinâmicos com base nos centros/turnos selecionados
cursos_disponiveis = ["Todos"] + sorted(list(df_filtered["CURSO"].dropna().unique()))
curso_sel = st.sidebar.selectbox("Curso de Graduação:", cursos_disponiveis)

if curso_sel != "Todos":
    df_filtered = df_filtered[df_filtered["CURSO"] == curso_sel]

st.sidebar.markdown("---")
st.sidebar.info(
    "**Fonte de Dados:** SEDAP+ (2023)[cite: 4]\n\n"
    "**IDPNA:** Estudantes cotistas sem apoio social (`IN_RESERVA_VAGAS=1` e `RECEBE_AUXILIO=0`)[cite: 4, 5]."
)

# 5. Título do Dashboard
st.title("📊 Painel de Assistência Estudantil e Vulnerabilidade")
st.subheader("Universidade Federal da Paraíba — Campus I (Ano-base 2023)")
st.markdown("---")

# 6. Cálculo dos KPIs Globais (Painel 1)
total_alunos = df_filtered["TOTAL_ALUNOS"].sum()
total_cotistas = df_filtered.loc[df_filtered["IN_RESERVA_VAGAS"] == 1, "TOTAL_ALUNOS"].sum()
total_assistidos = df_filtered.loc[df_filtered["RECEBE_AUXILIO"] == 1, "TOTAL_ALUNOS"].sum()
total_idpna = df_filtered["TOTAL_IDPNA"].sum()

pct_cotistas = (total_cotistas / total_alunos * 100) if total_alunos > 0 else 0
pct_cobertura = (total_assistidos / total_cotistas * 100) if total_cotistas > 0 else 0

# Exibição dos KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Alunos", f"{total_alunos:,.0f}")
col2.metric("Estudantes Cotistas", f"{total_cotistas:,.0f}", f"{pct_cotistas:.1f}% do total")
col3.metric("Cobertura PRAPE (Cotistas)", f"{pct_cobertura:.1f}%", f"{total_assistidos:,.0f} assistidos")
col4.metric("Demanda Não Atendida (IDPNA)", f"{total_idpna:,.0f}", delta_color="inverse")

st.markdown("---")

# 7. Abas da Aplicação
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Cobertura & Demandas por Curso",
    "🌓 Desigualdade por Turno (Diurno x Noturno)",
    "🧬 Equidade e Perfil Demográfico",
    "🏢 Visão por Centro de Ensino",
])

# -----------------------------------------------------------------------------
# TAB 1: Cobertura & Demandas por Curso (Perguntas 1 e 3)
# -----------------------------------------------------------------------------
with tab1:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### Cobertura de Apoio Social entre Cotistas")
        cotistas_df = df_filtered[df_filtered["IN_RESERVA_VAGAS"] == 1]
        sem_apoio = cotistas_df.loc[cotistas_df["RECEBE_AUXILIO"] == 0, "TOTAL_ALUNOS"].sum()
        com_apoio = cotistas_df.loc[cotistas_df["RECEBE_AUXILIO"] == 1, "TOTAL_ALUNOS"].sum()

        fig_pie = px.pie(
            names=["Sem Apoio Social (IDPNA)", "Com Apoio Social"],
            values=[sem_apoio, com_apoio],
            color_discrete_sequence=["#ef553b", "#636efa"],
            hole=0.4,
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.markdown("### Top 10 Cursos — Volume Absoluto de IDPNA")
        df_cursos_idpna = (
            df_filtered.groupby("CURSO")["TOTAL_IDPNA"]
            .sum()
            .reset_index()
            .sort_values("TOTAL_IDPNA", ascending=False)
            .head(10)
        )

        fig_bar_top = px.bar(
            df_cursos_idpna,
            x="TOTAL_IDPNA",
            y="CURSO",
            orientation="h",
            text="TOTAL_IDPNA",
            color="TOTAL_IDPNA",
            color_continuous_scale="Reds",
        )
        fig_bar_top.update_layout(
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
            margin=dict(t=30, b=0, l=0, r=0),
            xaxis_title="Estudantes em IDPNA",
            yaxis_title="",
        )
        st.plotly_chart(fig_bar_top, use_container_width=True)

    st.markdown("---")
    st.markdown("### Matriz de Demanda Reprimida (Cotistas x Apoio Social por Curso)")

    matriz_curso = (
        df_filtered.groupby(["CO_CURSO", "CURSO", "CENTRO"])
        .apply(
            lambda x: pd.Series({
                "TOTAL_ALUNOS": x["TOTAL_ALUNOS"].sum(),
                "TOTAL_COTISTAS": x.loc[x["IN_RESERVA_VAGAS"] == 1, "TOTAL_ALUNOS"].sum(),
                "TOTAL_COM_APOIO": x.loc[x["RECEBE_AUXILIO"] == 1, "TOTAL_ALUNOS"].sum(),
                "TOTAL_IDPNA": x["TOTAL_IDPNA"].sum(),
            }),
            include_groups=False,
        )
        .reset_index()
    )
    matriz_curso["TAXA_DESASSISTIDO"] = np.where(
        matriz_curso["TOTAL_COTISTAS"] > 0,
        (matriz_curso["TOTAL_IDPNA"] / matriz_curso["TOTAL_COTISTAS"] * 100).round(2),
        0,
    )

    fig_scatter = px.scatter(
        matriz_curso,
        x="TOTAL_COTISTAS",
        y="TOTAL_COM_APOIO",
        size="TOTAL_ALUNOS",
        color="TAXA_DESASSISTIDO",
        hover_name="CURSO",
        hover_data=["CENTRO", "TOTAL_IDPNA"],
        color_continuous_scale="Reds",
        labels={
            "TOTAL_COTISTAS": "Total de Cotistas",
            "TOTAL_COM_APOIO": "Cotistas com Auxílio",
            "TAXA_DESASSISTIDO": "% Desassistidos (IDR_C)",
        },
    )
    # Linha de Cobertura Ideal (y = x)
    max_val = max(matriz_curso["TOTAL_COTISTAS"].max(), matriz_curso["TOTAL_COM_APOIO"].max())
    fig_scatter.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode="lines",
            name="Linha de Referência 1:1",
            line=dict(dash="dash", color="gray"),
        )
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: Desigualdade por Turno (Pergunta 2)
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("### Taxa de Cotistas Desassistidos — Diurno vs. Noturno")

    df_cot_turno = df_filtered[(df_filtered["IN_RESERVA_VAGAS"] == 1) & (df_filtered["GRUPO_TURNO"].isin(["Diurno", "Noturno"]))]

    resumo_turno = (
        df_cot_turno.groupby("GRUPO_TURNO")
        .apply(
            lambda x: pd.Series({
                "TOTAL_COTISTAS": x["TOTAL_ALUNOS"].sum(),
                "DESASSISTIDOS": x["TOTAL_IDPNA"].sum(),
                "ASSISTIDOS": x.loc[x["RECEBE_AUXILIO"] == 1, "TOTAL_ALUNOS"].sum(),
            }),
            include_groups=False,
        )
        .reset_index()
    )
    resumo_turno["PCT_DESASSISTIDOS"] = (resumo_turno["DESASSISTIDOS"] / resumo_turno["TOTAL_COTISTAS"] * 100).round(2)

    col_t1, col_t2 = st.columns([1, 1])

    with col_t1:
        fig_turno = px.bar(
            resumo_turno,
            x="GRUPO_TURNO",
            y="PCT_DESASSISTIDOS",
            color="GRUPO_TURNO",
            text="PCT_DESASSISTIDOS",
            color_discrete_map={"Diurno": "#2b5c8f", "Noturno": "#e6550d"},
            labels={"GRUPO_TURNO": "Turno", "PCT_DESASSISTIDOS": "% Desassistidos (IDPNA)"},
        )
        fig_turno.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_turno.update_layout(showlegend=False, yaxis_range=[0, 100])
        st.plotly_chart(fig_turno, use_container_width=True)

    with col_t2:
        st.markdown("#### Teste de Hipótese (Qui-Quadrado)")
        if len(resumo_turno) == 2 and resumo_turno["TOTAL_COTISTAS"].sum() > 0:
            obs = resumo_turno[["ASSISTIDOS", "DESASSISTIDOS"]].values
            chi2, p_val, gl, _ = chi2_contingency(obs)

            st.write(f"**Estatística Qui-Quadrado ($\chi^2$):** {chi2:.4f}")
            st.write(f"**Graus de Liberdade:** {gl}")
            st.write(f"**p-valor:** {p_val:.6f}")

            if p_val < 0.05:
                st.success("✅ **Resultado Significativo (p < 0,05):** Existe associação estatisticamente significativa entre o turno do curso e a taxa de desassistência de estudantes cotistas.")
            else:
                st.warning("⚠️ **Resultado Não Significativo (p >= 0,05):** Não foram encontradas evidências estatísticas de diferença entre os turnos no recorte selecionado.")
        else:
            st.info("Filtro atual insuficiente para rodar o teste Qui-Quadrado de Independência.")

# -----------------------------------------------------------------------------
# TAB 3: Equidade e Perfil Demográfico (Pergunta 4)
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("### Comparativo Demográfico: Corpo Discente Total vs. Beneficiários")

    col_d1, col_d2 = st.columns(2)

    def gerar_comp_demo(df, coluna):
        total = df.groupby(coluna)["TOTAL_ALUNOS"].sum()
        assistidos = df[df["RECEBE_AUXILIO"] == 1].groupby(coluna)["TOTAL_ALUNOS"].sum()
        comp = pd.concat([total, assistidos], axis=1, keys=["Total Campus", "Assistidos"]).fillna(0)
        comp["% Total"] = (comp["Total Campus"] / comp["Total Campus"].sum() * 100).round(2)
        comp["% Assistidos"] = (comp["Assistidos"] / comp["Assistidos"].sum() * 100).round(2)
        comp["Diferença (p.p.)"] = (comp["% Assistidos"] - comp["% Total"]).round(2)
        return comp.reset_index()

    with col_d1:
        st.markdown("#### Perfil por Raça/Cor")
        df_raca_comp = gerar_comp_demo(df_filtered, "RACA_DESCRICAO")
        df_raca_melt = df_raca_comp.melt(
            id_vars="RACA_DESCRICAO",
            value_vars=["% Total", "% Assistidos"],
            var_name="Grupo",
            value_name="Percentual",
        )
        fig_raca = px.bar(
            df_raca_melt,
            x="RACA_DESCRICAO",
            y="Percentual",
            color="Grupo",
            barmode="group",
            color_discrete_sequence=["#9ecae1", "#de2d26"],
        )
        fig_raca.update_layout(xaxis_title="", yaxis_title="% do Grupo")
        st.plotly_chart(fig_raca, use_container_width=True)
        st.dataframe(df_raca_comp[["RACA_DESCRICAO", "% Total", "% Assistidos", "Diferença (p.p.)"]], hide_index=True)

    with col_d2:
        st.markdown("#### Perfil por Sexo")
        df_sexo_comp = gerar_comp_demo(df_filtered, "SEXO_DESCRICAO")
        df_sexo_melt = df_sexo_comp.melt(
            id_vars="SEXO_DESCRICAO",
            value_vars=["% Total", "% Assistidos"],
            var_name="Grupo",
            value_name="Percentual",
        )
        fig_sexo = px.bar(
            df_sexo_melt,
            x="SEXO_DESCRICAO",
            y="Percentual",
            color="Grupo",
            barmode="group",
            color_discrete_sequence=["#9ecae1", "#de2d26"],
        )
        fig_sexo.update_layout(xaxis_title="", yaxis_title="% do Grupo")
        st.plotly_chart(fig_sexo, use_container_width=True)
        st.dataframe(df_sexo_comp[["SEXO_DESCRICAO", "% Total", "% Assistidos", "Diferença (p.p.)"]], hide_index=True)

# -----------------------------------------------------------------------------
# TAB 4: Visão por Centro de Ensino (Mapa de Calor)
# -----------------------------------------------------------------------------
with tab4:
    st.markdown("### Mapa de Calor da Demanda Reprimida (IDR_C) por Centro e Turno")

    heat = (
        df_filtered.groupby(["CENTRO", "GRUPO_TURNO"])
        .apply(
            lambda x: pd.Series({
                "TOTAL_COTISTAS": x.loc[x["IN_RESERVA_VAGAS"] == 1, "TOTAL_ALUNOS"].sum(),
                "TOTAL_IDPNA": x["TOTAL_IDPNA"].sum(),
            }),
            include_groups=False,
        )
        .reset_index()
    )
    heat["IDR_C"] = np.where(
        heat["TOTAL_COTISTAS"] > 0,
        (heat["TOTAL_IDPNA"] / heat["TOTAL_COTISTAS"] * 100).round(2),
        np.nan,
    )

    heat_pivot = heat.pivot(index="CENTRO", columns="GRUPO_TURNO", values="IDR_C")

    fig_heat = px.imshow(
        heat_pivot,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="Reds",
        labels=dict(x="Turno", y="Centro", color="% IDR_C"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)