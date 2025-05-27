import streamlit as st
from streamlit_folium import folium_static
from modules.data_loading import load_data
from modules.ui import setup_ui, display_filters, display_results
from modules.mapping import create_map
from modules.search import search_oae

def main():

    setup_ui()

    uploaded_files = display_filters()
    
    if len(uploaded_files) == 2:
        df_snv, df_oae = load_data(uploaded_files)     

        filtered_snv, filtered_oae = display_results(df_snv, df_oae)

        if not filtered_snv.empty or not filtered_oae.empty:
            m = create_map(filtered_snv, filtered_oae)
            folium_static(m, width=1400, height=800)
        else:
            st.warning("Nenhum dado encontrado com os filtros selecionados.")

if __name__ == "__main__":
    main()