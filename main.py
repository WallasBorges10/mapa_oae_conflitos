def main():

    setup_ui()

    uploaded_files = display_filters()
    
    if len(uploaded_files) == 2:
        df_snv, df_oae = load_data(uploaded_files)

        # 🔹 PADRONIZAÇÃO GLOBAL DE COLUNAS (INSERIR AQUI)
        df_snv.columns = (
            df_snv.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        df_oae.columns = (
            df_oae.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        filtered_snv, filtered_oae = display_results(df_snv, df_oae)

        if not filtered_snv.empty or not filtered_oae.empty:
            m = create_map(filtered_snv, filtered_oae)
            folium_static(m, width=1400, height=800)
        else:
            st.warning("Nenhum dado encontrado com os filtros selecionados.")
