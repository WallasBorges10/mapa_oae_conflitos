import streamlit as st
from streamlit_folium import folium_static
from streamlit import set_page_config

def setup_ui():
    """Setup the Streamlit page configuration and title."""
    st.set_page_config(page_title="Mapa OAE", layout="wide")
    st.title("Mapa OAE")

def display_filters():
    """Display file upload filters and return uploaded files."""
    st.sidebar.header("Upload de Arquivos Obrigatórios")
    
    uploaded_files = {}
    
    # Upload do arquivo Excel base_oae_colep
    uploaded_excel = st.sidebar.file_uploader("Base OAE (Excel)", type=['xlsx'], key='base_oae_colep')
    if uploaded_excel is not None:
        uploaded_files['base_oae_colep'] = uploaded_excel

    # Upload do shapefile SNV (deve ser um zip)
    uploaded_snv = st.sidebar.file_uploader("Shapefile SNV (ZIP contendo .shp, .dbf, etc)", type=['zip'], key='SNV_202501A')
    if uploaded_snv is not None:
        uploaded_files['SNV_202501A'] = uploaded_snv

    # Mostrar mensagem principal se algum arquivo estiver faltando
    if len(uploaded_files) < 2:
        st.warning("Por favor, carregue todos os arquivos necessários para continuar.")
        
    return uploaded_files

def display_results(df_snv, df_oae):
    """Display filters and return filtered data."""
    # Sidebar para filtros
    with st.sidebar:
        st.header("Filtros")
        
        # 1. Filtro de UF (agora multiselect)
        uf_options = sorted(df_oae['uf'].dropna().unique().tolist())
        selected_ufs = st.multiselect(
            "UF",
            uf_options,
            key="uf",
            default=['MA']  # Mantém a seleção ao atualizar
        )
        
        # 2. Filtro de Tipo de Obra (depende da(s) UF(s) selecionada(s))
        df_filtered_uf = df_oae if not selected_ufs else df_oae[df_oae['uf'].isin(selected_ufs)]
        
        tipo_obra_options = ['Todos'] + sorted(df_filtered_uf['tipo_obra'].dropna().unique().tolist())
        selected_tipo_obra = st.selectbox(
            "Tipo de Obra",
            tipo_obra_options,
            key="tipo_obra",
            index=0 if 'tipo_obra' not in st.session_state else tipo_obra_options.index(st.session_state.tipo_obra) if st.session_state.tipo_obra in tipo_obra_options else 0
        )
        
        # 3. Filtro de Rodovia (depende da(s) UF(s) e Tipo de Obra selecionados)
        df_filtered_tipo = df_filtered_uf if selected_tipo_obra == 'Todos' else df_filtered_uf[df_filtered_uf['tipo_obra'] == selected_tipo_obra]
        
        # Garante que a coluna 'br' em df_oae e 'vl_br' em df_snv sejam comparáveis (mesmo formato)
        df_filtered_tipo['br'] = df_filtered_tipo['br'].astype(str).str.zfill(3)
        br_options = ['Todos'] + sorted(df_filtered_tipo['br'].dropna().unique().tolist())
        selected_br = st.selectbox(
            "Rodovia",
            br_options,
            key="br",
            index=0 if 'br' not in st.session_state else br_options.index(st.session_state.br) if st.session_state.br in br_options else 0
        )
        
        # 4. Filtro de Conflitos (depende de UF(s), Tipo de Obra e Rodovia selecionados)
        df_filtered_br = (
            df_filtered_tipo
            if selected_br == 'Todos'
            else df_filtered_tipo[df_filtered_tipo['br'] == selected_br]
        )
        
        # 🔹 inicialização segura
        selected_conflitos = []
        
        if 'conflitos' in df_filtered_br.columns:
            conflitos_options = sorted(
                df_filtered_br['conflitos']
                .dropna()
                .unique()
                .tolist()
            )
        
            selected_conflitos = st.multiselect(
                "Conflitos",
                conflitos_options,
                key="conflitos"
            )
        else:
            st.warning("Coluna 'conflitos' não encontrada no dataframe")
        
        # 5. Aplicação do filtro
        if selected_conflitos:
            df_filtered_conflitos = df_filtered_br[
                df_filtered_br['conflitos'].isin(selected_conflitos)
            ]
        else:
            df_filtered_conflitos = df_filtered_br
        
        codigo_options = sorted(
            df_filtered_conflitos['cod_sgo']
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        
        selected_codigos = st.multiselect(
            "Código",
            codigo_options,
            key="cod_sgo"
        )


    # Aplicar filtros finais aos dataframes
    filtered_oae = df_oae.copy()
    filtered_snv = df_snv.copy()

    # Aplicar filtro de UF (multiselect)
    if selected_ufs:
        filtered_oae = filtered_oae[filtered_oae['uf'].isin(selected_ufs)]
        filtered_snv = filtered_snv[filtered_snv['sg_uf'].isin(selected_ufs)]

    # Aplicar filtro de Tipo de Obra
    if selected_tipo_obra != 'Todos':
        filtered_oae = filtered_oae[filtered_oae['tipo_obra'] == selected_tipo_obra]

    # Aplicar filtro de Rodovia (simultâneo em df_oae['br'] e df_snv['vl_br'])
    if selected_br != 'Todos':
        br_selecionado = selected_br.zfill(3)  # Garante formato '001' em vez de '1'
        filtered_oae = filtered_oae[filtered_oae['br'].astype(str).str.zfill(3) == br_selecionado]
        filtered_snv = filtered_snv[filtered_snv['vl_br'].astype(str).str.zfill(3) == br_selecionado]

    # Aplicar filtro de Conflitos (se existir e selecionado)
    if 'conflitos' in df_oae.columns and selected_conflitos:
        filtered_oae = filtered_oae[filtered_oae['conflitos'].isin(selected_conflitos)]

    # Aplicar filtro de Código (com filtro em df_snv['vl_codigo'])
    if selected_codigos:
        # Filtra df_oae pelos códigos selecionados
        filtered_oae = filtered_oae[filtered_oae['cod_sgo'].astype(str).isin(selected_codigos)]
        
        # Extrai todos os vl_codigo associados aos códigos selecionados (separados por ";")
        vl_codigos_associados = set()
        for codigo in selected_codigos:
            vl_codigos_obra = filtered_oae[filtered_oae['cod_sgo'].astype(str) == codigo]['vl_codigo'].str.split(';').explode().dropna().unique()
            vl_codigos_associados.update(vl_codigos_obra)
        
        # Filtra df_snv onde vl_codigo está na lista de associados
        if vl_codigos_associados:
            filtered_snv = filtered_snv[filtered_snv['vl_codigo'].isin(vl_codigos_associados)]

    # Mostrar contagem de registros
    col1, col2 = st.columns(2)
    col1.write(f"SNV visíveis: {len(filtered_snv)}")
    col2.write(f"Obras de Arte Especiais visíveis: {len(filtered_oae)}")
    

    return filtered_snv, filtered_oae
