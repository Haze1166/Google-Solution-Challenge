# src/advisories.py
import logging

def generate_advisories_enhanced(risks, crop_info):
    """
    Generates simple, actionable advice based on identified risks,
    considering crop type and growth stage.
    """
    # Ensure logging is available (it should be configured in app.py)
    logger = logging.getLogger(__name__) # Use named logger is good practice
    logger.info(f"Generating enhanced advisories for Crop: {crop_info.get('type','N/A')}, Stage: {crop_info.get('stage','N/A')}")

    advisories = [] # Initialize as a list

    if not risks:
        advisories.append("❌ Could not generate advisories: Risk assessment data is missing.")
        logger.warning("Advisory generation failed: No risk data.")
        # Still return the list containing the error message
        return advisories

    # Check if any warnings were triggered at all
    # Use .get() for safer dictionary access
    has_any_warning = any(v.get('warning', False) for k, v in risks.items() if k != 'overall_alerts')

    if not has_any_warning:
        advisories.append("✅ No significant climate risks detected in the upcoming forecast based on current thresholds. Monitor crops as usual.")
        logger.info("Generated 'No Significant Risk' advisory.")
        # Return the list with the 'no risk' message
        # The problematic log line will be skipped, which is fine here.
        return advisories

    advisories.append("--- Climate Risk Advisories & Recommendations ---")

    # --- Generate specific advice based on triggered risks and context ---
    # (Keep all the if risks['drought'].get('warning'): ... advisories.append(...) logic here)
    # ... (Example for drought)
    if risks.get('drought', {}).get('warning'): # Safer access
        advisories.append("\n⚠️ Drought / Dry Spell Risk:")
        advisories.append("  - Focus on water conservation: check irrigation system efficiency, repair leaks.")
        # ... other drought advice ...
        if crop_info.get('stage') in ["Flowering", "Fruiting/Maturity"]:
             advisories.append(f"  - CRITICAL STAGE ({crop_info.get('stage')}): Ensure adequate water if possible, as yield is highly sensitive now.")
        else:
             advisories.append("  - Consider adjusting irrigation schedule if water is limited.")

    # ... (Include the logic for flood, heatwave, frost, wind, humidity using .get() for safety) ...
    if risks.get('flood_heavy_rain', {}).get('warning'):
        advisories.append("\n⚠️ Flood / Heavy Rain Risk:")
        #... append flood advice ...
    if risks.get('heatwave', {}).get('warning'):
        advisories.append("\n⚠️ Heatwave Risk:")
        #... append heatwave advice ...
    if risks.get('frost', {}).get('warning'):
        advisories.append("\n⚠️ Frost Risk:")
        #... append frost advice ...
    if risks.get('high_wind', {}).get('warning'):
        advisories.append("\n⚠️ High Wind Risk:")
        #... append wind advice ...
    if risks.get('prolonged_high_humidity', {}).get('warning'):
        advisories.append("\n⚠️ Prolonged High Humidity Risk:")
        #... append humidity advice ...

    # --- Add Specific Details Summary ---
    overall_alerts = risks.get('overall_alerts', []) # Get alerts list or empty list
    if overall_alerts:
        advisories.append("\n--- Specific Forecast Details Triggering Warnings ---")
        max_details_in_advisory = 7
        for i, detail in enumerate(overall_alerts):
             if i < max_details_in_advisory:
                 advisories.append(f"  - {detail}")
             elif i == max_details_in_advisory:
                 advisories.append("  - ... (and potentially more)")
                 break

    # --- Final Disclaimer ---
    advisories.append("\n---")
    advisories.append("NOTE: These advisories are based on forecast data and general rules. Always combine with your local knowledge, field observations, and consult local agricultural experts for critical decisions.")

    # ***** FIX: Add check before logging *****
    if isinstance(advisories, list):
        logger.info(f"Generated {len(advisories)} advisory lines.")
    else:
        # This case *shouldn't* happen with the current logic, but adding robustness
        logger.error(f"Error generating advisories: 'advisories' variable ended up as type {type(advisories)}, not list. Value: {advisories}")
        # Optionally, return a generic error message list
        # return ["❌ An internal error occurred while generating advisories."]

    return advisories # Return the final list