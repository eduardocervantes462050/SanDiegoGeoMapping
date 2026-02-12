import pandas as pd
import requests
import time
import math

# --- CONFIG ---
API_KEY = "AIzaSyAZ_gyK1_PKKLPL4kyGn_Fx2QkXWIaVqqY"  # replace with your API key
INPUT_CSV = "data/addresses.csv"
OUTPUT_CSV = "output/addresses_geocoded.csv"

REF_LAT = 32.8774418  # e.g., San Diego center
REF_LNG = -117.2194511

# --- LOAD DATA ---
df = pd.read_csv(INPUT_CSV)

# Ensure 'Address' column exists
if "Address" not in df.columns:
    raise ValueError("CSV must have a column named 'Address'")


# --- FUNCTION TO GEOCODE ---
def geocode_address(address):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data["status"] == "OK":
            lat = data["results"][0]["geometry"]["location"]["lat"]
            lng = data["results"][0]["geometry"]["location"]["lng"]
            return pd.Series([lat, lng])
        else:
            print(f"Warning: {address} -> {data['status']}")
            return pd.Series([None, None])
    except Exception as e:
        print(f"Error: {address} -> {e}")
        return pd.Series([None, None])


# --- APPLY GEOCODING ---
df[["Latitude", "Longitude"]] = df["Address"].apply(lambda x: geocode_address(x))

# Optional: pause 0.1s to avoid rate limits
time.sleep(0.1)


# --- FUNCTION TO CALCULATE DISTANCE ---
def haversine(lat1, lon1, lat2, lon2):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Earth radius in km
    return c * r


# --- CALCULATE DISTANCE FROM REFERENCE POINT ---
df["Distance_km"] = df.apply(
    lambda row: (
        haversine(REF_LAT, REF_LNG, row["Latitude"], row["Longitude"])
        if pd.notnull(row["Latitude"])
        else None
    ),
    axis=1,
)


# --- SAVE OUTPUT ---
df.to_csv(OUTPUT_CSV, index=False)
print(f"Geocoding complete! Output saved to {OUTPUT_CSV}")
