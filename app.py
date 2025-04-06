import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv

# Import your refactored logic
from src.config import DEFAULT_THRESHOLDS, get_adjusted_thresholds
# Import NEW geocoding function
from src.geocoding import geocode_address
from src.weather import get_weather_forecast_latlon
from src.risk_analysis import assess_climate_risks_enhanced
from src.advisories import generate_advisories_enhanced
# from src.ml_simulation import simulate_yield_prediction_placeholder # Optional

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_dev')
API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')

@app.route('/')
def index():
    """Renders the main input form."""
    return render_template('index.html')

@app.route('/get_advisory', methods=['POST'])
def get_advisory():
    """Handles form submission, geocodes, runs logic, and shows results."""
    if not API_KEY:
        logging.error("API Key not configured in environment variables.")
        # Use flash for user feedback instead of redirecting immediately with error template
        flash("Server configuration error: API Key missing.", "error")
        return redirect(url_for('index'))

    try:
        # Get form data - CHANGED to address
        address = request.form.get('address')
        crop = request.form.get('crop_type', 'Other')
        stage = request.form.get('growth_stage', 'Vegetative')

        if not address:
            flash("Please enter a location.", "error")
            return redirect(url_for('index'))

        logging.info(f"Request received: Address='{address}', Crop={crop}, Stage={stage}")

        # --- NEW: Geocoding Step ---
        lat, lon = geocode_address(address, API_KEY)

        if lat is None or lon is None:
            logging.warning(f"Geocoding failed for address: '{address}'")
            flash(f"Could not find coordinates for the location: '{address}'. Please try a different format (e.g., 'City, Country Code').", "error")
            return redirect(url_for('index'))
        # --- End Geocoding Step ---

        logging.info(f"Geocoded '{address}' to Lat={lat:.4f}, Lon={lon:.4f}")

        # --- Existing Logic Pipeline (using retrieved lat/lon) ---
        # 1. Get Weather Data
        weather_data = get_weather_forecast_latlon(API_KEY, lat, lon)
        if weather_data is None:
            # Add specific message if weather fails after geocoding succeeds
            flash("Successfully found location, but could not retrieve weather forecast data. The weather service might be temporarily unavailable.", "error")
            return redirect(url_for('index'))

        # 2. Adjust Thresholds & Assess Risks
        crop_info = {'type': crop, 'stage': stage}
        thresholds = get_adjusted_thresholds(DEFAULT_THRESHOLDS, crop, stage)
        identified_risks = assess_climate_risks_enhanced(weather_data, thresholds)

        # 3. Generate Advisories
        farmer_advisories = generate_advisories_enhanced(identified_risks, crop_info)

        # --- Render Results (Pass address and maybe lat/lon) ---
        return render_template('results.html',
                               advisories=farmer_advisories,
                               address=address, # Pass original address
                               lat=lat,       # Pass resolved coords
                               lon=lon,
                               crop_info=crop_info
                              )

    except Exception as e:
        logging.exception("An error occurred during advisory generation.")
        flash(f"An unexpected server error occurred. Please try again later.", "error") # Generic error for user
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    # Ensure host='0.0.0.0' for accessibility if running in Docker/some VMs
    # Port can be overridden by environment variable, common for deployment platforms
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) # Turn Debug OFF for production simulation