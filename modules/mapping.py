import folium
import geopandas as gpd
import streamlit as st

def create_map(filtered_snv, filtered_oae, selected_point=None):
    """Create and return a Folium map with the filtered data."""
    
    # Verificar se temos dados
    if filtered_snv.empty and filtered_oae.empty:
        st.warning("Nenhum dado para exibir no mapa")
        return folium.Map(location=[-15, -55], zoom_start=4)
    
    # Determinar centro do mapa
    if not filtered_oae.empty:
        avg_lat = filtered_oae['latitude'].mean()
        avg_lon = filtered_oae['longitude'].mean()
        center = [avg_lat, avg_lon]
        zoom_start = 8
    elif not filtered_snv.empty:
        center = [filtered_snv.geometry.centroid.y.mean(), filtered_snv.geometry.centroid.x.mean()]
        zoom_start = 6
    else:
        center = [-15, -55]
        zoom_start = 4
    
    # Criar mapa base
    m = folium.Map(location=center, zoom_start=zoom_start, control_scale=True)
    
    # Mapeamento de cores para tipos de administração
    color_map = {
        'Federal': 'red',
        'Estadual': 'blue',
        'Municipal': 'green',
        'Distrital': 'purple',
        'Concessão Federal': 'orange',
        'Convênio Adm.Federal/Estadual': 'cyan',
        'Convênio Adm.Federal/Municipal': 'pink'
    }
    
    # Adicionar rodovias (SNV)
    if not filtered_snv.empty:
        # Converter para GeoJSON
        geojson_data = filtered_snv.__geo_interface__
        
        # Adicionar ao mapa com estilo
        folium.GeoJson(
            geojson_data,
            name="Rodovias",
            style_function=lambda feature: {
                'color': color_map.get(feature['properties'].get('ds_tipo_ad', 'Federal'), 'gray'),
                'weight': 2,
                'opacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['vl_br', 'sg_uf', 'ds_tipo_ad', 'ds_jurisdi'],
                aliases=['BR:', 'UF:', 'Tipo:', 'Jurisdição:'],
                localize=True
            )
        ).add_to(m)
    
    # Adicionar pontos OAE
    if not filtered_oae.empty:
        # Criar cluster para melhor performance
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster(name="Obras").add_to(m)
        
        for _, row in filtered_oae.iterrows():
            # Criar popup HTML
            popup_html = f"""
            <div style="font-family: Arial; font-size: 12px; width: 250px;">
                <b>Código SGO:</b> {row.get('cod_sgo', 'N/A')}<br>
                <b>Descrição:</b> {row.get('descr_obra', 'N/A')}<br>
                <b>Tipo:</b> {row.get('tipo_obra', 'N/A')}<br>
                <b>UF:</b> {row.get('uf', 'N/A')}<br>
                <b>Conflito:</b> {row.get('tipo_conflito', 'N/A')}<br>
                <b>Nota SGO:</b> {row.get('nota_sgo', 'N/A')}<br>
                <a href="{row.get('streetview_link', '#')}" target="_blank" 
                   style="color: blue; text-decoration: underline;">
                   📍 Abrir Street View
                </a>
            </div>
            """
            
            popup = folium.Popup(popup_html, max_width=300)
            
            # Adicionar marcador
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                popup=popup,
                color='black',
                fill=True,
                fill_color='yellow',
                fill_opacity=0.8,
                weight=1
            ).add_to(marker_cluster)
    
    # Adicionar controles de camadas
    folium.TileLayer('OpenStreetMap', name='Mapa Padrão').add_to(m)
    folium.TileLayer('CartoDB.Positron', name='Modo Claro').add_to(m)
    folium.TileLayer('CartoDB.DarkMatter', name='Modo Escuro').add_to(m)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={{x}}&y={{y}}&z={{z}}',
        attr='Google',
        name='Satélite',
        overlay=False
    ).add_to(m)
    
    # Adicionar controle de camadas
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Adicionar fullscreen button
    from folium.plugins import Fullscreen
    Fullscreen().add_to(m)
    
    return m
