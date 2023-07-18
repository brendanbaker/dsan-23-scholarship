# mapmaker.py
# @Brendan Baker

import pandas as pd
import folium
from folium import LayerControl
from colorsys import rgb_to_hls, hls_to_rgb
from matplotlib.colors import hex2color
import random
import geopy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import geopy.distance

def add_noise(lat, lng):
    # Add random noise to the coordinates
    lat += random.uniform(-0.05, 0.05)
    lng += random.uniform(-0.05, 0.05)
    return lat, lng

def get_coordinates(location):
    if location.lower() == "anywhere" or location.lower() == 'united states':
        lat = random.uniform(33, 45)
        lng = random.uniform(-116, -84)  # Adjust the longitude range to avoid water
    else:
        try:
            location_data = geolocator.geocode(location)
            if location_data:
                lat, lng = location_data.latitude, location_data.longitude
            else:
                lat, lng = None, None
        except GeocoderTimedOut:
            lat, lng = None, None

    if lat and lng:
        lat, lng = add_noise(lat, lng)
        return lat, lng
    else:
        return None, None


def marker_size_and_color(salary, time_interval):
    base_color = "#85bb65"
    if time_interval == 'a year':
        size = salary / 5000
    elif time_interval == 'an hour':
        annual_salary = salary * 2080
        size = annual_salary / 5000

    r, g, b = hex2color(base_color)
    h, l, s = rgb_to_hls(r, g, b)
    l *= 0.5 + 0.5 * (1 - size / 20)
    r, g, b = hls_to_rgb(h, l, s)
    color = f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'

    opacity = min(1.0, 0.5 + 0.5 * (size / (20*2)))
    return size, base_color, 0.9

job_postings_df = pd.read_csv("./data/salary_location_clean.csv")

# Create a base map centered on the United States
map_job = folium.Map(location=[38.407512, -100.321473], zoom_start=4, tiles='CartoDB dark_matter')

# Create layers for in-person and remote jobs
in_person_layer = folium.FeatureGroup(name="In-person")
remote_layer = folium.FeatureGroup(name="Remote", show=False)

# Add job postings to the map
# Add job postings to the map
for index, posting in job_postings_df.iterrows():
    # For min_salary
    size, color, opacity = marker_size_and_color(posting['min_salary'], posting['time_interval'])
    salary_label = (
        f"${posting['min_salary']:,} - ${posting['max_salary']:,} a year"
        if posting['time_interval'] == 'a year'
        else f"${posting['min_salary'] * 2080:,} - ${posting['max_salary'] * 2080:,} a year (hourly)"
    )
    layer = in_person_layer if posting['location'].lower() not in ['anywhere', 'united states'] else remote_layer
    folium.CircleMarker(
        location=[posting['latitude'], posting['longitude']],
        radius=size,
        color='white',
        weight = 1,
        fill=True,
        fill_color="#305718",
        fill_opacity=opacity,
        popup=(
            f"<strong>{posting['name']}</strong><br>"
            f"Salary: {salary_label}<br>"
        ),
        tooltip=posting['name'],
    ).add_to(layer)

    # For max_salary
    size, color, opacity = marker_size_and_color(posting['max_salary'], posting['time_interval'])
    folium.CircleMarker(
        location=[posting['latitude'], posting['longitude']],
        radius=size,
        color='white',
        weight = 1,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=(
            f"<strong>{posting['name']}</strong><br><br>"
            f"<strong> Job title: </strong>{posting['job_title']}<br><br>"
            f"<strong> Location: </strong>{posting['location']}<br><br>"
            f"<strong>Salary:</strong> {salary_label}<br>"
        ),
        tooltip=posting['name'],
    ).add_to(layer)
    
map_job.add_child(in_person_layer)
map_job.add_child(remote_layer)

# Add layer control to the map with the menu open by default
folium.LayerControl(collapsed=False).add_to(map_job)


