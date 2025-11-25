"""
Advanced Battery Storage Calculator
Calculates battery requirements, costs, and lifecycle analysis
"""

def calculate_battery_requirements(daily_consumption_kwh, backup_hours, system_type):
    """
    Calculate battery capacity needed based on consumption and backup duration
    
    Args:
        daily_consumption_kwh: Daily energy consumption in kWh
        backup_hours: Desired backup duration in hours
        system_type: 'Hybrid' or 'Off-grid'
    
    Returns:
        dict with battery specifications
    """
    # Calculate hourly consumption
    hourly_consumption = daily_consumption_kwh / 24
    
    # Energy needed for backup
    backup_energy_kwh = hourly_consumption * backup_hours
    
    # For off-grid, add 1-2 days of autonomy
    if 'Off-grid' in system_type:
        autonomy_days = 2
        backup_energy_kwh = daily_consumption_kwh * autonomy_days
    
    return {
        'backup_energy_kwh': backup_energy_kwh,
        'hourly_consumption': hourly_consumption,
        'backup_hours': backup_hours
    }



def calculate_battery_specs(backup_energy_kwh, battery_type, depth_of_discharge=None, system_kw=None):
    """
    Calculate actual battery capacity and specifications
    
    Args:
        backup_energy_kwh: Required backup energy
        battery_type: 'Lithium' or 'Lead-Acid' or 'Gel'
        depth_of_discharge: Optional DoD override
        system_kw: System size in kW (to determine voltage)
    
    Returns:
        dict with battery specifications including proper series/parallel configuration
    """
    # Default Depth of Discharge based on battery type
    if depth_of_discharge is None:
        if 'Lithium' in battery_type:
            dod = 0.9  # Lithium: 90%
        elif 'Gel' in battery_type:
            dod = 0.6  # Gel: 60%
        else:  # Lead-Acid
            dod = 0.5  # Lead-Acid: 50%
    else:
        dod = depth_of_discharge
    
    # Determine system voltage based on system size
    if system_kw is None or system_kw < 1.5:
        system_voltage = 12  # Small systems: 12V
        batteries_in_series = 1
    elif system_kw < 5:
        system_voltage = 24  # Medium systems: 24V
        batteries_in_series = 2
    else:
        system_voltage = 48  # Large systems: 48V
        batteries_in_series = 4
    
    # Usable capacity needed
    usable_capacity_kwh = backup_energy_kwh
    
    # Total capacity (accounting for DoD)
    total_capacity_kwh = usable_capacity_kwh / dod
    
    # Different logic for Lithium vs Lead-Acid/Gel
    is_lithium = 'Lithium' in battery_type
    
    if is_lithium:
        # Lithium batteries - can be kWh-based or Ah-based
        # Check if we should use kWh-based lithium batteries (for larger systems)
        if total_capacity_kwh >= 2.5:
            # Use kWh-based lithium batteries (e.g., 5.12kWh Menred, 10.24kWh, etc.)
            kwh_battery_sizes = [2.56, 5.12, 7.68, 10.24, 15.36, 20.48]  # Common kWh battery sizes
            recommended_kwh_per_battery = min([s for s in kwh_battery_sizes if s >= total_capacity_kwh / batteries_in_series], 
                                             default=kwh_battery_sizes[-1])
            
            # Calculate how many kWh batteries needed
            parallel_strings = max(1, int(total_capacity_kwh / (recommended_kwh_per_battery * batteries_in_series)) + 
                                  (1 if total_capacity_kwh % (recommended_kwh_per_battery * batteries_in_series) > 0 else 0))
            total_batteries = batteries_in_series * parallel_strings
            actual_total_kwh = recommended_kwh_per_battery * total_batteries
            
            # Convert to Ah for display (at system voltage)
            recommended_ah = int((recommended_kwh_per_battery * 1000) / system_voltage)
            battery_voltage_unit = system_voltage
            
            return {
                'total_capacity_kwh': actual_total_kwh,
                'usable_capacity_kwh': actual_total_kwh * dod,
                'capacity_ah': recommended_ah,
                'recommended_ah': recommended_ah,
                'recommended_kwh': recommended_kwh_per_battery,
                'system_voltage': system_voltage,
                'battery_voltage_unit': battery_voltage_unit,
                'batteries_in_series': batteries_in_series,
                'parallel_strings': parallel_strings,
                'total_batteries': total_batteries,
                'depth_of_discharge': dod,
                'battery_type': battery_type,
                'configuration': f"{parallel_strings}P{batteries_in_series}S" if parallel_strings > 1 else f"{batteries_in_series}S",
                'is_kwh_based': True
            }
        else:
            # Small system - use Ah-based lithium (12V or 24V units)
            # Lithium can come in 12V or 24V units
            # Standard Ah sizes for lithium: 50, 100, 150, 200, 300Ah
            standard_sizes_lithium = [50, 100, 150, 200, 300]
            
            # Calculate needed Ah at 12V base
            capacity_ah = (total_capacity_kwh * 1000) / 12
            recommended_ah = min([s for s in standard_sizes_lithium if s >= capacity_ah], default=300)
            
            # Calculate parallel strings
            if recommended_ah < capacity_ah:
                parallel_strings = int(capacity_ah / recommended_ah) + 1
            else:
                parallel_strings = 1
            
            total_batteries = batteries_in_series * parallel_strings
            actual_total_kwh = (recommended_ah * 12 * parallel_strings) / 1000
            
            return {
                'total_capacity_kwh': actual_total_kwh,
                'usable_capacity_kwh': actual_total_kwh * dod,
                'capacity_ah': capacity_ah,
                'recommended_ah': recommended_ah,
                'system_voltage': system_voltage,
                'battery_voltage_unit': 12,  # Lithium Ah-based are typically 12V units
                'batteries_in_series': batteries_in_series,
                'parallel_strings': parallel_strings,
                'total_batteries': total_batteries,
                'depth_of_discharge': dod,
                'battery_type': battery_type,
                'configuration': f"{parallel_strings}P{batteries_in_series}S" if parallel_strings > 1 else f"{batteries_in_series}S",
                'is_kwh_based': False
            }
    
    else:
        # Lead-Acid or Gel - ALWAYS 12V, max 200Ah
        # Standard sizes: 50, 80, 100, 120, 150, 200Ah
        standard_sizes_lead = [50, 80, 100, 120, 150, 200]
        
        # Calculate needed Ah at 12V
        capacity_ah = (total_capacity_kwh * 1000) / 12
        
        # Find appropriate battery size (max 200Ah)
        recommended_ah = min([s for s in standard_sizes_lead if s >= capacity_ah], default=200)
        
        # If capacity needed exceeds what one 200Ah battery can provide per string,
        # we need parallel strings
        if capacity_ah > 200:
            # Need multiple parallel strings
            parallel_strings = int(capacity_ah / 200) + 1
            recommended_ah = 200  # Use max size
        elif recommended_ah < capacity_ah:
            # Need multiple parallel strings with smaller batteries
            parallel_strings = int(capacity_ah / recommended_ah) + 1
        else:
            parallel_strings = 1
        
        total_batteries = batteries_in_series * parallel_strings
        actual_total_kwh = (recommended_ah * 12 * parallel_strings) / 1000
        
        return {
            'total_capacity_kwh': actual_total_kwh,
            'usable_capacity_kwh': actual_total_kwh * dod,
            'capacity_ah': capacity_ah,
            'recommended_ah': recommended_ah,
            'system_voltage': system_voltage,
            'battery_voltage_unit': 12,  # Lead-Acid/Gel are ALWAYS 12V
            'batteries_in_series': batteries_in_series,
            'parallel_strings': parallel_strings,
            'total_batteries': total_batteries,
            'depth_of_discharge': dod,
            'battery_type': battery_type,
            'configuration': f"{parallel_strings}P{batteries_in_series}S" if parallel_strings > 1 else f"{batteries_in_series}S",
            'is_kwh_based': False
        }




def calculate_battery_cost(battery_specs, battery_type):
    """
    Calculate battery costs based on type and capacity
    
    Kenya market prices (approximate):
    - Lithium: 40,000 - 60,000 KSh/kWh
    - Lead-Acid: 15,000 - 25,000 KSh/kWh
    """
    capacity_kwh = battery_specs['total_capacity_kwh']
    
    if battery_type == 'Lithium':
        cost_per_kwh = 50000  # Mid-range
        cycle_life = 6000
        warranty_years = 10
    else:  # Lead-Acid
        cost_per_kwh = 20000  # Mid-range
        cycle_life = 1500
        warranty_years = 3
    
    initial_cost = capacity_kwh * cost_per_kwh
    
    return {
        'initial_cost_ksh': initial_cost,
        'cost_per_kwh': cost_per_kwh,
        'cycle_life': cycle_life,
        'warranty_years': warranty_years
    }


def calculate_lifecycle_cost(battery_cost_data, battery_specs, daily_cycles, years=25):
    """
    Calculate total cost of ownership over system lifetime
    
    Args:
        battery_cost_data: Initial cost and specs from calculate_battery_cost
        battery_specs: Battery specifications
        daily_cycles: Average charge/discharge cycles per day
        years: Analysis period (default 25 years)
    """
    cycle_life = battery_cost_data['cycle_life']
    initial_cost = battery_cost_data['initial_cost_ksh']
    
    # Calculate number of replacements needed
    total_cycles = daily_cycles * 365 * years
    replacements_needed = int(total_cycles / cycle_life)
    
    # Replacement costs (assume 10% price reduction per replacement)
    total_replacement_cost = sum(
        initial_cost * (0.9 ** i) for i in range(1, replacements_needed + 1)
    )
    
    # Maintenance costs (2% of battery cost per year for Lead-Acid, 0.5% for Lithium)
    maintenance_rate = 0.005 if battery_specs['battery_type'] == 'Lithium' else 0.02
    annual_maintenance = initial_cost * maintenance_rate
    total_maintenance = annual_maintenance * years
    
    # Total lifecycle cost
    total_cost = initial_cost + total_replacement_cost + total_maintenance
    
    # Levelized cost (cost per kWh cycled)
    total_kwh_cycled = battery_specs['usable_capacity_kwh'] * total_cycles
    levelized_cost = total_cost / total_kwh_cycled if total_kwh_cycled > 0 else 0
    
    return {
        'initial_cost': initial_cost,
        'replacements_needed': replacements_needed,
        'replacement_cost': total_replacement_cost,
        'maintenance_cost': total_maintenance,
        'total_lifecycle_cost': total_cost,
        'levelized_cost_per_kwh': levelized_cost,
        'cost_per_year': total_cost / years
    }


def compare_battery_types(backup_energy_kwh, daily_cycles=1, years=25):
    """
    Compare Lithium vs Lead-Acid batteries
    
    Returns:
        dict with comparison data
    """
    comparison = {}
    
    for battery_type in ['Lithium', 'Lead-Acid']:
        # Calculate specs
        specs = calculate_battery_specs(backup_energy_kwh, battery_type)
        cost_data = calculate_battery_cost(specs, battery_type)
        lifecycle = calculate_lifecycle_cost(cost_data, specs, daily_cycles, years)
        
        comparison[battery_type] = {
            'specs': specs,
            'costs': cost_data,
            'lifecycle': lifecycle
        }
    
    # Calculate savings
    lithium_total = comparison['Lithium']['lifecycle']['total_lifecycle_cost']
    lead_acid_total = comparison['Lead-Acid']['lifecycle']['total_lifecycle_cost']
    
    comparison['savings_with_lithium'] = lead_acid_total - lithium_total
    comparison['roi_better'] = 'Lithium' if lithium_total < lead_acid_total else 'Lead-Acid'
    
    return comparison
