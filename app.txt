import streamlit as st
import pandas as pd
import json
import os

# Configuração da página do aplicativo
st.set_page_config(
    page_title="Portal de Permutas - Rede Pública",
    page_icon="🏛️",
    layout="wide"
)

# Estilização visual limpa e profissional (CSS)
st.markdown("""
    <style>
        .main { background-color: #f8fafc; }
        .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }
        h1, h2, h3 { color: #1e3a8a; }
    </style>
""", unsafe_allow_html=True)

# Carregamento dos dados em cache
@st.cache_data
def carregar_dados():
    if os.path.exists('permutas_database.json'):
        with open('permutas_database.json', 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame()

df = carregar_dados()

# Título do Portal
st.title("🏛️ Portal Oficial de Consulta de Permutas")
st.markdown("Sistema integrado para cruzamento de demandas e ofertas de permuta da rede pública. Utilize os filtros abaixo para localizar servidores e contatos.")

if df.empty:
    st.error("⚠️ O arquivo de banco de dados 'permutas_database.json' não foi encontrado. Certifique-se de enviá-lo junto com o app.py.")
else:
    # Formatação de datas
    df['data_envio_limpa'] = df['data_envio'].astype(str).str.split('T').str[0]
    
    # Cartões de Métricas (KPIs) no topo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Cadastros", len(df))
    with col2:
        st.metric("Municípios de Origem", df['municipio_origem'].nunique())
    with col3:
        st.metric("Municípios Desejados", df['municipio_desejado_1'].nunique())

    st.markdown("---")

    # Painel de Filtros na Barra Lateral
    st.sidebar.header("🔍 Painel de Filtros")
    
    origens_opcoes = ["Todos"] + sorted(df['municipio_origem'].dropna().unique().tolist())
    origem_selecionada = st.sidebar.selectbox("Filtrar por Município de Origem", origens_opcoes)

    destinos_lista = list(set(df['municipio_desejado_1'].dropna().unique().tolist() + df['municipio_desejado_2'].dropna().unique().tolist()))
    destinos_opcoes = ["Todos"] + sorted([d for d in destinos_lista if d])
    destino_selecionado = st.sidebar.selectbox("Filtrar por Município Desejado", destinos_opcoes)

    busca_texto = st.sidebar.text_input("Pesquisa Livre (Nome ou Observação)", "")

    # Filtragem inteligente dos dados
    df_filtrado = df.copy()

    if origem_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado['municipio_origem'].str.strip() == origem_selecionada.strip()]

    if destino_selecionado != "Todos":
        df_filtrado = df_filtrado[
            (df_filtrado['municipio_desejado_1'].str.strip() == destino_selecionado.strip()) | 
            (df_filtrado['municipio_desejado_2'].str.strip() == destino_selecionado.strip())
        ]

    if busca_texto:
        termo = busca_texto.lower()
        df_filtrado = df_filtrado[
            df_filtrado['nome'].str.lower().str.contains(termo, na=False) | 
            df_filtrado['observacao'].str.lower().str.contains(termo, na=False)
        ]

    # Exibição dos Registros Localizados
    st.subheader(f"Servidores Encontrados ({len(df_filtrado)})")

    if df_filtrado.empty:
        st.info("Nenhum registro corresponde aos filtros selecionados.")
    else:
        tabela_exibicao = df_filtrado[[
            'data_envio_limpa', 'nome', 'rede', 'municipio_origem', 
            'municipio_desejado_1', 'municipio_desejado_2', 'observacao', 'telefone', 'email'
        ]].copy()
        
        tabela_exibicao.columns = [
            'Data', 'Nome', 'Rede', 'Origem', 
            'Destino 1', 'Destino 2', 'Observações', 'Telefone (Contato)', 'E-mail (Contato)'
        ]

        # Tabela interativa com colunas ajustáveis e contatos visíveis
        st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True)

        # Botão para download dos dados filtrados
        csv = tabela_exibicao.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar dados filtrados em CSV",
            data=csv,
            file_name="permutas_filtradas.csv",
            mime="text/csv"
        )