import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import streamlit as st

def create_map(filtered_snv, filtered_oae, selected_point=None):
    """Create and return a Folium map with the filtered data."""
    # Mapeamento de cores
    color_map = {
        'Convênio Adm.Federal/Estadual': 'cyan',
        'Federal': 'red',
        'Distrital': 'cyan',
        'Estadual': 'cyan',
        'Municipal': 'cyan',
        'Concessão Federal': 'cyan',
        'Convênio Adm.Federal/Municipal': 'cyan'
    }
    
    # Definir listas para tooltips
    lista_snv = ['vl_br', 'sg_uf', 'vl_codigo', 'ds_coinc', 'ds_tipo_ad', 'ds_jurisdi','ds_superfi','ul']
    lista_oae = ['cod_sgo', 'descr_obra', 'tipo_obra','nota_sgo', 'origem_cadastro', 'uf', 'vl_codigo', 'ds_tipo_ad','ds_jurisdi', 'ul','tipo_conflito']

    # Mostrar progresso
    with st.spinner('Preparando mapa...'):
        m = filtered_snv.explore(
            column='ds_tipo_ad',
            cmap=list(color_map.values()),
            categories=list(color_map.keys()),
            style_kwds={"fillOpacity": 0.1},
            tooltip=lista_snv,
            categorical=True,
            name="Rodovias(SNV)",
            tiles="OpenStreetMap"
        )
    
    # Adicione este bloco para marcar o ponto selecionado
    if selected_point is not None:
        folium.Marker(
            location=[selected_point['latitude'], selected_point['longitude']],
            popup=f"OAE: {selected_point['cod_sgo']}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # Adicionar pontos OAE com tooltip personalizado
    for _, row in filtered_oae.iterrows():
        # Criar conteúdo HTML para o tooltip
        html = f"""
        <div style="font-family: Arial; font-size: 12px">
            <b>UF:</b> {row['uf']}<br>
            <b>Código SGO:</b> {row['cod_sgo']}<br>
            <b>Descrição:</b> {row['descr_obra']}<br>
            <b>Tipo Obra:</b> {row['tipo_obra']}<br>
            <b>Rodovia:</b> {row['br']}<br>
            <b>Nota SGO:</b> {row['nota_sgo']}<br>        

            <a href="{row['streetview_link']}" target="_blank" style="color: blue; text-decoration: underline;">
                Abrir no Street View
            </a>
        </div>
        """
        
        iframe = folium.IFrame(html, width=250, height=150)
        popup = folium.Popup(iframe, max_width=250)
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color='black',
            fill=True,
            fill_opacity=0.5,
            popup=popup
        ).add_to(m)
    
    # Adicionar diferentes tipos de mapas base
    folium.TileLayer('OpenStreetMap', name='Rodovias').add_to(m)
    folium.TileLayer('CartoDB.Positron', name='Light Mode').add_to(m)
    folium.TileLayer('CartoDB.DarkMatter', name='Dark Mode').add_to(m)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Satélite (Google)',
        max_zoom=20
    ).add_to(m)
    
    folium.LayerControl().add_to(m)

    return m

