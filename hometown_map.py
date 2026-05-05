import pandas as pd
import folium
import requests
import time

# I understand this part: these are my Mapbox settings.
# I need to replace these with my own Mapbox token and style information.
access_token = "pk.eyJ1IjoidGVyaXF1aW50IiwiYSI6ImNtbHRycXdodDAzcGMzZ3Ewbmd0eWhhNTYifQ.OtLgrZN4opZ_FGt-EpqDbQ"
mapbox_username = "teriquint"
mapbox_style_id = "mapbox://styles/teriquint/cmm0v6y2m008e01s27o31772w"

# I understand this part: Python reads my CSV file so it can use the locations.
locations = pd.read_csv("hometown_locations.csv")

# I understand the logic: this function sends an address to Mapbox and gets back latitude and longitude.
def geocode_address(address):
    url = "https://api.mapbox.com/search/geocode/v6/forward"
    params = {
        "q": address,
        "access_token": access_token,
        "limit": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "features" in data and len(data["features"]) > 0:
        coordinates = data["features"][0]["geometry"]["coordinates"]
        longitude = coordinates[0]
        latitude = coordinates[1]
        return latitude, longitude

    return None, None

# I understand this part: these lists will store the latitude and longitude for each location.
latitudes = []
longitudes = []

# I understand the logic: this loop geocodes every address in my CSV.
for address in locations["Address"]:
    lat, lon = geocode_address(address)
    latitudes.append(lat)
    longitudes.append(lon)
    time.sleep(0.2)

locations["Latitude"] = latitudes
locations["Longitude"] = longitudes

# I understand this part: this creates the starting map view around Lake Stevens and Seattle.
m = folium.Map(
    location=[47.75, -122.17],
    zoom_start=9,
    tiles=None
)

# I understand this part: this connects my custom Mapbox basemap to Folium.
tiles = f"https://api.mapbox.com/styles/v1/{mapbox_username}/{mapbox_style_id}/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={access_token}"

folium.TileLayer(
    tiles=tiles,
    attr="Mapbox",
    name="Custom Mapbox Basemap",
    overlay=False,
    control=True
).add_to(m)

# I understand this part: each location type gets a different marker color.
type_colors = {
    "Park": "green",
    "Community": "purple",
    "Cultural": "blue",
    "Recreation": "orange",
    "Landmark": "red",
    "Sports": "darkblue"
}

# I understand the logic: this loop adds each location marker to the map.
for index, row in locations.iterrows():
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

# I understand this part: this saves the finished interactive map as an HTML file.
m.save("hometown_map.html")

print("Map created! Open hometown_map.html to view it.")