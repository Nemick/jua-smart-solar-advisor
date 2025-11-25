import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.api_core import exceptions
import sys
sys.path.append('.')
from prompts.system_prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def generate_solar_recommendation(
    location, monthly_consumption_kwh, system_preference, 
    equipment_catalog, tariff_data, baseline_assumptions, 
    ghi_kwh_m2_day, effective_rate_ksh_per_kwh, tariff_category,
    existing_system_config=None,
    model_name="gemini-1.5-flash"
):
    """
    Generates a solar system recommendation using Google Gemini.
    """
    # 1. Format the System Prompt with dynamic data
    system_prompt_formatted = SYSTEM_PROMPT.format(
        location=location,
        ghi_kwh_m2_day=ghi_kwh_m2_day,
        monthly_consumption_kwh=monthly_consumption_kwh,
        system_preference=system_preference,
        tariff_category=tariff_category,
        effective_rate_ksh_per_kwh=effective_rate_ksh_per_kwh,
        system_losses_percent=baseline_assumptions.get("system_losses_percent", 0.15),
        degradation_rate_per_year=baseline_assumptions.get("degradation_rate_per_year", 0.008),
        installation_cost_ksh_per_watt=sum(baseline_assumptions.get("installation_cost_ksh_per_watt_range", [55, 120])) / 2,
        grid_emission_factor_tco2_per_mwh=baseline_assumptions.get("grid_emission_factor_tco2_per_mwh", 0.4087)
    )

    # 2. Format the User Prompt with all data for the model to use
    user_prompt_formatted = USER_PROMPT_TEMPLATE.format(
        location=location,
        monthly_consumption_kwh=monthly_consumption_kwh,
        system_preference=system_preference,
        equipment_catalog=json.dumps(equipment_catalog, indent=2),
        tariff_data=json.dumps(tariff_data, indent=2),
        baseline_assumptions=json.dumps(baseline_assumptions, indent=2)
    )
    
    # CRITICAL: If an existing configuration is provided, force the AI to use it
    if existing_system_config:
        config_str = json.dumps(existing_system_config, indent=2)
        user_prompt_formatted += f"""
        
        CRITICAL INSTRUCTION:
        The user has already calculated a specific system configuration using our deterministic calculator. 
        You MUST use the following specifications for your report. 
        DO NOT propose a different system size, panel count, or cost. 
        Your job is to provide the qualitative details (brands, maintenance, specific models) for THIS configuration:
        
        EXISTING CONFIGURATION TO USE:
        {config_str}
        
        - Use 'system_kw' as 'required_system_size_kw'
        - Use 'solar_cost' + 'battery_cost' + 'other_costs' as 'upfront_cost_ksh'
        - Use the exact panel count and battery details provided.
        """

    # Load .env and get Gemini API key
    try:
        load_dotenv()
    except Exception:
        pass

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None, "❌ Gemini API key not found. Add GEMINI_API_KEY to your .env file. Get a free key at: https://aistudio.google.com/app/apikey"
    
    # Configure the client to use the provided API key
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return None, f"Error configuring Gemini client: {e}"

    # 3. Configure the model for JSON output
    generation_config = GenerationConfig(
        temperature=0.1,
        response_mime_type="application/json"
    )

    # 4. Call the Gemini API
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt_formatted
        )
        
        response = model.generate_content(
            contents=user_prompt_formatted,
            generation_config=generation_config
        )
        
        # The response.text should be a valid JSON string due to the config
        return json.loads(response.text), None

    except exceptions.GoogleAPICallError as e:
        error_message = f"Gemini API Error: {e}"
        print(error_message)
        return None, error_message
    except json.JSONDecodeError as e:
        error_message = f"JSON Decode Error: {e}. Raw response: {response.text}"
        print(error_message)
        return None, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        return None, error_message

if __name__ == '__main__':
    # Example usage for testing
    from utils.cost_calculator import load_json_data, calculate_tariff_cost
    
    # Mock user input
    location = "Nairobi"
    monthly_consumption_kwh = 300
    system_preference = "Grid-tied (net metering)"
    
    # Load data
    tariff_data = load_json_data("epra_tariffs_2024_2026.json")
    equipment_catalog = load_json_data("equipment_catalog.json")
    baseline_assumptions = load_json_data("baseline_assumptions.json")
    ghi_data = load_json_data("kenya_counties_irradiance.json")
    
    # Pre-calculate necessary values
    ghi_kwh_m2_day = ghi_data.get(location, {}).get("ghi_kwh_m2_day", 5.0)
    _, effective_rate_ksh_per_kwh, tariff_category = calculate_tariff_cost(monthly_consumption_kwh, tariff_data)
    
    print(f"Simulating API call for {location} ({monthly_consumption_kwh} kWh/month)...")
    
    # Generate recommendation
    recommendation, error = generate_solar_recommendation(
        location, monthly_consumption_kwh, system_preference, 
        equipment_catalog, tariff_data, baseline_assumptions, 
        ghi_kwh_m2_day, effective_rate_ksh_per_kwh, tariff_category
    )
    
    if recommendation:
        print("\n--- Recommendation JSON ---")
        print(json.dumps(recommendation, indent=2))
    else:
        print(f"\n--- Error ---")
        print(error)
