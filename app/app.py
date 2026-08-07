# app.py
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
import streamlit as st

from css import load_css, render_metric_card

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Painel Executivo | UFPB",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# -----------------------------------------------------------------------------
# 2. RESOLUÇÃO DE CAMINHOS E CARREGAMENTO DE DADOS
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve() if "__file__" in locals() else Path.cwd()
BASE_DIR = SCRIPT_DIR if (SCRIPT_DIR / "data").exists() else SCRIPT_DIR.parent
ASSETS_DIR = SCRIPT_DIR / "assets"

PATH_FATO = BASE_DIR / "data" / "processed" / "Fato" / "fato_assistencia.csv"
PATH_DIM_CURSO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_curso_ufpb_campus_1.csv"
PATH_DIM_CENTRO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_centro.csv"
PATH_DIM_RACA = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_raca.csv"
PATH_DIM_SEXO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_sexo.csv"
PATH_DIM_TURNO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_turno.csv"


@st.cache_data
def load_data():
    if not PATH_FATO.exists():
        st.error(f"Base de dados não localizada em: {PATH_FATO}")
        st.stop()

    df_fato = pd.read_csv(PATH_FATO, sep=";")

    if PATH_DIM_CURSO.exists():
        df_c = pd.read_csv(PATH_DIM_CURSO, sep=";")
        df_fato = df_fato.merge(df_c[["CO_CURSO", "NO_CURSO"]], on="CO_CURSO", how="left").rename(
            columns={"NO_CURSO": "CURSO"}
        )

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

    mapa_turno = {"Matutino": "Diurno", "Vespertino": "Diurno", "Integral": "Diurno", "Noturno": "Noturno"}
    df_fato["GRUPO_TURNO"] = df_fato["TURNO_DESCRICAO"].map(mapa_turno).fillna("Não informado")

    return df_fato


df_raw = load_data()

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (LOGO UFPB E FILTROS)
# -----------------------------------------------------------------------------
with st.sidebar:
    logo_path = ASSETS_DIR / "logo_ufpb.png"
    if logo_path.exists():
        st.image(str(logo_path), width=90)

    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-top: 10px;'>UFPB</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.8rem; color: #64748b; margin-bottom: 12px;'>Assistência Estudantil</p>", unsafe_allow_html=True)
    st.markdown("---")

    centros = ["Todos"] + sorted(list(df_raw["CENTRO"].dropna().unique()))
    centro_sel = st.selectbox("Centro de Ensino", centros)

    turnos = ["Todos"] + sorted(list(df_raw["GRUPO_TURNO"].unique()))
    turno_sel = st.selectbox("Turno do Curso", turnos)

    df_filtered = df_raw.copy()
    if centro_sel != "Todos":
        df_filtered = df_filtered[df_filtered["CENTRO"] == centro_sel]
    if turno_sel != "Todos":
        df_filtered = df_filtered[df_filtered["GRUPO_TURNO"] == turno_sel]

    cursos = ["Todos"] + sorted(list(df_filtered["CURSO"].dropna().unique()))
    curso_sel = st.selectbox("Curso Específico", cursos)

    if curso_sel != "Todos":
        df_filtered = df_filtered[df_filtered["CURSO"] == curso_sel]

    st.markdown("---")
    st.markdown("<p style='font-size: 0.75rem; color: #94a3b8;'>UFPB - Campus I</p>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. CABEÇALHO & CARDS KPI
# -----------------------------------------------------------------------------
st.markdown("<h2 style='font-weight: 700; color: #0f172a; margin-bottom: 2px;'>Diagnóstico de Assistência Estudantil</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569; font-size: 0.9rem; margin-bottom: 20px;'>Relatório de monitoramento de demanda reprimida e alocação orçamentária</p>", unsafe_allow_html=True)

total_alunos = df_filtered["TOTAL_ALUNOS"].sum()
total_cotistas = df_filtered.loc[df_filtered["IN_RESERVA_VAGAS"] == 1, "TOTAL_ALUNOS"].sum()
total_assistidos = df_filtered.loc[df_filtered["RECEBE_AUXILIO"] == 1, "TOTAL_ALUNOS"].sum()
total_idpna = df_filtered["TOTAL_IDPNA"].sum()

pct_cotistas = (total_cotistas / total_alunos * 100) if total_alunos > 0 else 0
pct_cobertura = (total_assistidos / total_cotistas * 100) if total_cotistas > 0 else 0
pct_idpna = (total_idpna / total_cotistas * 100) if total_cotistas > 0 else 0

k1, k2, k3, k4 = st.columns(4)

with k1:
    render_metric_card("Matriculados", f"{total_alunos:,.0f}", "Corpo discente ativo", "TOTAL", "default")

with k2:
    render_metric_card("Estudantes Cotistas", f"{total_cotistas:,.0f}", "Ações Afirmativas", f"{pct_cotistas:.1f}% do total", "default")

with k3:
    render_metric_card("Atendidos com Auxílio", f"{total_assistidos:,.0f}", "Bolsistas ativos", f"{pct_cobertura:.1f}% Cobertura", "primary", value_color="#1e3a8a")

with k4:
    render_metric_card("Demanda Reprimida", f"{total_idpna:,.0f}", "Cotistas sem assistência (IDPNA)", f"{pct_idpna:.1f}% Fila", "primary", value_color="#1e3a8a")

# -----------------------------------------------------------------------------
# 5. ABAS VISUAIS
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "Priorização de Editais",
    "Análise de Turno",
    "Equidade Demográfica",
])

# -----------------------------------------------------------------------------
# TAB 1: PRIORIZAÇÃO DE EDITAIS
# -----------------------------------------------------------------------------
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    if df_filtered.empty or total_alunos == 0:
        st.info("Nenhum registro encontrado para a combinação de filtros selecionada.")
    else:
        c_left, c_right = st.columns([1.1, 1])

        with c_left:
            st.markdown(
                """
                <div class="saas-card">
                    <h4 style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 2px;">Cursos com Maior Demanda Reprimida (IDPNA)</h4>
                    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 16px;">Volume absoluto de estudantes cotistas sem atendimento</p>
            """,
                unsafe_allow_html=True,
            )

            df_top_idpna = (
                df_filtered.groupby("CURSO")["TOTAL_IDPNA"]
                .sum()
                .reset_index()
                .sort_values("TOTAL_IDPNA", ascending=True)
                .tail(10)
            )

            fig_bar = px.bar(
                df_top_idpna,
                x="TOTAL_IDPNA",
                y="CURSO",
                orientation="h",
                text="TOTAL_IDPNA",
                color_discrete_sequence=["#1e3a8a"],
            )
            fig_bar.update_traces(textposition="outside", cliponaxis=False)
            fig_bar.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=30, t=0, b=0),
                xaxis=dict(showgrid=False, title="", showticklabels=False),
                yaxis=dict(title="", showgrid=False, tickfont=dict(size=11, color="#334155")),
                height=330,
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c_right:
            st.markdown(
                """
                <div class="saas-card">
                    <h4 style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 2px;">Matriz de Cobertura por Curso</h4>
                    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 16px;">Relação entre alunos cotistas e bolsistas ativos</p>
            """,
                unsafe_allow_html=True,
            )

            matriz_curso = (
                df_filtered.groupby(["CURSO", "CENTRO"])
                .apply(
                    lambda x: pd.Series({
                        "TOTAL_COTISTAS": x.loc[x["IN_RESERVA_VAGAS"] == 1, "TOTAL_ALUNOS"].sum(),
                        "TOTAL_COM_APOIO": x.loc[x["RECEBE_AUXILIO"] == 1, "TOTAL_ALUNOS"].sum(),
                        "TOTAL_IDPNA": x["TOTAL_IDPNA"].sum(),
                    }),
                    include_groups=False,
                )
                .reset_index()
            )
            
            if not matriz_curso.empty and "TOTAL_COTISTAS" in matriz_curso.columns:
                matriz_curso = matriz_curso[matriz_curso["TOTAL_COTISTAS"] > 0]

            if not matriz_curso.empty:
                fig_scatter = px.scatter(
                    matriz_curso,
                    x="TOTAL_COTISTAS",
                    y="TOTAL_COM_APOIO",
                    size="TOTAL_IDPNA",
                    color_discrete_sequence=["#1e3a8a"],
                    hover_name="CURSO",
                    hover_data=["CENTRO", "TOTAL_IDPNA"],
                )
                max_v = max(matriz_curso["TOTAL_COTISTAS"].max(), 10)
                fig_scatter.add_trace(
                    go.Scatter(
                        x=[0, max_v],
                        y=[0, max_v],
                        mode="lines",
                        name="Meta 100%",
                        line=dict(dash="dash", color="#cbd5e1", width=1.5),
                    )
                )
                fig_scatter.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False,
                    xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Nº Cotistas"),
                    yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Nº Atendidos"),
                    height=330,
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Sem dados suficientes para exibir a matriz.")
            st.markdown("</div>", unsafe_allow_html=True)

        # Tabela Executiva
        st.markdown(
            """
            <div class="saas-card">
                <h4 style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 12px;">Detalhamento Tático por Curso</h4>
        """,
            unsafe_allow_html=True,
        )

        if not matriz_curso.empty and "TOTAL_IDPNA" in matriz_curso.columns:
            df_table = matriz_curso.sort_values("TOTAL_IDPNA", ascending=False).copy()
            df_table["Taxa Desassistência (%)"] = ((df_table["TOTAL_IDPNA"] / df_table["TOTAL_COTISTAS"]) * 100).round(1)
            df_table.columns = ["Curso", "Centro", "Nº Cotistas", "Nº Atendidos", "Fila IDPNA", "Taxa Desassistência (%)"]

            st.dataframe(
                df_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Taxa Desassistência (%)": st.column_config.ProgressColumn(
                        "Taxa Desassistência (%)",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                },
            )
        else:
            st.info("Nenhum dado de cursos disponível para visualização em tabela.")
            
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: ANÁLISE POR TURNO
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    
    if df_filtered.empty or total_alunos == 0:
        st.info("Nenhum registro encontrado para a combinação de filtros selecionada.")
    else:
        col_t1, col_t2 = st.columns([1, 1])

        df_cot_turno = df_filtered[
            (df_filtered["IN_RESERVA_VAGAS"] == 1) & (df_filtered["GRUPO_TURNO"].isin(["Diurno", "Noturno"]))
        ]

        if df_cot_turno.empty:
            st.info("Não há dados de cotistas para os turnos selecionados.")
        else:
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
            resumo_turno["PCT_DESASSISTIDOS"] = (resumo_turno["DESASSISTIDOS"] / resumo_turno["TOTAL_COTISTAS"] * 100).round(1)

            with col_t1:
                st.markdown(
                    """
                    <div class="saas-card">
                        <h4 style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 2px;">Proporção de Cotistas Não Atendidos</h4>
                        <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 16px;">Comparativo percentual por turno</p>
                """,
                    unsafe_allow_html=True,
                )

                fig_turno = px.bar(
                    resumo_turno,
                    x="GRUPO_TURNO",
                    y="PCT_DESASSISTIDOS",
                    text="PCT_DESASSISTIDOS",
                    color="GRUPO_TURNO",
                    color_discrete_map={"Diurno": "#64748b", "Noturno": "#1e3a8a"},
                )
                fig_turno.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig_turno.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    yaxis=dict(range=[0, 100], showgrid=False, title=""),
                    xaxis=dict(title="", showgrid=False),
                    height=280,
                )
                st.plotly_chart(fig_turno, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_t2:
                st.markdown(
                    """
                    <div class="saas-card">
                        <h4 style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 8px;">Teste Hipotético de Qui-Quadrado (&chi;²)</h4>
                """,
                    unsafe_allow_html=True,
                )

                if len(resumo_turno) == 2 and resumo_turno["TOTAL_COTISTAS"].sum() > 0:
                    obs = resumo_turno[["ASSISTIDOS", "DESASSISTIDOS"]].values
                    chi2, p_val, gl, _ = chi2_contingency(obs)

                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 12px;">
                            <span style="font-size: 0.8rem; color: #64748b;">Estatística Qui-Quadrado</span><br>
                            <b style="font-size: 1.3rem; color: #0f172a;">{chi2:.2f}</b> 
                            <span style="font-size: 0.85rem; color: #64748b; margin-left: 16px;">p-valor: <b>{p_val:.4e}</b></span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    if p_val < 0.05:
                        st.markdown(
                            """
                            <div class="badge-primary" style="display: block; text-align: center; font-size: 0.8rem; padding: 10px;">
                                Diferença estatisticamente significativa observada entre os turnos (p < 0,05).
                            </div>
                        """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            """
                            <div class="badge-default" style="display: block; text-align: center; font-size: 0.8rem; padding: 10px;">
                                Sem diferença estatística significativa na proporção observada (p >= 0,05).
                            </div>
                        """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("Necessário dados de ambos os turnos (Diurno e Noturno) para realizar o teste estatístico.")
                st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 3: EQUIDADE E DEMOGRAFIA
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)

    if df_filtered.empty or total_alunos == 0:
        st.info("Nenhum registro encontrado para a combinação de filtros selecionada.")
    else:
        def calc_equidade(df, col_demo):
            tot = df.groupby(col_demo)["TOTAL_ALUNOS"].sum()
            ast = df[df["RECEBE_AUXILIO"] == 1].groupby(col_demo)["TOTAL_ALUNOS"].sum()
            df_c = pd.concat([tot, ast], axis=1, keys=["Total Campus", "Assistidos"]).fillna(0)
            
            tot_sum = df_c["Total Campus"].sum()
            ast_sum = df_c["Assistidos"].sum()

            df_c["% no Campus"] = (df_c["Total Campus"] / tot_sum * 100).round(1) if tot_sum > 0 else 0
            df_c["% nos Assistidos"] = (df_c["Assistidos"] / ast_sum * 100).round(1) if ast_sum > 0 else 0
            df_c["Diferença (p.p.)"] = (df_c["% nos Assistidos"] - df_c["% no Campus"]).round(1)
            return df_c.reset_index()

        ce1, ce2 = st.columns(2)

        with ce1:
            st.markdown(
                """
                <div class="saas-card">
                    <h4 style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 2px;">Representatividade por Raça/Cor</h4>
                    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 16px;">Variação em Pontos Percentuais (% Assistidos - % Campus)</p>
            """,
                unsafe_allow_html=True,
            )

            df_raca = calc_equidade(df_filtered, "RACA_DESCRICAO")

            fig_raca = px.bar(
                df_raca,
                x="RACA_DESCRICAO",
                y="Diferença (p.p.)",
                text="Diferença (p.p.)",
                color="Diferença (p.p.)",
                color_continuous_scale=["#64748b", "#cbd5e1", "#1e3a8a"],
            )
            fig_raca.update_traces(texttemplate="%{text:+.1f} p.p.", textposition="outside")
            fig_raca.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                yaxis=dict(title="", showgrid=True, gridcolor="#f1f5f9"),
                xaxis=dict(title=""),
                height=280,
            )
            st.plotly_chart(fig_raca, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with ce2:
            st.markdown(
                """
                <div class="saas-card">
                    <h4 style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 2px;">Representatividade por Gênero</h4>
                    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 16px;">Variação em Pontos Percentuais (% Assistidos - % Campus)</p>
            """,
                unsafe_allow_html=True,
            )

            df_sexo = calc_equidade(df_filtered, "SEXO_DESCRICAO")

            fig_sexo = px.bar(
                df_sexo,
                x="SEXO_DESCRICAO",
                y="Diferença (p.p.)",
                text="Diferença (p.p.)",
                color="Diferença (p.p.)",
                color_continuous_scale=["#64748b", "#cbd5e1", "#1e3a8a"],
            )
            fig_sexo.update_traces(texttemplate="%{text:+.1f} p.p.", textposition="outside")
            fig_sexo.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                yaxis=dict(title="", showgrid=True, gridcolor="#f1f5f9"),
                xaxis=dict(title=""),
                height=280,
            )
            st.plotly_chart(fig_sexo, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)