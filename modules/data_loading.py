import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import zipfile
import tempfile
import os
import streamlit as st

@st.cache_data
def load_data(uploaded_files):
    """Load and process the input files."""
    # Verificar se os arquivos necessários foram carregados
    required_files = ['base_oae_colep', 'SNV_202501A']
    for file in required_files:
        if file not in uploaded_files:
            st.error(f"Arquivo obrigatório não encontrado: {file}")
            st.stop()
    
    try:
        # 1. Carregando os dados dos arquivos enviados
        df_oae = pd.read_excel(uploaded_files['base_oae_colep'])
        
        # Processar o shapefile SNV
        with zipfile.ZipFile(uploaded_files['SNV_202501A'], 'r') as z:
            # Encontrar o arquivo .shp dentro do ZIP
            shp_file = [f for f in z.namelist() if f.endswith('.shp')][0]
            # Extrair todos os arquivos para um diretório temporário
            temp_dir = tempfile.mkdtemp()
            z.extractall(temp_dir)
            # Carregar o shapefile usando o caminho completo
            df_snv = gpd.read_file(os.path.join(temp_dir, shp_file))
        
        # Converter para GeoDataFrame se necessário
        if not isinstance(df_oae, gpd.GeoDataFrame):
            df_oae['geometry'] = df_oae.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
            df_oae = gpd.GeoDataFrame(df_oae, geometry='geometry', crs=df_snv.crs)
        
        # Criar coluna streetview_link
        df_oae['streetview_link'] = df_oae.apply(
            lambda row: f"https://www.google.com/maps?q=&layer=c&cbll={row['latitude']},{row['longitude']}", 
            axis=1
        )
        
        # Converter para o mesmo CRS
        df_snv = df_snv.to_crs(epsg=5880)
        df_oae = df_oae.to_crs(epsg=5880)

        df_snv['geometry'] = df_snv['geometry'].simplify(tolerance=10, preserve_topology=True)
        df_oae['cod_sgo'] = df_oae['cod_sgo'].astype(str).str.zfill(6)

        return df_snv, df_oae
    
    except Exception as e:
        st.error(f"Erro ao processar os arquivos: {str(e)}")
        st.stop()