import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da Página
st.set_page_config(
    page_title="Portal de Permutas - Rede Pública",
    page_icon="🏛️",
    layout="wide"
)

# Estilização Visual (Padrão Executivo / Cartões em Grade)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .main { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
        .portal-header { border-bottom: 2px solid #3b82f6; padding-bottom: 15px; margin-bottom: 20px; }
        .portal-title { font-size: 24px; font-weight: 700; color: #1e3a8a; margin: 0 0 5px 0; }
        .portal-desc { font-size: 14px; color: #64748b; margin: 0; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; margin-top: 15px; }
        .card-item { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .card-name { font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 4px; }
        .card-badge { display: inline-block; background: #eff6ff; color: #1d4ed8; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; margin-bottom: 10px; }
        .card-route { font-size: 13px; background: #f1f5f9; padding: 8px 10px; border-radius: 6px; margin-bottom: 10px; color: #334155; }
        .card-obs { font-size: 12px; color: #475569; font-style: italic; margin-bottom: 12px; min-height: 30px; }
        .card-footer { border-top: 1px solid #f1f5f9; padding-top: 10px; font-size: 12px; color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

# Carregamento dos Dados
@st.cache_data
def carregar_dados():
    if os.path.exists('permutas_database.json'):
        with open('permutas_database.json', 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.error("⚠️ O arquivo 'permutas_database.json' não foi encontrado no repositório.")
else:
    # Cabeçalho Institucional
    st.markdown("""
        <div class="portal-header">
            <h2 class="portal-title">🏛️ Portal Oficial de Consulta de Permutas</h2>
            <p class="portal-desc">Sistema integrado para cruzamento de demandas e ofertas da rede pública.</p>
        </div>
    """, unsafe_allow_html=True)

    # Painel de Filtros na Barra Lateral (Sidebar)
    st.sidebar.header("🔍 Filtros de Pesquisa")
    
    origens_opcoes = ["Todos"] + sorted(df['municipio_origem'].dropna().astype(str).str.strip().unique().tolist())
    origem_sel = st.sidebar.selectbox("Município de Origem", origens_opcoes)

    destinos_lista = list(set(df['municipio_desejado_1'].dropna().astype(str).str.strip().unique().tolist() + 
                              df['municipio_desejado_2'].dropna().astype(str).str.strip().unique().tolist()))
    destinos_opcoes = ["Todos"] + sorted([d for d in destinos_lista if d and d != 'nan'])
    destino_sel = st.sidebar.selectbox("Município Desejado", destinos_opcoes)

    busca_txt = st.sidebar.text_input("Busca Livre (Nome ou Observação)", "")

    # Aplicar Filtros
    df_f = df.copy()
    if origem_sel != "Todos":
        df_f = df_f[df_f['municipio_origem'].astype(str).str.strip().str.lower() == origem_sel.strip().lower()]
    if destino_sel != "Todos":
        df_f = df_f[
            (df_f['municipio_desejado_1'].astype(str).str.strip().str.lower() == destino_sel.strip().lower()) | 
            (df_f['municipio_desejado_2'].astype(str).str.strip().str.lower() == destino_sel.strip().lower())
        ]
    if busca_txt:
        termo = busca_txt.lower()
        df_f = df_f[
            df_f['nome'].astype(str).str.lower().str.contains(termo, na=False) | 
            df_f['observacao'].astype(str).str.lower().str.contains(termo, na=False)
        ]

    # Cartões de Métricas (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("Cadastros Filtrados", len(df_f))
    col2.metric("Origens na Base", df['municipio_origem'].nunique())
    col3.metric("Destinos Desejados", df['municipio_desejado_1'].nunique())

    st.markdown("---")

    # Exibição em Grade de Cartões
    if df_f.empty:
        st.info("Nenhum servidor localizado com os critérios informados.")
    else:
        cards_html = '<div class="cards-grid">'
        for _, row in df_f.iterrows():
            nome = str(row.get('nome', 'Servidor'))
            rede = str(row.get('rede', 'Municipal'))
            origem_val = str(row.get('municipio_origem', ''))
            d1 = str(row.get('municipio_desejado_1', ''))
            d2 = str(row.get('municipio_desejado_2', ''))
            destinos_str = f"<b>{d1}</b>" + (f" / {d2}" if d2 and d2 != 'nan' else "")
            obs = str(row.get('observacao', ''))
            obs_str = obs if obs and obs != 'nan' else "Nenhuma observação informada."
            tel = str(row.get('telefone', ''))
            email = str(row.get('email', ''))
            
            cards_html += f"""
            <div class="card-item">
                <div class="card-name">{nome}</div>
                <div class="card-badge">Rede: {rede}</div>
                <div class="card-route">
                    📍 <b>Origem:</b> {origem_val}<br>
                    🎯 <b>Deseja:</b> {destinos_str}
                </div>
                <div class="card-obs">"{obs_str}"</div>
                <div class="card-footer">
                    📞 <b>Tel:</b> {tel}<br>
                    📧 <b>E-mail:</b> {email}
                </div>
            </div>
            """
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown("---")

    # Gráficos Estatísticos de Barras Horizontais
    st.subheader("📊 Análise Estatística de Demanda por Município")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    sns.set_theme(style="whitegrid")
    
    # 1. Gráfico de Destinos Mais Desejados
    todos_destinos = pd.concat([df_f['municipio_desejado_1'], df_f['municipio_desejado_2']]).dropna()
    todos_destinos = todos_destinos[todos_destinos.astype(str).str.strip() != '']
    top_destinos = todos_destinos.value_counts().head(6)
    
    if not top_destinos.empty:
        sns.barplot(x=top_destinos.values, y=top_destinos.index, ax=axes[0], palette="Blues_r")
        axes[0].set_title("Top Municipios Mais Desejados (Destinos)", fontsize=12, fontweight='bold', color="#1e3a8a")
        axes[0].set_xlabel("Numero de Interesses", fontsize=10)
        axes[0].set_ylabel("Municipio", fontsize=10)
        for p in axes[0].patches:
            axes[0].annotate(f"{int(p.get_width())}", (p.get_width() + 0.2, p.get_y() + p.get_height()/2.),
                             va='center', fontsize=9, color='#1e293b', fontweight='bold')

    # 2. Gráfico de Demanda de Saída (Origem)
    top_origens = df_f['municipio_origem'].value_counts().head(6)
    if not top_origens.empty:
        sns.barplot(x=top_origens.values, y=top_origens.index, ax=axes[1], palette="crest")
        axes[1].set_title("Top Municipios com Maior Demanda de Saida (Origem)", fontsize=12, fontweight='bold', color="#1e3a8a")
        axes[1].set_xlabel("Numero de Servidores", fontsize=10)
        axes[1].set_ylabel("Municipio", fontsize=10)
        for p in axes[1].patches:
            axes[1].annotate(f"{int(p.get_width())}", (p.get_width() + 0.2, p.get_y() + p.get_height()/2.),
                             va='center', fontsize=9, color='#1e293b', fontweight='bold')

    plt.tight_layout()
    st.pyplot(fig)
