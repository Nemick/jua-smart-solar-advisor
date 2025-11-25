import json

def load_json_data(filename):
    """Loads JSON data from the data directory."""
    path = f"data/{filename}"
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def validate_recommendation(recommendation, equipment_catalog, assumptions):
    """Validates the Gemini model's recommendation against technical, price, and physics rules."""
    errors = []
    if not recommendation or not equipment_catalog or not assumptions:
        errors.append("Missing recommendation, catalog, or assumptions for validation.")
        return errors

    # Technical Validation
    sys_sizing = recommendation.get("system_sizing", {})
    panel_count = sys_sizing.get("panel_count", 0)
    panel_wattage = sys_sizing.get("panel_wattage_w", 0)
    system_size_kw = sys_sizing.get("required_system_size_kw", 0)
    inverter_size_kw = sys_sizing.get("inverter_size_kw", 0)

    # 1. Panel count * wattage matches system size (±5%)
    if panel_count > 0 and panel_wattage > 0:
        calculated_size_kw = (panel_count * panel_wattage) / 1000
        if not (0.95 * calculated_size_kw <= system_size_kw <= 1.05 * calculated_size_kw):
            errors.append(f"Technical Error: System size mismatch. Calculated: {calculated_size_kw:.2f} kW, Recommended: {system_size_kw:.2f} kW")

    # 2. Inverter capacity = 1.1-1.3x panel capacity
    if system_size_kw > 0 and inverter_size_kw > 0:
        if not (1.1 * system_size_kw <= inverter_size_kw <= 1.3 * system_size_kw):
            errors.append(f"Technical Error: Inverter size is not 1.1-1.3x the system size. System: {system_size_kw:.2f} kW, Inverter: {inverter_size_kw:.2f} kW")

    # Price Validation
    fin_analysis = recommendation.get("financial_analysis", {})
    cost_per_watt = fin_analysis.get("cost_per_watt_ksh", 0)
    min_cost_per_watt, max_cost_per_watt = assumptions.get("installation_cost_ksh_per_watt_range", [55, 120])

    # 3. Cost per watt is within Kenya market ranges
    if cost_per_watt > 0 and not (min_cost_per_watt <= cost_per_watt <= max_cost_per_watt):
        errors.append(f"Price Error: Cost per watt ({cost_per_watt:.2f} KSh) is outside the expected range of {min_cost_per_watt}-{max_cost_per_watt} KSh.")

    # Physics Validation
    loc_analysis = recommendation.get("location_analysis", {})
    ghi = loc_analysis.get("ghi_kwh_m2_day", 0)
    annual_gen = sys_sizing.get("target_annual_generation_kwh", 0)
    system_losses = assumptions.get("system_losses_percent", 0.15)

    # 4. Annual generation is physically possible
    if ghi > 0 and system_size_kw > 0 and annual_gen > 0:
        # Max possible generation (kW * GHI * 365 * (1 - losses))
        max_possible_gen = system_size_kw * ghi * 365 * (1 - system_losses)
        if annual_gen > max_possible_gen * 1.05: # Allow 5% margin
            errors.append(f"Physics Error: Annual generation ({annual_gen:.2f} kWh) exceeds theoretical maximum ({max_possible_gen:.2f} kWh).")

    return errors

if __name__ == '__main__':
    # Example usage for testing
    mock_recommendation = {
        "system_sizing": {
            "required_system_size_kw": 3.0,
            "panel_count": 6,
            "panel_wattage_w": 550,
            "total_panel_capacity_kw": 3.3,
            "inverter_size_kw": 3.5,
            "battery_capacity_kwh": 0,
            "target_annual_generation_kwh": 4500
        },
        "financial_analysis": {
            "upfront_cost_ksh": 300000,
            "cost_per_watt_ksh": 90,
            "annual_savings_ksh": 40000,
            "payback_period_years": 7.5,
            "net_metering_credit_ksh_per_year": 0,
            "25_year_npv_ksh": 1500000
        },
        "location_analysis": {
            "county": "Nairobi",
            "ghi_kwh_m2_day": 5.2,
            "tariff_category": "Ordinary 2",
            "effective_rate_ksh_per_kwh": 28.0
        }
    }
    equipment = load_json_data("equipment_catalog.json")
    assumptions = load_json_data("baseline_assumptions.json")

    validation_errors = validate_recommendation(mock_recommendation, equipment, assumptions)
    if validation_errors:
        print("Validation Failed:")
        for error in validation_errors:
            print(f"- {error}")
    else:
        print("Validation Passed!")
