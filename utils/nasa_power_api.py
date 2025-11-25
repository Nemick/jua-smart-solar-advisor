import requests
import pandas as pd
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

# Convert address to coordinates
def address_to_coordinates(address):
    geolocator = Nominatim(user_agent="nasa_power_api")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Address '{address}' not found")

# Fetch NASA POWER data
def fetch_nasa_power_data(lat, lon, start_date, end_date, parameters):
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": ",".join(parameters),
        "community": "RE",
        "latitude": lat,
        "longitude": lon,
        "start": start_date.strftime("%Y%m%d"),
        "end": end_date.strftime("%Y%m%d"),
        "format": "JSON"
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    if 'properties' in data and 'parameter' in data['properties']:
        df = pd.DataFrame(data['properties']['parameter'])
        df.index = pd.to_datetime(df.index)
        df = df.reset_index().rename(columns={"index": "Date"})
        return df
    else:
        raise ValueError("No data found for the given parameters")

# Wrapper: fetch by address
def fetch_by_address(address, start_date=None, end_date=None, parameters=None):
    today = datetime.now()
    first_day_of_current_month = today.replace(day=1)
    reference_date = first_day_of_current_month - timedelta(days=1)
    print(f"Today's date is {today}, and reference date is {reference_date}")

    # Default timeframe: last 12 months
    if end_date is None:
        end_date = reference_date
    if start_date is None:
        start_date = end_date.replace(year=end_date.year - 1)

    # Default parameters
    if parameters is None:
        parameters = [
            'ALLSKY_SFC_SW_DWN', 'CLRSKY_SFC_SW_DWN', 'ALLSKY_KT',
            'T2M', 'RH2M', 'T2M_MAX', 'T2M_MIN', 'WS10M'
        ]

    lat, lon = address_to_coordinates(address)
    return fetch_nasa_power_data(lat, lon, start_date, end_date, parameters)