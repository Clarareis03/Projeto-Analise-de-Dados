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
PATH_DIM_GRAU = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_grau.csv"
PATH_DIM_MODALIDADE = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_modalidade.csv"


@st.cache_data
def load_data():
    if not PATH_FATO.exists():
        st.error(f"Base de dados não localizada em: {PATH_FATO}")
        st.stop()

    df_fato = pd.read_csv(PATH_FATO, sep=";")

    # Cruzamento com Tabela Dimensão Curso
    if PATH_DIM_CURSO.exists():
        df_c = pd.read_csv(PATH_DIM_CURSO, sep=";")
        if "CO_CURSO" in df_fato.columns and "CO_CURSO" in df_c.columns:
            df_fato = df_fato.merge(df_c[["CO_CURSO", "NO_CURSO"]], on="CO_CURSO", how="left").rename(
                columns={"NO_CURSO": "CURSO"}
            )

    # Cruzamento com Tabela Dimensão Centro
    if PATH_DIM_CENTRO.exists():
        df_cent = pd.read_csv(PATH_DIM_CENTRO, sep=";")
        common_cent = list(set(df_fato.columns).intersection(set(df_cent.columns)))
        if common_cent:
            df_fato = df_fato.merge(df_cent, on=common_cent, how="left")

    # Cruzamento com Tabela Dimensão Raça
    if PATH_DIM_RACA.exists():
        df_r = pd.read_csv(PATH_DIM_RACA, sep=";")
        if "DESCRICAO" in df_r.columns:
            df_r = df_r.rename(columns={"DESCRICAO": "RACA_DESCRICAO"})
        common_raca = list(set(df_fato.columns).intersection(set(df_r.columns)))
        if common_raca:
            df_fato = df_fato.merge(df_r, on=common_raca, how="left")

    # Cruzamento com Tabela Dimensão Sexo
    if PATH_DIM_SEXO.exists():
        df_s = pd.read_csv(PATH_DIM_SEXO, sep=";")
        if "DESCRICAO" in df_s.columns:
            df_s = df_s.rename(columns={"DESCRICAO": "SEXO_DESCRICAO"})
        common_sexo = list(set(df_fato.columns).intersection(set(df_s.columns)))
        if common_sexo:
            df_fato = df_fato.merge(df_s, on=common_sexo, how="left")

    # Cruzamento com Tabela Dimensão Turno
    if PATH_DIM_TURNO.exists():
        df_t = pd.read_csv(PATH_DIM_TURNO, sep=";")
        if "DESCRICAO" in df_t.columns:
            df_t = df_t.rename(columns={"DESCRICAO": "TURNO_DESCRICAO"})
        common_turno = list(set(df_fato.columns).intersection(set(df_t.columns)))
        if common_turno:
            df_fato = df_fato.merge(df_t, on=common_turno, how="left")

    # Cruzamento com Tabela Dimensão Grau
    if PATH_DIM_GRAU.exists():
        df_g = pd.read_csv(PATH_DIM_GRAU, sep=";")
        if "DESCRICAO" in df_g.columns:
            df_g = df_g.rename(columns={"DESCRICAO": "GRAU_DESCRICAO"})
        common_grau = list(set(df_fato.columns).intersection(set(df_g.columns)))
        if common_grau:
            df_fato = df_fato.merge(df_g, on=common_grau, how="left")

    # Cruzamento com Tabela Dimensão Modalidade
    if PATH_DIM_MODALIDADE.exists():
        df_m = pd.read_csv(PATH_DIM_MODALIDADE, sep=";")
        if "DESCRICAO" in df_m.columns:
            df_m = df_m.rename(columns={"DESCRICAO": "MODALIDADE_DESCRICAO"})
        common_mod = list(set(df_fato.columns).intersection(set(df_m.columns)))
        if common_mod:
            df_fato = df_fato.merge(df_m, on=common_mod, how="left")

    # Agrupamento de turnos
    if "TURNO_DESCRICAO" in df_fato.columns:
        mapa_turno = {"Matutino": "Diurno", "Vespertino": "Diurno", "Integral": "Diurno", "Noturno": "Noturno"}
        df_fato["GRUPO_TURNO"] = df_fato["TURNO_DESCRICAO"].map(mapa_turno).fillna("Não informado")

    return df_fato


df_raw = load_data()

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (FILTROS DE DIMENSÃO)
# -----------------------------------------------------------------------------
with st.sidebar:
    logo_path = ASSETS_DIR / "logo_ufpb.png"
    if logo_path.exists():
        st.image(str(logo_path), width=90)

    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-top: 10px;'>UFPB</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.8rem; color: #64748b; margin-bottom: 12px;'>Assistência Estudantil</p>", unsafe_allow_html=True)
    st.markdown("---")

    df_filtered = df_raw.copy()

    # 1. Centro
    if "CENTRO" in df_filtered.columns:
        centros = ["Todos"] + sorted([str(x) for x in df_filtered["CENTRO"].dropna().unique()])
        centro_sel = st.selectbox("Centro de Ensino", centros)
        if centro_sel != "Todos":
            df_filtered = df_filtered[df_filtered["CENTRO"] == centro_sel]

    # 2. Turno
    if "GRUPO_TURNO" in df_filtered.columns:
        turnos = ["Todos"] + sorted([str(x) for x in df_filtered["GRUPO_TURNO"].dropna().unique()])
        turno_sel = st.selectbox("Turno do Curso", turnos)
        if turno_sel != "Todos":
            df_filtered = df_filtered[df_filtered["GRUPO_TURNO"] == turno_sel]

    # 3. Curso
    if "CURSO" in df_filtered.columns:
        cursos = ["Todos"] + sorted([str(x) for x in df_filtered["CURSO"].dropna().unique()])
        curso_sel = st.selectbox("Curso Específico", cursos)
        if curso_sel != "Todos":
            df_filtered = df_filtered[df_filtered["CURSO"] == curso_sel]

    # 4. Raça / Cor
    col_raca = "RACA_DESCRICAO" if "RACA_DESCRICAO" in df_filtered.columns else ("DESCRICAO_RACA" if "DESCRICAO_RACA" in df_filtered.columns else None)
    if col_raca:
        racas = ["Todos"] + sorted([str(x) for x in df_filtered[col_raca].dropna().unique()])
        raca_sel = st.selectbox("Raça / Cor", racas)
        if raca_sel != "Todos":
            df_filtered = df_filtered[df_filtered[col_raca] == raca_sel]

    # 5. Sexo / Gênero
    col_sexo = "SEXO_DESCRICAO" if "SEXO_DESCRICAO" in df_filtered.columns else ("DESCRICAO_SEXO" if "DESCRICAO_SEXO" in df_filtered.columns else None)
    if col_sexo:
        sexos = ["Todos"] + sorted([str(x) for x in df_filtered[col_sexo].dropna().unique()])
        sexo_sel = st.selectbox("Sexo / Gênero", sexos)
        if sexo_sel != "Todos":
            df_filtered = df_filtered[df_filtered[col_sexo] == sexo_sel]

    # 6. Modalidade de Ingresso
    col_mod = "MODALIDADE_DESCRICAO" if "MODALIDADE_DESCRICAO" in df_filtered.columns else ("MODALIDADE" if "MODALIDADE" in df_filtered.columns else None)
    if col_mod:
        modalidades = ["Todos"] + sorted([str(x) for x in df_filtered[col_mod].dropna().unique()])
        modalidade_sel = st.selectbox("Modalidade de Ingresso", modalidades)
        if modalidade_sel != "Todos":
            df_filtered = df_filtered[df_filtered[col_mod] == modalidade_sel]

    st.markdown("---")
    st.markdown("<p style='font-size: 0.75rem; color: #94a3b8;'>UFPB - Campus I</p>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. CABEÇALHO & CARDS KPI (PAINEL DE COBERTURA INSTITUCIONAL)
# -----------------------------------------------------------------------------
st.markdown("<h2 style='font-weight: 700; color: #0f172a; margin-bottom: 2px;'>Painel de Cobertura Institucional — UFPB Campus I</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569; font-size: 0.9rem; margin-bottom: 20px;'>Relatório de monitoramento de demanda reprimida e alocação orçamentária</p>", unsafe_allow_html=True)

# Métricas Calculadas alinhadas com o Painel de Cobertura Institucional
total_alunos = df_filtered["TOTAL_ALUNOS"].sum() if "TOTAL_ALUNOS" in df_filtered.columns else 0
total_cotistas = df_filtered.loc[df_filtered["IN_RESERVA_VAGAS"] == 1, "TOTAL_ALUNOS"].sum() if "IN_RESERVA_VAGAS" in df_filtered.columns else 0

# Cotistas que efetivamente recebem auxílio PRAPE
cotistas_atendidos = (
    df_filtered.loc[(df_filtered["IN_RESERVA_VAGAS"] == 1) & (df_filtered["RECEBE_AUXILIO"] == 1), "TOTAL_ALUNOS"].sum()
    if "IN_RESERVA_VAGAS" in df_filtered.columns and "RECEBE_AUXILIO" in df_filtered.columns
    else 0
)

total_idpna = df_filtered["TOTAL_IDPNA"].sum() if "TOTAL_IDPNA" in df_filtered.columns else 0

# Taxas Percentuais
pct_cotistas = (total_cotistas / total_alunos * 100) if total_alunos > 0 else 0
cobertura_prape = (cotistas_atendidos / total_cotistas * 100) if total_cotistas > 0 else 0

# Formatação visual dos números no padrão brasileiro (ex: 31.210 e 11.730)
str_total_alunos = f"{total_alunos:,.0f}".replace(",", ".")
str_idpna = f"{total_idpna:,.0f}".replace(",", ".")

k1, k2, k3, k4 = st.columns(4)

with k1:
    render_metric_card(
        "Total de Estudantes (Campus I)",
        str_total_alunos,
        "Corpo discente ativo",
        "TOTAL",
        "default"
    )

with k2:
    render_metric_card(
        "% Ingressantes por Cotas",
        f"{pct_cotistas:.1f}%",
        f"{total_cotistas:,.0f}".replace(",", ".") + " estudantes cotistas",
        "COTAS",
        "default"
    )

with k3:
    render_metric_card(
        "Cobertura PRAPE sobre Cotistas",
        f"{cobertura_prape:.1f}%",
        f"{cotistas_atendidos:,.0f}".replace(",", ".") + " cotistas assistidos",
        "PRAPE",
        "primary",
        value_color="#10b981"  # Destaque verde para cobertura
    )

with k4:
    render_metric_card(
        "Demanda Potencial Não Atendida (IDPNA)",
        str_idpna,
        "Fila de espera de cotistas",
        "IDPNA",
        "primary",
        value_color="#ef4444"  # Destaque vermelho para demanda reprimida
    )

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
                    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 16px;">Relação entre alunos cotistas e cotistas com apoio</p>
            """,
                unsafe_allow_html=True,
            )

            matriz_curso = (
                df_filtered.groupby(["CURSO", "CENTRO"])
                .apply(
                    lambda x: pd.Series({
                        "TOTAL_COTISTAS": x.loc[x["IN_RESERVA_VAGAS"] == 1, "TOTAL_ALUNOS"].sum() if "IN_RESERVA_VAGAS" in x.columns else 0,
                        "COTISTAS_ATENDIDOS": x.loc[(x["IN_RESERVA_VAGAS"] == 1) & (x["RECEBE_AUXILIO"] == 1), "TOTAL_ALUNOS"].sum() if "IN_RESERVA_VAGAS" in x.columns and "RECEBE_AUXILIO" in x.columns else 0,
                        "TOTAL_IDPNA": x["TOTAL_IDPNA"].sum() if "TOTAL_IDPNA" in x.columns else 0,
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
                    y="COTISTAS_ATENDIDOS",
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
                    yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Cotistas Atendidos"),
                    height=330,
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Sem dados suficientes para exibir a matriz.")
            st.markdown("</div>", unsafe_allow_html=True)

        # Tabela Executiva Detalhada
        st.markdown(
            """
            <div class="saas-card">
                <h4 style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 12px;">Detalhamento Tático por Curso</h4>
        """,
            unsafe_allow_html=True,
        )

        if not matriz_curso.empty and "TOTAL_IDPNA" in matriz_curso.columns:
            df_table = matriz_curso.sort_values("TOTAL_IDPNA", ascending=False).copy()
            df_table["Taxa Desassistência (%)"] = np.where(
                df_table["TOTAL_COTISTAS"] > 0,
                ((df_table["TOTAL_IDPNA"] / df_table["TOTAL_COTISTAS"]) * 100).round(1),
                0
            )
            df_table.columns = ["Curso", "Centro", "Nº Cotistas", "Cotistas Atendidos", "Fila IDPNA", "Taxa Desassistência (%)"]

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
        ] if "IN_RESERVA_VAGAS" in df_filtered.columns and "GRUPO_TURNO" in df_filtered.columns else pd.DataFrame()

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
            resumo_turno["PCT_DESASSISTIDOS"] = np.where(
                resumo_turno["TOTAL_COTISTAS"] > 0,
                (resumo_turno["DESASSISTIDOS"] / resumo_turno["TOTAL_COTISTAS"] * 100).round(1),
                0
            )

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
            if col_demo not in df.columns:
                return pd.DataFrame()
            tot = df.groupby(col_demo)["TOTAL_ALUNOS"].sum()
            ast = df[df["RECEBE_AUXILIO"] == 1].groupby(col_demo)["TOTAL_ALUNOS"].sum() if "RECEBE_AUXILIO" in df.columns else pd.Series(dtype=float)
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

            col_raca_plot = col_raca if col_raca else "RACA_DESCRICAO"
            df_raca = calc_equidade(df_filtered, col_raca_plot)

            if not df_raca.empty:
                fig_raca = px.bar(
                    df_raca,
                    x=col_raca_plot,
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
            else:
                st.info("Dimensão de Raça não disponível.")
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

            col_sexo_plot = col_sexo if col_sexo else "SEXO_DESCRICAO"
            df_sexo = calc_equidade(df_filtered, col_sexo_plot)

            if not df_sexo.empty:
                fig_sexo = px.bar(
                    df_sexo,
                    x=col_sexo_plot,
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
            else:
                st.info("Dimensão de Sexo não disponível.")
            st.markdown("</div>", unsafe_allow_html=True)