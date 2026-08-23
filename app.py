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
    st.title("🏛️ Portal Oficial de Consulta de Permutas")
    st.markdown("Sistema integrado para cruzamento de demandas e ofertas de permuta da rede pública.")
    st.markdown("---")

    # Painel de Filtros na Barra Lateral
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

    # Exibição em Cartões Organizados por Colunas Nativas
    if df_f.empty:
        st.info("Nenhum servidor localizado com os critérios informados.")
    else:
        st.subheader("📋 Servidores Encontrados")
        
        # Criar linhas com 3 colunas de cartões
        for i in range(0, len(df_f), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(df_f):
                    row = df_f.iloc[i + j]
                    with cols[j]:
                        nome = str(row.get('nome', 'Servidor'))
                        rede = str(row.get('rede', 'Municipal'))
                        origem_val = str(row.get('municipio_origem', ''))
                        d1 = str(row.get('municipio_desejado_1', ''))
                        d2 = str(row.get('municipio_desejado_2', ''))
                        destinos_str = f"**{d1}**" + (f" / {d2}" if d2 and d2 != 'nan' else "")
                        obs = str(row.get('observacao', ''))
                        obs_str = f"*{obs}*" if obs and obs != 'nan' else "*Nenhuma observação informada.*"
                        tel = str(row.get('telefone', ''))
                        email = str(row.get('email', ''))
                        
                        # Bloco visual limpo para cada cartão
                        st.markdown(f"""
                        **{nome}**  
                        `Rede: {rede}`  
                        📍 **Origem:** {origem_val}  
                        🎯 **Deseja:** {destinos_str}  
                        {obs_str}  
                        📞 **Tel:** {tel}  
                        📧 **E-mail:** {email}
                        """, unsafe_allow_html=True)
                        st.markdown("---")

    # Gráficos Estatísticos
    st.subheader("📊 Análise Estatística de Demanda por Município")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    sns.set_theme(style="whitegrid")
    
    # 1. Gráfico de Destinos Mais Desejados
    todos_destinos = pd.concat([df_f['municipio_desejado_1'], df_f['municipio_desejado_2']]).dropna()
    todos_destinos = todos_destinos[todos_destinos.astype(str).str.strip() != '']
    top_destinos = todos_destinos.value_counts().head(6)
    
    if not top_destinos.empty:
        sns.barplot(x=top_destinos.values, y=top_destinos.index, ax=axes[0], palette="Blues_r")
        axes[0].set_title("Top Municípios Mais Desejados (Destinos)", fontsize=12, fontweight='bold', color="#1e3a8a")
        axes[0].set_xlabel("Número de Interesses", fontsize=10)
        axes[0].set_ylabel("Município", fontsize=10)
        for p in axes[0].patches:
            axes[0].annotate(f"{int(p.get_width())}", (p.get_width() + 0.2, p.get_y() + p.get_height()/2.),
                             va='center', fontsize=9, color='#1e293b', fontweight='bold')

    # 2. Gráfico de Demanda de Saída (Origem)
    top_origens = df_f['municipio_origem'].value_counts().head(6)
    if not top_origens.empty:
        sns.barplot(x=top_origens.values, y=top_origens.index, ax=axes[1], palette="crest")
        axes[1].set_title("Top Municípios com Maior Demanda de Saída (Origem)", fontsize=12, fontweight='bold', color="#1e3a8a")
        axes[1].set_xlabel("Número de Servidores", fontsize=10)
        axes[1].set_ylabel("Município", fontsize=10)
        for p in axes[1].patches:
            axes[1].annotate(f"{int(p.get_width())}", (p.get_width() + 0.2, p.get_y() + p.get_height()/2.),
                             va='center', fontsize=9, color='#1e293b', fontweight='bold')

    plt.tight_layout()
    st.pyplot(fig)
