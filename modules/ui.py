import streamlit as st

def setup_ui():
    """Setup the Streamlit page configuration and title."""
    st.set_page_config(page_title="Mapa OAE", layout="wide")
    st.title("Mapa OAE")

def display_filters():
    """Display file upload filters and return uploaded files."""
    st.sidebar.header("Upload de Arquivos Obrigatórios")
    
    uploaded_files = []
    
    # Upload do arquivo Excel base_oae_colep
    uploaded_excel = st.sidebar.file_uploader(
        "Base OAE (Excel)", 
        type=['xlsx', 'xls'], 
        key='base_oae_colep'
    )
    
    # Upload do shapefile SNV (deve ser um zip)
    uploaded_snv = st.sidebar.file_uploader(
        "Shapefile SNV (ZIP)", 
        type=['zip'], 
        key='SNV_202501A'
    )
    
    if uploaded_excel:
        uploaded_files.append(uploaded_excel)
    if uploaded_snv:
        uploaded_files.append(uploaded_snv)
    
    return uploaded_files

def display_results(df_snv, df_oae):
    """Display filters and return filtered data."""
    with st.sidebar:
        st.header("Filtros")
        
        # Inicializar session state para filtros
        for key in ['uf', 'tipo_obra', 'br', 'conflitos', 'cod_sgo']:
            if key not in st.session_state:
                st.session_state[key] = []
        
        # 1. Filtro de UF
        uf_options = sorted(df_oae['uf'].dropna().unique().tolist()) if 'uf' in df_oae.columns else []
        if uf_options:
            selected_ufs = st.multiselect(
                "UF",
                options=uf_options,
                default=st.session_state.uf,
                key="uf_filter"
            )
            st.session_state.uf = selected_ufs
        else:
            st.warning("Coluna 'uf' não encontrada")
            selected_ufs = []
        
        # 2. Aplicar filtro de UF
        if selected_ufs:
            filtered_oae = df_oae[df_oae['uf'].isin(selected_ufs)].copy()
            filtered_snv = df_snv[df_snv['sg_uf'].isin(selected_ufs)].copy()
        else:
            filtered_oae = df_oae.copy()
            filtered_snv = df_snv.copy()
        
        # 3. Filtro de Tipo de Obra
        if 'tipo_obra' in filtered_oae.columns:
            tipo_options = ['Todos'] + sorted(filtered_oae['tipo_obra'].dropna().unique().tolist())
            selected_tipo = st.selectbox(
                "Tipo de Obra",
                options=tipo_options,
                index=0
            )
            
            if selected_tipo != 'Todos':
                filtered_oae = filtered_oae[filtered_oae['tipo_obra'] == selected_tipo]
        
        # 4. Filtro de Rodovia
        if 'br' in filtered_oae.columns:
            # Garantir que a coluna 'br' seja string
            filtered_oae['br'] = filtered_oae['br'].astype(str).str.zfill(3)
            
            br_options = ['Todos'] + sorted(filtered_oae['br'].dropna().unique().tolist())
            selected_br = st.selectbox(
                "Rodovia",
                options=br_options,
                index=0
            )
            
            if selected_br != 'Todos':
                filtered_oae = filtered_oae[filtered_oae['br'] == selected_br]
                if 'vl_br' in filtered_snv.columns:
                    filtered_snv = filtered_snv[filtered_snv['vl_br'].astype(str).str.zfill(3) == selected_br]
        
        # 5. Filtro de Conflitos (se a coluna existir)
        if 'tipo_conflito' in filtered_oae.columns:
            conflito_options = sorted(filtered_oae['tipo_conflito'].dropna().unique().tolist())
            selected_conflitos = st.multiselect(
                "Tipo de Conflito",
                options=conflito_options,
                default=st.session_state.conflitos
            )
            st.session_state.conflitos = selected_conflitos
            
            if selected_conflitos:
                filtered_oae = filtered_oae[filtered_oae['tipo_conflito'].isin(selected_conflitos)]
        
        # 6. Filtro por Código SGO
        if 'cod_sgo' in filtered_oae.columns:
            codigo_options = sorted(filtered_oae['cod_sgo'].astype(str).unique().tolist())
            selected_codigos = st.multiselect(
                "Código SGO",
                options=codigo_options,
                default=st.session_state.cod_sgo
            )
            st.session_state.cod_sgo = selected_codigos
            
            if selected_codigos:
                filtered_oae = filtered_oae[filtered_oae['cod_sgo'].astype(str).isin(selected_codigos)]
    
    # Mostrar estatísticas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rodovias visíveis", len(filtered_snv))
    with col2:
        st.metric("Obras visíveis", len(filtered_oae))
    
    return filtered_snv, filtered_oae
