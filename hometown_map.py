import pandas as pd
import folium
import requests
import time

# ------------------------------------------------------------
# Lab 6 Hometown Map
# This script reads my CSV file, geocodes each address with Mapbox,
# creates an interactive Folium map, and saves it as hometown_map.html.
# ------------------------------------------------------------

# I understand this part: these connect my Python script to Mapbox.
# The access token starts with pk. and comes from my Mapbox account.
access_token = "pk.eyJ1IjoidGVyaXF1aW50IiwiYSI6ImNtbHRycXdodDAzcGMzZ3Ewbmd0eWhhNTYifQ.OtLgrZN4opZ_FGt-EpqDbQ"

# My Mapbox username and custom style ID
mapbox_username = "teriquint"
mapbox_style_id = "cmlvuoat3004m01rigs6wex62"

# I understand this part: Folium needs an https tile URL, not the mapbox:// style URL.
tiles = f"https://api.mapbox.com/styles/v1/{mapbox_teriquint}/{cmlvuoat3004m01rigs6wex62}/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={access_token}"

# I understand this part: Python reads my CSV file of hometown locations.
locations = pd.read_csv("hometown_locations.csv")

# ------------------------------------------------------------
# Geocoding function
# ------------------------------------------------------------

# I understand the logic: this function sends an address to Mapbox
# and gets back latitude and longitude coordinates.
def geocode_address(address):
    geocode_url = "https://api.mapbox.com/search/geocode/v6/forward"

    params = {
        "q": address,
        "access_token": access_token,
        "limit": 1
    }

    response = requests.get(geocode_url, params=params)
    data = response.json()

    if "features" in data and len(data["features"]) > 0:
        coordinates = data["features"][0]["geometry"]["coordinates"]

        # Mapbox returns longitude first, then latitude.
        longitude = coordinates[0]
        latitude = coordinates[1]

        return latitude, longitude

    # If Mapbox cannot find the address, this returns empty values.
    return None, None


# ------------------------------------------------------------
# Geocode all locations
# ------------------------------------------------------------

# I understand this part: these lists store the coordinates for each location.
latitudes = []
longitudes = []

# I understand the logic: this loop geocodes every address in the CSV file.
for address in locations["Address"]:
    lat, lon = geocode_address(address)
    latitudes.append(lat)
    longitudes.append(lon)

    # This small pause helps avoid sending requests too quickly.
    time.sleep(0.2)

# Add the coordinates back into the dataframe.
locations["Latitude"] = latitudes
locations["Longitude"] = longitudes

# ------------------------------------------------------------
# Create the map
# ------------------------------------------------------------

# I understand this part: this centers the map between Lake Stevens and Seattle.
m = folium.Map(
    location=[47.75, -122.17],
    zoom_start=9,
    tiles=None
)

# I understand this part: this adds my custom Mapbox basemap.
folium.TileLayer(
    tiles=tiles,
    attr="Mapbox",
    name="Custom Mapbox Basemap",
    overlay=False,
    control=True
).add_to(m)

# ------------------------------------------------------------
# Marker colors by location type
# ------------------------------------------------------------

# I understand this part: each type of place gets a different marker color.
type_colors = {
    "Park": "green",
    "Community": "purple",
    "Cultural": "blue",
    "Recreation": "orange",
    "Landmark": "red",
    "Sports": "darkblue",
    "Restaurant": "cadetblue",
    "School": "darkpurple",
    "Historical": "darkred"
}

# ------------------------------------------------------------
# Add markers and pop-ups
# ------------------------------------------------------------

# I understand the logic: this loop adds every location from the CSV to the map.
for index, row in locations.iterrows():

    # Only add the marker if the location was geocoded correctly.
    if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):

        popup_html = f"""
        <div style="width:250px;">
            <h3>{row['Name']}</h3>
            <p><strong>Type:</strong> {row['Type']}</p>
            <p>{row['Description']}</p>
            <img src="{row['Image_URL']}" alt="{row['Name']}" style="width:100%; border-radius:8px;">
        </div>
        """

        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row["Name"],
            icon=folium.Icon(
                color=type_colors.get(row["Type"], "gray"),
                icon="info-sign"
            )
        ).add_to(m)

# Add a layer control in case I add more map layers later.
folium.LayerControl().add_to(m)

# ------------------------------------------------------------
# Save the final map
# ------------------------------------------------------------

# I understand this part: this saves the finished interactive map as an HTML file.
m.save("hometown_map.html")

print("Map created! Open hometown_map.html to view it.")