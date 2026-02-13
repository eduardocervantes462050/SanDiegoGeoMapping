import folium
import pandas as pd
import geopandas as gpd
import branca.colormap as cm

# -----------------------------
# LOAD ZIP SHAPEFILE
# -----------------------------
zip_shapefile = "data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp"

gdf_zips = gpd.read_file(zip_shapefile).to_crs(epsg=4326)
gdf_zips = gdf_zips[["ZCTA5CE20", "geometry"]]

gdf_zips["ZCTA5CE20"] = gdf_zips["ZCTA5CE20"].astype(str)
sd_zips = gdf_zips[gdf_zips["ZCTA5CE20"].str.startswith("92")]

# -----------------------------
# LOAD ADDRESS DATA
# -----------------------------
df = pd.read_csv("output/addresses_geocoded.csv")

df["Price per sqf"] = pd.to_numeric(df["Price per sqf"], errors="coerce")
df["Distance_km"] = pd.to_numeric(df["Distance_km"], errors="coerce")

# Extract ZIP from address if needed
df["ZIP"] = df["Address"].str.extract(r"(\d{5})")

# -----------------------------
# CREATE MAP
# -----------------------------
m = folium.Map(location=[32.7157, -117.1611], zoom_start=11, tiles="cartodbpositron")

# -----------------------------
# CREATE COLOR SCALE
# -----------------------------
vmin = df["Price per sqf"].min()
vmax = df["Price per sqf"].max()

colormap = cm.LinearColormap(colors=["green", "yellow", "red"], vmin=vmin, vmax=vmax)

colormap.caption = "Price per Sqft"
colormap.add_to(m)

# -----------------------------
# SHADE ZIP CODES BY AVG PRICE
# -----------------------------
zip_avg = df.groupby("ZIP")["Price per sqf"].mean().reset_index()
zip_avg.columns = ["ZCTA5CE20", "AvgPrice"]

sd_zips = sd_zips.merge(zip_avg, on="ZCTA5CE20", how="left")


def style_zip(feature):
    value = feature["properties"]["AvgPrice"]
    return {
        "fillColor": colormap(value) if value else "#cccccc",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.4,
    }


folium.GeoJson(
    sd_zips,
    name="ZIP Avg Price",
    style_function=style_zip,
    tooltip=folium.GeoJsonTooltip(
        fields=["ZCTA5CE20", "AvgPrice"],
        aliases=["ZIP:", "Avg Price per Sqft:"],
    ),
).add_to(m)

# -----------------------------
# ADD PROPERTY MARKERS
# -----------------------------
marker_layer = folium.FeatureGroup(name="Properties")

for _, row in df.iterrows():

    if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):

        popup_text = f"""
        <b>Address:</b> {row['Address']}<br>
        <b>Price per Sqft:</b> ${row['Price per sqf']:.2f}<br>
        <b>Distance:</b> {row['Distance_km']:.2f} km
        """

        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=4 + (row["Price per sqf"] / vmax) * 8,  # Size scales with price
            color=colormap(row["Price per sqf"]),
            fill=True,
            fill_color=colormap(row["Price per sqf"]),
            fill_opacity=0.85,
            popup=popup_text,
        ).add_to(marker_layer)

marker_layer.add_to(m)

# -----------------------------
# ADD LAYER CONTROL
# -----------------------------
folium.LayerControl().add_to(m)

# -----------------------------
# SAVE MAP
# -----------------------------
m.save("output/san_diego_map.html")
print("Professional interactive map saved.")
