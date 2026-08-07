# app.py
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
import streamlit as st

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA & CSS CUSTOMIZADO (DESIGN EXECUTIVO DE CARDS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Painel Executivo — Assistência Estudantil UFPB",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Estilo Global e Fundo */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Estilização da Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    
    /* Cards Executivos */
    div[data-testid="stVerticalBlock"] > div[data-testid="stBlock"] {
        border-radius: 12px;
    }
    
    .exec-card {
        background-color: #ffffff;
        padding: 20px 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
        margin-bottom: 2px;
    }
    .metric-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-sub {
        font-size: 0.8125rem;
        color: #64748b;
    }
    
    /* Destaques de Alerta */
    .alert-text {
        color: #dc2626;
        font-weight: 600;
    }
    
    /* Ocultar elementos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. RESOLUÇÃO DE CAMINHOS & DADOS
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve() if "__file__" in locals() else Path.cwd()
BASE_DIR = SCRIPT_DIR if (SCRIPT_DIR / "data").exists() else SCRIPT_DIR.parent

PATH_FATO = BASE_DIR / "data" / "processed" / "Fato" / "fato_assistencia.csv"
PATH_DIM_CURSO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_curso_ufpb_campus_1.csv"
PATH_DIM_CENTRO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_centro.csv"
PATH_DIM_RACA = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_raca.csv"
PATH_DIM_SEXO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_sexo.csv"
PATH_DIM_TURNO = BASE_DIR / "data" / "processed" / "Dimensões" / "dim_turno.csv"


@st.cache_data
def load_data():
    if not PATH_FATO.exists():
        st.error(f"Base de dados não localizada no caminho: {PATH_FATO}")
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
# 3. SIDEBAR DE CONTROLE E FILTROS
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 🏛️ UFPB Campus I")
st.sidebar.markdown("**Painel de Tomada de Decisão**")
st.sidebar.markdown("---")

centros = ["Todos"] + sorted(list(df_raw["CENTRO"].dropna().unique()))
centro_sel = st.sidebar.selectbox("Centro de Ensino", centros)

turnos = ["Todos"] + sorted(list(df_raw["GRUPO_TURNO"].unique()))
turno_sel = st.sidebar.selectbox("Turno do Curso", turnos)

df_filtered = df_raw.copy()
if centro_sel != "Todos":
    df_filtered = df_filtered[df_filtered["CENTRO"] == centro_sel]
if turno_sel != "Todos":
    df_filtered = df_filtered[df_filtered["GRUPO_TURNO"] == turno_sel]

cursos = ["Todos"] + sorted(list(df_filtered["CURSO"].dropna().unique()))
curso_sel = st.sidebar.selectbox("Curso Específico", cursos)

if curso_sel != "Todos":
    df_filtered = df_filtered[df_filtered["CURSO"] == curso_sel]

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Metodologia Storytelling:**\n"
    "- Foco em lacunas de atendimento (IDPNA)\n"
    "- Dados extraídos do SEDAP+ (2023)\n"
    "- Resoluções PRAPE / UFPB"
)

# -----------------------------------------------------------------------------
# 4. CABEÇALHO & CARDS EXECUTIVOS DE KPI (VISÃO GERAL)
# -----------------------------------------------------------------------------
st.markdown("## 📊 Diagnóstico de Assistência Estudantil e Demanda Reprimida")
st.markdown(
    " Monitoramento de vulnerabilidade socioeconômica e alocação orçamentária dos auxílios institucionais."
)
st.markdown("<br>", unsafe_allow_html=True)

# Cálculo dos Métricas Principais
total_alunos = df_filtered["TOTAL_ALUNOS"].sum()
total_cotistas = df_filtered.loc[df_filtered["IN_RESERVA_VAGAS"] == 1, "TOTAL_ALUNOS"].sum()
total_assistidos = df_filtered.loc[df_filtered["RECEBE_AUXILIO"] == 1, "TOTAL_ALUNOS"].sum()
total_idpna = df_filtered["TOTAL_IDPNA"].sum()

pct_cotistas = (total_cotistas / total_alunos * 100) if total_alunos > 0 else 0
pct_cobertura = (total_assistidos / total_cotistas * 100) if total_cotistas > 0 else 0
pct_idpna = (total_idpna / total_cotistas * 100) if total_cotistas > 0 else 0

# Exibição em Cards CSS
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
        <div class="exec-card">
            <div class="metric-label">Corpo Discente Total</div>
            <div class="metric-value">{total_alunos:,.0f}</div>
            <div class="metric-sub">Matriculados no recorte</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""
        <div class="exec-card">
            <div class="metric-label">Estudantes Cotistas</div>
            <div class="metric-value">{total_cotistas:,.0f}</div>
            <div class="metric-sub"><b>{pct_cotistas:.1f}%</b> do total de alunos</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""
        <div class="exec-card">
            <div class="metric-label">Atendidos por Auxílios</div>
            <div class="metric-value" style="color: #1e3a8a;">{total_assistidos:,.0f}</div>
            <div class="metric-sub">Taxa de Cobertura: <b>{pct_cobertura:.1f}%</b></div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""
        <div class="exec-card" style="border-left: 4px solid #dc2626;">
            <div class="metric-label">Demanda Reprimida (IDPNA)</div>
            <div class="metric-value" style="color: #dc2626;">{total_idpna:,.0f}</div>
            <div class="metric-sub"><span class="alert-text">{pct_idpna:.1f}%</span> dos cotistas sem apoio</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# 5. ABAS COM FOCO EM DECISÃO E STORYTELLING
# -----------------------------------------------------------------------------
tab_prioridades, tab_turno, tab_equidade = st.tabs([
    "🎯 Priorização de Editais (Cursos Críticos)",
    "🌓 Análise de Impacto por Turno",
    "🧬 Monitoramento de Equidade Racial e Gênero",
])

# -----------------------------------------------------------------------------
# TAB 1: PRIORIZAÇÃO DE EDITAIS
# -----------------------------------------------------------------------------
with tab_prioridades:
    st.markdown("### Onde estão as maiores lacunas de atendimento da UFPB?")
    st.caption("Cursos com maior volume absoluto de alunos cotistas desassistidos requerem prioridade nos novos editais da PRAPE.")

    col_chart1, col_chart2 = st.columns([1.2, 1])

    with col_chart1:
        st.markdown("**Top 10 Cursos em Volume Absoluto de IDPNA**")
        df_top_idpna = (
            df_filtered.groupby("CURSO")["TOTAL_IDPNA"]
            .sum()
            .reset_index()
            .sort_values("TOTAL_IDPNA", ascending=True)
            .tail(10)
        )

        fig_bar_top = px.bar(
            df_top_idpna,
            x="TOTAL_IDPNA",
            y="CURSO",
            orientation="h",
            text="TOTAL_IDPNA",
            color_discrete_sequence=["#dc2626"],
        )
        fig_bar_top.update_traces(textposition="outside", cliponaxis=False)
        fig_bar_top.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=0, r=30, t=10, b=0),
            xaxis=dict(showgrid=False, title="", showticklabels=False),
            yaxis=dict(title="", showgrid=False),
            height=380,
        )
        st.plotly_chart(fig_bar_top, use_container_width=True)

    with col_chart2:
        st.markdown("**Matriz de Alocação: Cobertura vs. Vulnerabilidade**")
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
        matriz_curso = matriz_curso[matriz_curso["TOTAL_COTISTAS"] > 0]

        fig_scatter = px.scatter(
            matriz_curso,
            x="TOTAL_COTISTAS",
            y="TOTAL_COM_APOIO",
            size="TOTAL_IDPNA",
            color_discrete_sequence=["#1e3a8a"],
            hover_name="CURSO",
            hover_data=["CENTRO", "TOTAL_IDPNA"],
            labels={"TOTAL_COTISTAS": "Total de Cotistas", "TOTAL_COM_APOIO": "Cotistas Assistidos"},
        )
        # Linha Ideal de Atendimento 1:1
        max_v = max(matriz_curso["TOTAL_COTISTAS"].max(), 10)
        fig_scatter.add_trace(
            go.Scatter(
                x=[0, max_v],
                y=[0, max_v],
                mode="lines",
                name="Meta 100% Atendimento",
                line=dict(dash="dot", color="#94a3b8"),
            )
        )
        fig_scatter.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            height=380,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📋 Tabela Tática para Gestão de Edital")
    
    # Tabela limpa e formatada
    df_table = matriz_curso.sort_values("TOTAL_IDPNA", ascending=False).copy()
    df_table["Taxa Desassistência (%)"] = ((df_table["TOTAL_IDPNA"] / df_table["TOTAL_COTISTAS"]) * 100).round(1)
    df_table.columns = ["Curso", "Centro", "Nº Cotistas", "Nº Atendidos", "Nº IDPNA (Fila)", "Taxa Desassistência (%)"]
    
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

# -----------------------------------------------------------------------------
# TAB 2: ANÁLISE POR TURNO
# -----------------------------------------------------------------------------
with tab_turno:
    st.markdown("### Disparidade entre Cursos Diurnos e Noturnos")
    st.caption("Avaliação se os cursos do período noturno possuem barreira no acesso aos programas permanentes de assistência.")

    df_cot_turno = df_filtered[
        (df_filtered["IN_RESERVA_VAGAS"] == 1) & (df_filtered["GRUPO_TURNO"].isin(["Diurno", "Noturno"]))
    ]

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

    c_t1, c_t2 = st.columns([1, 1.2])

    with c_t1:
        st.markdown("**Proporção de Cotistas Não Atendidos por Turno**")
        fig_turno = px.bar(
            resumo_turno,
            x="GRUPO_TURNO",
            y="PCT_DESASSISTIDOS",
            text="PCT_DESASSISTIDOS",
            color="GRUPO_TURNO",
            color_discrete_map={"Diurno": "#64748b", "Noturno": "#dc2626"},
        )
        fig_turno.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_turno.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            yaxis=dict(range=[0, 100], showgrid=False, title=""),
            xaxis=dict(title="", showgrid=False),
            height=320,
        )
        st.plotly_chart(fig_turno, use_container_width=True)

    with c_t2:
        st.markdown("**Validação Estatística (Teste Qui-Quadrado)**")
        st.markdown(
            """
            O teste do **Qui-Quadrado ($\chi^2$)** verifica se a diferença de atendimento entre diurno e noturno é pontual ou um **padrão estrutural da instituição**.
            """
        )
        if len(resumo_turno) == 2 and resumo_turno["TOTAL_COTISTAS"].sum() > 0:
            obs = resumo_turno[["ASSISTIDOS", "DESASSISTIDOS"]].values
            chi2, p_val, gl, _ = chi2_contingency(obs)

            st.markdown(
                f"""
                <div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-left: 4px solid #1e3a8a;">
                    <b>Estatística Qui-Quadrado:</b> {chi2:.2f}<br>
                    <b>p-valor:</b> {p_val:.4e}<br>
                    <b>Graus de Liberdade:</b> {gl}
                </div>
            """,
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if p_val < 0.05:
                st.error("结论: **Diferença Estatisticamente Significativa (p < 0,05).** Os estudantes do turno noturno possuem menor taxa proporcional de cobertura de auxílios.")
            else:
                st.info("结论: **Não há diferença estatística significativa** na taxa de atendimento entre os turnos no recorte selecionado.")

# -----------------------------------------------------------------------------
# TAB 3: EQUIDADE E PERFIL DEMOGRÁFICO
# -----------------------------------------------------------------------------
with tab_equidade:
    st.markdown("### Representatividade dos Beneficiários da PRAPE")
    st.caption("Comparativo entre a composição do corpo discente total da UFPB e a população efetivamente atendida pelos auxílios.")

    def calc_equidade(df, col_demo):
        tot = df.groupby(col_demo)["TOTAL_ALUNOS"].sum()
        ast = df[df["RECEBE_AUXILIO"] == 1].groupby(col_demo)["TOTAL_ALUNOS"].sum()
        df_c = pd.concat([tot, ast], axis=1, keys=["Total Campus", "Assistidos"]).fillna(0)
        df_c["% no Campus"] = (df_c["Total Campus"] / df_c["Total Campus"].sum() * 100).round(1)
        df_c["% nos Assistidos"] = (df_c["Assistidos"] / df_c["Assistidos"].sum() * 100).round(1)
        df_c["Diferença (p.p.)"] = (df_c["% nos Assistidos"] - df_c["% no Campus"]).round(1)
        return df_c.reset_index()

    ce1, ce2 = st.columns(2)

    with ce1:
        st.markdown("**Perfil Raça/Cor**")
        df_raca = calc_equidade(df_filtered, "RACA_DESCRICAO")

        fig_raca = px.bar(
            df_raca,
            x="RACA_DESCRICAO",
            y="Diferença (p.p.)",
            text="Diferença (p.p.)",
            color="Diferença (p.p.)",
            color_continuous_scale=["#dc2626", "#e2e8f0", "#1e3a8a"],
        )
        fig_raca.update_traces(texttemplate="%{text:+.1f} p.p.", textposition="outside")
        fig_raca.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            coloraxis_showscale=False,
            yaxis=dict(title="Diferença de Proporção (p.p.)", showgrid=True, gridcolor="#f1f5f9"),
            xaxis=dict(title=""),
            height=300,
        )
        st.plotly_chart(fig_raca, use_container_width=True)
        st.caption(" *Valores positivos indicam sobre-representação entre os bolsistas em relação ao campus.*")

    with ce2:
        st.markdown("**Perfil Sexo**")
        df_sexo = calc_equidade(df_filtered, "SEXO_DESCRICAO")

        fig_sexo = px.bar(
            df_sexo,
            x="SEXO_DESCRICAO",
            y="Diferença (p.p.)",
            text="Diferença (p.p.)",
            color="Diferença (p.p.)",
            color_continuous_scale=["#dc2626", "#e2e8f0", "#1e3a8a"],
        )
        fig_sexo.update_traces(texttemplate="%{text:+.1f} p.p.", textposition="outside")
        fig_sexo.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            coloraxis_showscale=False,
            yaxis=dict(title="Diferença de Proporção (p.p.)", showgrid=True, gridcolor="#f1f5f9"),
            xaxis=dict(title=""),
            height=300,
        )
        st.plotly_chart(fig_sexo, use_container_width=True)
        st.caption(" *Valores positivos indicam sobre-representação entre os bolsistas em relação ao campus.*")