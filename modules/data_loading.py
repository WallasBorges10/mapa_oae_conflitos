import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import zipfile
import tempfile
import os
import streamlit as st

@st.cache_data
def load_data(base_oae_file, snv_file):
    """Load and process the input files."""
    try:
        # 1. Carregar dados OAE do Excel
        df_oae = pd.read_excel(base_oae_file)
        
        # 2. Processar shapefile SNV
        with zipfile.ZipFile(snv_file, 'r') as z:
            # Encontrar arquivo .shp
            shp_files = [f for f in z.namelist() if f.endswith('.shp')]
            if not shp_files:
                st.error("Nenhum arquivo .shp encontrado no ZIP")
                return None, None
            
            # Extrair para diretório temporário
            temp_dir = tempfile.mkdtemp()
            z.extractall(temp_dir)
            
            # Carregar shapefile
            df_snv = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
        
        # 3. Processar dados OAE
        # Verificar se colunas de coordenadas existem
        if 'latitude' in df_oae.columns and 'longitude' in df_oae.columns:
            # Criar geometria para OAE
            geometry = [Point(xy) for xy in zip(df_oae['longitude'], df_oae['latitude'])]
            df_oae = gpd.GeoDataFrame(df_oae, geometry=geometry, crs="EPSG:4326")
        else:
            st.error("Colunas 'latitude' e/ou 'longitude' não encontradas no arquivo OAE")
            return None, None
        
        # 4. Garantir mesmo CRS (WGS84 - EPSG:4326)
        df_snv = df_snv.to_crs(epsg=4326)
        df_oae = df_oae.to_crs(epsg=4326)
        
        # 5. Criar link do Street View
        df_oae['streetview_link'] = df_oae.apply(
            lambda row: f"https://www.google.com/maps?q=&layer=c&cbll={row['latitude']},{row['longitude']}&cbp=12,90,0,0,5", 
            axis=1
        )
        
        # 6. Padronizar formatos
        if 'cod_sgo' in df_oae.columns:
            df_oae['cod_sgo'] = df_oae['cod_sgo'].astype(str).str.zfill(6)
        
        # 7. Simplificar geometrias do SNV para melhor performance
        df_snv['geometry'] = df_snv['geometry'].simplify(tolerance=0.001, preserve_topology=True)
        
        st.success(f"Dados carregados: {len(df_snv)} rodovias, {len(df_oae)} obras")
        return df_snv, df_oae
    
    except Exception as e:
        st.error(f"Erro ao processar os arquivos: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None, None
