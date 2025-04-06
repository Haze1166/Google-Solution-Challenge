# src/config.py
import logging

DEFAULT_THRESHOLDS = {
    'drought_risk_days': 7, 'drought_risk_mm': 2,
    'flood_risk_mm_per_day': 50, 'heavy_rain_mm_per_3h': 15,
    'heatwave_temp_c': 38, 'heatwave_days': 3,
    'frost_risk_temp_c': 2,
    'high_wind_speed_ms': 15,
    'high_humidity_perc': 85, 'high_humidity_duration_h': 12
}

def get_adjusted_thresholds(base_thresholds, crop, stage):
    adjusted = base_thresholds.copy()
    logging.info(f"Adjusting thresholds for Crop: {crop}, Stage: {stage}")
    # --- Add the adjustment logic from Colab Cell 3 here ---
    if stage in ["Flowering", "Fruiting/Maturity"]:
        adjusted['heatwave_temp_c'] = max(32, adjusted.get('heatwave_temp_c', 38) - 3)
        adjusted['drought_risk_days'] = max(3, adjusted.get('drought_risk_days', 7) - 2)
        logging.info("Applied higher sensitivity for Flowering/Fruiting stages.")
    if crop == "Rice" and stage != "Germination/Seedling":
        adjusted['drought_risk_days'] = min(10, adjusted.get('drought_risk_days', 7) + 3)
        logging.info("Applied lower drought sensitivity for Rice.")
    if crop == "Vegetables" and stage == "Germination/Seedling":
         adjusted['frost_risk_temp_c'] = max(3, adjusted.get('frost_risk_temp_c', 2) + 1)
         logging.info("Applied higher frost sensitivity for Vegetable seedlings.")
    if crop == "Maize" and stage in ["Fruiting/Maturity"]:
        adjusted['high_wind_speed_ms'] = max(10, adjusted.get('high_wind_speed_ms', 15) - 3)
        logging.info("Applied higher wind sensitivity for mature Maize.")
    # --- End adjustment logic ---
    logging.info(f"Final adjusted thresholds: {adjusted}")
    return adjusted