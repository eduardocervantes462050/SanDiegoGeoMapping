import folium
import pandas as pd
import geopandas as gpd

# --- LOAD ZIP CODE SHAPEFILE ---
zip_shapefile = "data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp"
gdf_zips = gpd.read_file(zip_shapefile, usecols=["ZCTA5CE20", "geometry"]).to_crs(
    epsg=4326
)
gdf_zips["ZCTA5CE20"] = gdf_zips["ZCTA5CE20"].astype(str)

# Filter San Diego ZIPs
sd_zips = gdf_zips[gdf_zips["ZCTA5CE20"].str.startswith("92")]

# --- LOAD ADDRESSES ---
df_addresses = pd.read_csv("output/addresses_geocoded.csv")

# --- CREATE MAP ---
m = folium.Map(location=[32.7157, -117.1611], zoom_start=11)  # San Diego center

# Add ZIP polygons with popup showing ZIP code
folium.GeoJson(
    sd_zips,
    name="San Diego ZIPs",
    tooltip=folium.GeoJsonTooltip(
        fields=["ZCTA5CE20"],  # Column to display
        aliases=["ZIP Code:"],  # Label shown before value
        localize=True,
    ),
    style_function=lambda x: {
        "fillColor": "#ffff00",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.2,
    },
).add_to(m)

# Add address pins
for idx, row in df_addresses.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=row["Address"],
        icon=folium.Icon(color="red"),
    ).add_to(m)

# Save interactive map to HTML
m.save("output/san_diego_map.html")
print("Interactive map saved as output/san_diego_map.html")
