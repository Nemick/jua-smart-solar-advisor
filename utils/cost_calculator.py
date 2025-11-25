import json
import os

def load_json_data(filename):
    """Loads JSON data from the data directory."""
    # Use absolute path based on script location
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(script_dir, "data", filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found at {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}")
        return None

def calculate_tariff_cost(monthly_consumption_kwh, tariff_data):
    """
    Calculates the monthly electricity cost and effective rate based on EPRA tariffs.
    Assumes domestic tariff for simplicity, as commercial is more complex.
    """
    if not tariff_data:
        return 0.0, 0.0, "N/A"

    tariffs = tariff_data.get("tariffs", {}).get("domestic", [])
    pass_through_charge = tariff_data.get("pass_through_charges_ksh_per_kwh", 5.5)
    vat_rate = tariff_data.get("vat_rate", 0.16)

    total_base_cost = 0.0
    remaining_consumption = monthly_consumption_kwh
    tariff_category = "Unknown"

    # Calculate base cost based on tiered structure
    for tier in tariffs:
        tier_name = tier["name"]
        min_kwh, max_kwh = tier["range_kwh"]
        rate = tier["base_rate_ksh_per_kwh"]

        if monthly_consumption_kwh >= min_kwh:
            if remaining_consumption > 0:
                consumption_in_tier = min(remaining_consumption, max_kwh - min_kwh + 1)
                
                # Special handling for the first tier (Lifeline)
                if tier_name == "Lifeline":
                    consumption_in_tier = min(monthly_consumption_kwh, max_kwh)
                    
                # For subsequent tiers, calculate consumption in that tier
                elif tier_name == "Ordinary 1":
                    consumption_in_tier = min(remaining_consumption, max_kwh - 30)
                
                elif tier_name == "Ordinary 2":
                    consumption_in_tier = remaining_consumption
                
                
                cost_in_tier = consumption_in_tier * rate
                total_base_cost += cost_in_tier
                remaining_consumption -= consumption_in_tier
                tariff_category = tier_name
                
                if remaining_consumption <= 0:
                    break
    
    # Simple approximation for pass-through charges and VAT
    total_pass_through_cost = monthly_consumption_kwh * pass_through_charge
    
    # Total cost before VAT (simplified: base + pass-through)
    subtotal = total_base_cost + total_pass_through_cost
    
    # VAT on subtotal
    total_vat = subtotal * vat_rate
    
    total_monthly_cost = subtotal + total_vat
    
    effective_rate = total_monthly_cost / monthly_consumption_kwh if monthly_consumption_kwh > 0 else 0.0

    return total_monthly_cost, effective_rate, tariff_category

def calculate_system_cost(system_size_kw, equipment_catalog, assumptions):
    """
    Estimates the total upfront cost of a solar system with proper breakdown.
    
    Returns:
        total_cost: Total system cost in KSh
        cost_per_watt: Cost per watt
        breakdown: Dict with detailed cost breakdown
    """
    if not equipment_catalog or not assumptions:
        return 0.0, 0.0, {}

    system_size_watts = system_size_kw * 1000
    
    # Get real equipment costs from catalog
    panels = equipment_catalog.get("panels", [])
    inverters = equipment_catalog.get("inverters", [])
    
    # 1. Panel Cost Calculation
    # User provided: 35 KSh/Watt base rate
    panel_rate_per_watt = 35
    standard_wattage = 450  # Using standard 450W panels
    
    # Calculate number of panels
    import math
    num_panels = max(1, math.ceil(system_size_watts / standard_wattage))
    
    # Recalculate actual system size
    actual_system_watts = num_panels * standard_wattage
    actual_system_kw = actual_system_watts / 1000
    
    # Base Panel Cost
    panel_base_cost = actual_system_watts * panel_rate_per_watt
    
    # 2. Inverter Cost Calculation
    # Inverters come in standard sizes: 1.5kW, 3kW, 5kW, 8kW, 10kW
    suitable_inverters = [inv for inv in inverters if inv.get("capacity_kw", 0) >= system_size_kw]
    if suitable_inverters:
        chosen_inverter = min(suitable_inverters, key=lambda x: x.get("capacity_kw", 999))
        inverter_base_cost = chosen_inverter.get("price_ksh", system_size_kw * 25000)
        inverter_capacity = chosen_inverter.get("capacity_kw", system_size_kw)
    else:
        # Fallback: KSh 25,000 per kW base price
        inverter_base_cost = system_size_kw * 25000
        # Round up inverter size
        if system_size_kw <= 1.5: inverter_capacity = 1.5
        elif system_size_kw <= 3.0: inverter_capacity = 3.0
        elif system_size_kw <= 5.0: inverter_capacity = 5.0
        else: inverter_capacity = math.ceil(system_size_kw)
        
    # 3. VAT Calculation (16% on Equipment)
    vat_rate = 0.16
    equipment_base_total = panel_base_cost + inverter_base_cost
    vat_amount = equipment_base_total * vat_rate
    
    # 4. Mounting & Installation
    # User provided: 3,000 KSh per panel for mounting
    mounting_cost = num_panels * 3000
    
    # 5. Safety & Earthing (CRITICAL)
    # Earth Rod + Clamp + Copper Tape + Lightning Arrestor + SPD
    # Basic Earthing Kit: ~3,500 KSh
    # Surge Protection Device (DC + AC): ~6,000 KSh
    # Lightning Arrestor: ~4,500 KSh
    safety_cost = 3500 + 6000 + 4500
    
    # Electrical Installation (Wiring, DB Board, Inverter setup)
    # Estimated at ~5,000 KSh + 2,000 per kW
    electrical_labor = 5000 + (actual_system_kw * 2000)
    
    # BOS (Cables, breakers, trunking) - approx 8% of equipment (reduced since safety is separate)
    bos_cost = equipment_base_total * 0.08
    
    # Total Cost
    total_cost = equipment_base_total + vat_amount + mounting_cost + electrical_labor + bos_cost + safety_cost
    
    # Cost per watt
    cost_per_watt = total_cost / actual_system_watts if actual_system_watts > 0 else 0
    
    # Detailed breakdown
    breakdown = {
        'panels': {
            'count': num_panels,
            'wattage': standard_wattage,
            'base_cost': panel_base_cost,
            'cost': panel_base_cost, # For backward compatibility
            'percentage': (panel_base_cost / total_cost * 100)
        },
        'inverter': {
            'capacity_kw': inverter_capacity,
            'base_cost': inverter_base_cost,
            'cost': inverter_base_cost,
            'percentage': (inverter_base_cost / total_cost * 100)
        },
        'vat': {
            'amount': vat_amount,
            'rate': "16%",
            'percentage': (vat_amount / total_cost * 100)
        },
        'mounting': {
            'cost': mounting_cost,
            'rate': "KSh 3,000/panel",
            'percentage': (mounting_cost / total_cost * 100)
        },
        'safety': {
            'cost': safety_cost,
            'desc': "Earthing & Protection",
            'percentage': (safety_cost / total_cost * 100)
        },
        'installation': {
            'cost': electrical_labor,
            'desc': "Electrical & Wiring",
            'percentage': (electrical_labor / total_cost * 100)
        },
        'bos': {
            'cost': bos_cost,
            'desc': "Cables & Accessories",
            'percentage': (bos_cost / total_cost * 100)
        },
        'total': total_cost,
        'actual_system_kw': actual_system_kw
    }
    
    return total_cost, cost_per_watt, breakdown

if __name__ == '__main__':
    # Example usage for testing
    tariff_data = load_json_data("epra_tariffs_2024_2026.json")
    
    # Test cases from roadmap (Domestic)
    consumption_low = 25 # Lifeline
    consumption_mid = 80 # Ordinary 1
    consumption_high = 150 # Ordinary 2
    
    cost_low, rate_low, cat_low = calculate_tariff_cost(consumption_low, tariff_data)
    cost_mid, rate_mid, cat_mid = calculate_tariff_cost(consumption_mid, tariff_data)
    cost_high, rate_high, cat_high = calculate_tariff_cost(consumption_high, tariff_data)
    
    print(f"Consumption: {consumption_low} kWh -> Cost: {cost_low:.2f} KSh, Rate: {rate_low:.2f} KSh/kWh, Category: {cat_low}")
    print(f"Consumption: {consumption_mid} kWh -> Cost: {cost_mid:.2f} KSh, Rate: {rate_mid:.2f} KSh/kWh, Category: {cat_mid}")
    print(f"Consumption: {consumption_high} kWh -> Cost: {cost_high:.2f} KSh, Rate: {rate_high:.2f} KSh/kWh, Category: {cat_high}")
    
    # Test cost estimation
    assumptions = load_json_data("baseline_assumptions.json")
    equipment = load_json_data("equipment_catalog.json")
    
    system_size_kw = 3.0
    cost, cost_per_watt = calculate_system_cost(system_size_kw, equipment, assumptions)
    print(f"\nSystem Size: {system_size_kw} kW -> Estimated Upfront Cost: {cost:.2f} KSh, Est. Cost/Watt: {cost_per_watt:.2f} KSh/W")
