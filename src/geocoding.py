# src/geocoding.py
import requests
import logging
import os

# Use a named logger
logger = logging.getLogger(__name__)

def geocode_address(address_query: str, api_key: str) -> tuple[float | None, float | None]:
    """
    Converts a text address into latitude and longitude using OpenWeatherMap Geocoding API.

    Args:
        address_query: The address string (e.g., "London, UK", "Bhopal, IN").
        api_key: Your OpenWeatherMap API key.

    Returns:
        A tuple containing (latitude, longitude) floats if successful,
        otherwise returns (None, None).
    """
    if not address_query or not api_key:
        logger.warning("Geocoding failed: Address query or API key is missing.")
        return None, None

    base_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': address_query,
        'limit': 1,  # We only need the most likely result
        'appid': api_key
    }
    logger.info(f"Attempting to geocode address: '{address_query}'")

    try:
        response = requests.get(base_url, params=params, timeout=10) # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        results = response.json()

        if not results or not isinstance(results, list):
            logger.warning(f"Geocoding failed: No results found or unexpected response format for '{address_query}'. Response: {results}")
            return None, None

        # Extract lat/lon from the first result
        first_result = results[0]
        lat = first_result.get('lat')
        lon = first_result.get('lon')
        found_name = first_result.get('name', 'N/A')
        found_country = first_result.get('country', 'N/A')


        if lat is not None and lon is not None:
            logger.info(f"Geocoding successful for '{address_query}': Found '{found_name}, {found_country}' at ({lat:.4f}, {lon:.4f})")
            # Ensure they are floats before returning
            return float(lat), float(lon)
        else:
            logger.warning(f"Geocoding failed: Lat/Lon missing in the response for '{address_query}'. Response: {first_result}")
            return None, None

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error during geocoding for '{address_query}': {http_err} - Status: {response.status_code}")
        if response.status_code == 401: logger.error("Check API key validity.")
        elif response.status_code == 429: logger.error("Geocoding rate limit exceeded.")
        return None, None
    except requests.exceptions.Timeout:
        logger.error(f"Timeout during geocoding request for '{address_query}'.")
        return None, None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Connection error during geocoding for '{address_query}': {req_err}")
        return None, None
    except (json.JSONDecodeError, IndexError, KeyError, TypeError, ValueError) as e:
        logger.error(f"Error parsing geocoding response or extracting data for '{address_query}': {e}. Response: {response.text if 'response' in locals() else 'N/A'}", exc_info=False)
        return None, None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during geocoding for '{address_query}'.") # Log full traceback for unexpected
        return None, None