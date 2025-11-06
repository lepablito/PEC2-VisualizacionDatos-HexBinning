import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium

# Carga de datos y preprocesamiento basico
df: pd.DataFrame = pd.read_csv(r"data\uber-raw-data-jul14.csv")
df.columns = [c.strip().replace(" ", "_").replace("/", "_").lower() for c in df.columns]
df = df.dropna(subset=["lat","lon"])

# Limites y centro para luego configurar el mapa y la imagen overlay
min_lat, max_lat = df["lat"].min(), df["lat"].max()
min_lon, max_lon = df["lon"].min(), df["lon"].max()
center = [(min_lat + max_lat) / 2.0, (min_lon + max_lon) / 2.0]

# Generate a transparent PNG with the hexbin (log-scaled) using the data extent as image extent,
# so it lines up with lat/lon when used as an ImageOverlay.

# Generamos el PNG transparente con hexbin (escala logaritmica)
fig = plt.figure(figsize=(8, 8), dpi=200)
ax = plt.axes()
# Fondo transparente (png)
fig.patch.set_alpha(0.0)
ax.set_facecolor((0,0,0,0))
# Creamos el hexbin
hb = ax.hexbin(df["lon"], df["lat"], gridsize=100, mincnt=1, bins="log")
ax.set_xlim(min_lon, max_lon)
ax.set_ylim(min_lat, max_lat)
ax.axis('off')
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Save transparent overlay image
overlay_path = r"data\hexbin.png"
plt.savefig(overlay_path, transparent=True)
plt.close(fig)

# Creamos el mapa folium centrado en los datos
m = folium.Map(location=center, zoom_start=11, tiles="OpenStreetMap", control_scale=True)

# Add the hexbin image as an overlay aligned to the data bounds
image_overlay = folium.raster_layers.ImageOverlay(
    name="Hexbin (log counts)",
    image=overlay_path,
    bounds=[[min_lat, min_lon], [max_lat, max_lon]],
    opacity=0.65,
    interactive=False,
    cross_origin=False,
    zindex=2,
)
image_overlay.add_to(m)

# Añadir título al mapa
title_html = '''
             <div style="position: fixed; 
                         top: 10px; left: 50px; width: 500px; height: 90px; 
                         background-color: white; border:2px solid grey; z-index:9999; 
                         font-size:16px; padding: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
             <h4 style="margin-top:0;">Viajes de Uber en Nueva York - Julio 2014</h4>
             <p style="margin:0; font-size:12px;">Densidad de recogidas usando Hexagonal Binning (escala logarítmica)</p>
             </div>
             '''
m.get_root().html.add_child(folium.Element(title_html))

# Añadir leyenda explicativa
legend_html = '''
             <div style="position: fixed; 
                         bottom: 50px; left: 50px; width: 220px; 
                         background-color: white; border:2px solid grey; z-index:9999; 
                         font-size:14px; padding: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
             <p style="margin-top:0; font-weight: bold;">Leyenda</p>
             <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 20px; height: 20px; background: linear-gradient(to right, #440154, #31688e, #35b779, #fde724); margin-right: 10px;"></div>
                <span style="font-size: 11px;">Menos → Más viajes</span>
             </div>
             <p style="margin: 5px 0; font-size: 11px;">• Colores más cálidos = mayor concentración</p>
             </div>
             '''
m.get_root().html.add_child(folium.Element(legend_html))

# Añadir control de capas para poder activar/desactivar el overlay
folium.LayerControl().add_to(m)

# Creamos el HTML del mapa con overlay
html_path = r"root/hexbinning-interactive.html"
m.save(html_path)

(overlay_path, html_path)