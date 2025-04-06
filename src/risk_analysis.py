# src/risk_analysis.py
import logging
from datetime import datetime, timedelta, date

# Use a named logger for best practice
logger = logging.getLogger(__name__)

def assess_climate_risks_enhanced(forecast_data, thresholds):
    """
    Analyzes forecast data to identify potential climate risks using provided thresholds.
    Includes checks for Temp (Heat/Frost), Rain (Drought/Flood), Wind, Humidity.
    """
    logger.info("Starting enhanced climate risk assessment...")

    # --- Initialize risks dictionary (Ensure correct syntax) ---
    risks = {
        "drought": {"warning": False, "details": []},
        "flood_heavy_rain": {"warning": False, "details": []},
        "heatwave": {"warning": False, "details": []},
        "frost": {"warning": False, "details": []},
        "high_wind": {"warning": False, "details": []},
        "prolonged_high_humidity": {"warning": False, "details": []},
        "overall_alerts": []
    } # Make sure brackets match and commas are correct

    # --- Robust Input Validation ---
    # Explicitly check for None and dictionary type first
    if forecast_data is None:
        logger.warning("Input 'forecast_data' is None. Cannot assess risks.")
        return risks # Return initialized risks (all False)

    if not isinstance(forecast_data, dict):
        logger.warning(f"Input 'forecast_data' is not a dictionary (type: {type(forecast_data)}). Cannot assess risks.")
        return risks

    # Now check for the 'list' key and if it's a non-empty list
    if 'list' not in forecast_data or not isinstance(forecast_data['list'], list) or not forecast_data['list']:
        logger.warning("Input 'forecast_data' is missing 'list' key, 'list' is not a list, or 'list' is empty. Cannot assess risks.")
        # Log content if it's small enough to be helpful
        if len(str(forecast_data)) < 200:
             logger.warning(f"Problematic forecast_data content: {forecast_data}")
        return risks # Return initialized risks

    # --- Main Logic Block (Ensure correct indentation) ---
    try: # Wrap main processing in a try block for unexpected errors
        forecast_list = forecast_data['list']
        daily_summary = {}

        # --- Aggregate data daily (with enhanced error handling) ---
        logger.info("Aggregating 3-hourly forecast data into daily summaries...")
        for i, entry in enumerate(forecast_list): # Use enumerate for logging entry index on error
            dt_obj = None # Initialize dt_obj
            try:
                # Check if entry is a dictionary before proceeding
                if not isinstance(entry, dict):
                    logger.warning(f"Skipping forecast entry #{i}: Item is not a dictionary (type: {type(entry)}, value: {entry})")
                    continue

                # Safely get timestamp
                ts = entry.get('dt')
                if ts is None:
                    logger.warning(f"Skipping forecast entry #{i}: Missing 'dt' timestamp.")
                    continue
                dt_obj = datetime.fromtimestamp(ts)
                day_str = dt_obj.strftime('%Y-%m-%d')

                # Initialize day summary if first time seeing this day
                if day_str not in daily_summary:
                    daily_summary[day_str] = {
                        'max_temp': -100, 'min_temp': 200, 'total_rain': 0,
                        'max_wind_speed': 0, 'humidity_readings': [], 'rain_3h_intervals': [],
                        'count': 0
                    }

                summary = daily_summary[day_str]
                # Use .get() extensively for safe access, providing defaults
                main = entry.get('main', {})
                wind = entry.get('wind', {})
                rain_data = entry.get('rain', {})
                rain_3h = rain_data.get('3h', 0) # Default to 0 if 'rain' or '3h' missing

                summary['max_temp'] = max(summary['max_temp'], main.get('temp_max', summary['max_temp'])) # Default to current max if missing
                summary['min_temp'] = min(summary['min_temp'], main.get('temp_min', summary['min_temp'])) # Default to current min if missing
                summary['total_rain'] += rain_3h
                summary['max_wind_speed'] = max(summary['max_wind_speed'], wind.get('speed', 0))
                summary['humidity_readings'].append(main.get('humidity')) # Append None if humidity is missing
                if rain_3h > 0:
                    summary['rain_3h_intervals'].append(rain_3h)
                summary['count'] += 1

            except (KeyError, TypeError, ValueError, AttributeError) as e:
                # Catch potential errors during processing of a single entry
                dt_str = dt_obj.strftime('%Y-%m-%d %H:%M') if dt_obj else "Unknown Time"
                logger.error(f"Error processing forecast entry #{i} ({dt_str}): {e}. Entry: {entry}", exc_info=False) # Log error without full traceback for brevity unless debugging needed
                continue # Skip to next entry

        logger.info(f"Processed {len(daily_summary)} daily summaries.")

        # --- Apply Risk Assessment Rules (ensure correct indentation) ---
        logger.info("Applying risk assessment rules...")
        consecutive_dry_days = 0
        consecutive_hot_days = 0
        today = date.today()
        days_processed_for_risk = 0
        sorted_days = sorted(daily_summary.keys())

        for day_str in sorted_days:
            try: # Add try/except around day processing as well
                day_date = datetime.strptime(day_str, '%Y-%m-%d').date()
                if day_date < today: continue

                days_processed_for_risk += 1
                summary = daily_summary[day_str] # Should exist if day_str is from the dict keys

                # --- Check Individual Day Risks (using .get() for safety on thresholds) ---
                day_alerts = []
                # Frost
                frost_threshold = thresholds.get('frost_risk_temp_c', 2) # Default if missing
                if summary.get('min_temp', 100) <= frost_threshold: # Default high if min_temp missing
                    risks['frost']['warning'] = True
                    alert = f"Frost Risk on {day_str}: Min temp forecast {summary.get('min_temp'):.1f}°C (Threshold: <= {frost_threshold}°C)."
                    risks['frost']['details'].append(alert)
                    day_alerts.append(alert)

                # ... (Apply similar .get() safety for Flood, Wind, Humidity checks) ...
                 # Flood / Heavy Rain
                flood_thresh_day = thresholds.get('flood_risk_mm_per_day', 50)
                flood_thresh_3h = thresholds.get('heavy_rain_mm_per_3h', 15)
                total_rain = summary.get('total_rain', 0)
                rain_intervals = summary.get('rain_3h_intervals', [])
                max_3h_rain = max(rain_intervals) if rain_intervals else 0

                if total_rain >= flood_thresh_day:
                    risks['flood_heavy_rain']['warning'] = True
                    alert = f"Flood Risk on {day_str}: Total rain forecast {total_rain:.1f}mm (Threshold: >= {flood_thresh_day}mm)."
                    risks['flood_heavy_rain']['details'].append(alert)
                    day_alerts.append(alert)
                elif max_3h_rain >= flood_thresh_3h: # Check burst only if daily flood not triggered
                    risks['flood_heavy_rain']['warning'] = True
                    alert = f"Heavy Rain Burst Risk on {day_str}: Max 3h rain forecast {max_3h_rain:.1f}mm (Threshold: >= {flood_thresh_3h}mm)."
                    risks['flood_heavy_rain']['details'].append(alert)
                    day_alerts.append(alert)

                 # High Wind
                wind_threshold = thresholds.get('high_wind_speed_ms', 15)
                max_wind = summary.get('max_wind_speed', 0)
                if max_wind >= wind_threshold:
                    risks['high_wind']['warning'] = True
                    alert = f"High Wind Risk on {day_str}: Max wind forecast {max_wind:.1f} m/s (Threshold: >= {wind_threshold} m/s)."
                    risks['high_wind']['details'].append(alert)
                    day_alerts.append(alert)

                # High Humidity
                humid_thresh = thresholds.get('high_humidity_perc', 85)
                humid_dur_thresh = thresholds.get('high_humidity_duration_h', 12)
                humid_readings = [h for h in summary.get('humidity_readings', []) if h is not None] # Filter out Nones
                humid_hours = sum(1 for h in humid_readings if h >= humid_thresh) * 3 # Approx hours
                if humid_hours >= humid_dur_thresh and humid_readings: # Check there were readings
                     risks['prolonged_high_humidity']['warning'] = True
                     avg_humid_high = sum(h for h in humid_readings if h >= humid_thresh) / len([h for h in humid_readings if h >= humid_thresh]) if any(h >= humid_thresh for h in humid_readings) else humid_thresh # Avoid division by zero
                     alert = f"Prolonged High Humidity Risk on {day_str}: Approx {humid_hours} hours >= {humid_thresh}% (Avg high: {avg_humid_high:.0f}%, Threshold: >= {humid_dur_thresh}h)."
                     risks['prolonged_high_humidity']['details'].append(alert)
                     day_alerts.append(alert)


                # --- Check Consecutive Day Risks ---
                drought_mm_thresh = thresholds.get('drought_risk_mm', 2)
                drought_days_thresh = thresholds.get('drought_risk_days', 7)
                heat_temp_thresh = thresholds.get('heatwave_temp_c', 38)
                heat_days_thresh = thresholds.get('heatwave_days', 3)

                # Drought
                if summary.get('total_rain', 100) <= drought_mm_thresh: # Default high if missing
                    consecutive_dry_days += 1
                else:
                    consecutive_dry_days = 0
                if consecutive_dry_days >= drought_days_thresh and not risks['drought']['warning']:
                    risks['drought']['warning'] = True
                    drought_start_day = (day_date - timedelta(days=consecutive_dry_days - 1)).strftime('%Y-%m-%d')
                    alert = f"Drought Risk Developing: {consecutive_dry_days} consecutive days with <= {drought_mm_thresh}mm rain starting around {drought_start_day}."
                    risks['drought']['details'].append(alert)
                    day_alerts.append(alert)

                # Heatwave
                if summary.get('max_temp', 0) >= heat_temp_thresh: # Default low if missing
                    consecutive_hot_days += 1
                else:
                    consecutive_hot_days = 0
                if consecutive_hot_days >= heat_days_thresh:
                    already_alerted = any(f"ending {day_str}" in d for d in risks['heatwave']['details'])
                    if not already_alerted:
                        risks['heatwave']['warning'] = True
                        # heatwave_start_day = (day_date - timedelta(days=consecutive_hot_days - 1)).strftime('%Y-%m-%d') # Start day less useful than end day here
                        alert = f"Heatwave Risk: {consecutive_hot_days} consecutive days >= {heat_temp_thresh}°C (ending {day_str})."
                        risks['heatwave']['details'].append(alert)
                        day_alerts.append(alert)

                if day_alerts:
                    risks['overall_alerts'].extend(day_alerts)

                if days_processed_for_risk >= 5:
                    logger.info("Reached 5-day forecast limit for risk assessment.")
                    break

            except Exception as e_day:
                 # Catch errors processing a specific day's summary
                 logger.error(f"Error processing risk assessment for day {day_str}: {e_day}", exc_info=False)
                 continue # Skip to next day

    except Exception as e_main:
        # Catch any unexpected error in the main processing block
        logger.exception("An unexpected error occurred during the main risk assessment processing.") # Log full traceback here
        # Return the partially filled risks dictionary or the initial one
        return risks

    # --- Final Return (ensure correct indentation) ---
    logger.info("Enhanced risk assessment complete.")
    return risks # This should be aligned with the start of the 'def' line, minus one indent level