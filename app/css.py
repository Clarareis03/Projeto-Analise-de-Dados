# css.py
import streamlit as st


def load_css():
    """Injeta os estilos visuais executivos em tom Azul Executivo e Cinza Neutro."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Fundo em Cinza Claro Executivo */
    .stApp {
        background-color: #f8fafc;
    }

    /* Sidebar Clean */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }

    /* Cards Estilo Executivo */
    .saas-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
    }

    .saas-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .saas-value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.1;
        margin-bottom: 6px;
    }

    .saas-sub {
        font-size: 0.825rem;
        color: #64748b;
    }

    /* Badges Executivas em Azul / Neutro */
    .badge-default {
        background-color: #f1f5f9;
        color: #475569;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid #cbd5e1;
    }

    .badge-primary {
        background-color: #eff6ff;
        color: #1e3a8a;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid #bfdbfe;
    }

    /* Abas Corporativas com Indicador em Azul Executivo */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #cbd5e1;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: transparent;
        border-radius: 6px 6px 0 0;
        color: #64748b;
        font-weight: 600;
        font-size: 0.875rem;
        padding: 0px 18px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        border: 1px solid #cbd5e1;
        border-bottom: 3px solid #1e3a8a !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_metric_card(title, value, subtext, badge_text="", badge_type="default", value_color="#0f172a"):
    """Gera cartões KPI no padrão executivo."""
    badge_html = f'<span class="badge-{badge_type}">{badge_text}</span>' if badge_text else ""
    html = f"""
    <div class="saas-card">
        <div class="saas-title">
            <span>{title}</span>
            {badge_html}
        </div>
        <div class="saas-value" style="color: {value_color};">{value}</div>
        <div class="saas-sub">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)