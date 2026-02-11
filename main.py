import streamlit as st
from streamlit_folium import folium_static
from modules.data_loading import load_data
from modules.ui import setup_ui, display_filters, display_results
from modules.mapping import create_map
from modules.search import search_oae

def main():
    setup_ui()
    
    # Obter os arquivos carregados
    uploaded_files = display_filters()
    
    # Verificar se temos os dois arquivos necessários
    if uploaded_files and len(uploaded_files) == 2:
        # Extrair os arquivos específicos
        base_oae_file = uploaded_files[0] if "base_oae" in uploaded_files[0].name else uploaded_files[1]
        snv_file = uploaded_files[1] if "SNV" in uploaded_files[1].name else uploaded_files[0]
        
        # Carregar dados
        df_snv, df_oae = load_data(base_oae_file, snv_file)
        
        if df_snv is not None and df_oae is not None:
            # Aplicar filtros
            filtered_snv, filtered_oae = display_results(df_snv, df_oae)
            
            # Verificar se há dados para exibir
            if not filtered_snv.empty or not filtered_oae.empty:
                m = create_map(filtered_snv, filtered_oae)
                folium_static(m, width=1400, height=800)
            else:
                st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.info("Aguardando upload dos arquivos necessários...")

if __name__ == "__main__":
    main()
