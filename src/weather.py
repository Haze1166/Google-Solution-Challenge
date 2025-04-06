# src/weather.py
import requests
import json
import logging

def get_weather_forecast_latlon(api_key, lat, lon):
    # ... (Copy the function code from Colab Cell 4a) ...
    # Make sure it uses logging.info, logging.error etc.
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {'lat': lat, 'lon': lon, 'appid': api_key, 'units': 'metric'}
    logging.info(f"Attempting to fetch weather data for Lat: {lat}, Lon: {lon}")
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        logging.info(f"Successfully fetched data.")
        return response.json()
    # ... (include the full try/except block with logging) ...
    except requests.exceptions.HTTPError as http_err:
         logging.error(f"HTTP error occurred: {http_err} - Status: {response.status_code}")
         if response.status_code == 401: logging.error("Check API key.")
         elif response.status_code == 429: logging.error("Rate limit exceeded.")
         else: logging.error(f"Error {response.status_code}: {response.text}")
         return None # Return None on error
    # ... other exceptions
    except Exception as e:
        logging.error(f"An unexpected error occurred during weather fetch: {e}")
        return None