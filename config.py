


# ============================================================================
# NASA POWER API CONFIGURATION
# ============================================================================
NASA_POWER_API = {
    'base_url': 'https://power.larc.nasa.gov/api/v1/ag_re/climatology',
    'timeseries_url': 'https://power.larc.nasa.gov/api/v1/ag_re/timeseries',
    'resolution': '0.5 degrees',
    'data_coverage': 'Global',
    'cost': 'Free',
    'documentation': 'https://power.larc.nasa.gov/docs/',
    'available_since': '1984',
    'request_timeout': 30
}

# ============================================================================
# SOLAR PARAMETERS (0.5° resolution available)
# ============================================================================
SOLAR_IRRADIANCE_PARAMS = {
    'ALLSKY_SFC_SW_DWN': {
        'name': 'All-sky Global Horizontal Irradiance (GHI)',
        'unit': 'kWh/m²/day',
        'description': 'Solar irradiance under all sky conditions'
    },
    'CLRSKY_SFC_SW_DWN': {
        'name': 'Clear-sky GHI',
        'unit': 'kWh/m²/day',
        'description': 'Solar irradiance under clear sky conditions'
    },
    'ALLSKY_KT': {
        'name': 'Clearness Index',
        'unit': '0-1 (unitless)',
        'description': 'Ratio of diffuse to extraterrestrial radiation'
    }
}

# ============================================================================
# WEATHER PARAMETERS (0.5° resolution available)
# ============================================================================
WEATHER_PARAMS = {
    'T2M': {
        'name': 'Temperature at 2m',
        'unit': '°C',
        'description': 'Air temperature (affects PV efficiency)'
    },
    'T2M_MAX': {
        'name': 'Maximum Temperature',
        'unit': '°C',
        'description': 'Maximum daily temperature'
    },
    'T2M_MIN': {
        'name': 'Minimum Temperature',
        'unit': '°C',
        'description': 'Minimum daily temperature'
    },
    'RH2M': {
        'name': 'Relative Humidity',
        'unit': '%',
        'description': 'Atmospheric humidity (affects soiling rates)'
    },
    'WS2M': {
        'name': 'Wind Speed at 2m',
        'unit': 'm/s',
        'description': 'Wind speed (affects cooling and dust)'
    }
}

# ============================================================================
# PV SYSTEM EFFICIENCY ASSUMPTIONS
# ============================================================================
PV_EFFICIENCY = {
    'module_efficiency': 0.15,  # 15% typical for modern panels
    'soiling_loss': 0.02,  # 2% annual soiling loss
    'performance_ratio': 0.80,  # 80% PR (includes inverter, wiring, temp losses)
    'temperature_coefficient': -0.0040  # -0.4% per °C above STC (25°C)
}

# ============================================================================
# SYSTEM STATUS
# ============================================================================
SYSTEM_STATUS = {
    'version': '1.2.0',
    'status': 'ACTIVE',
    'last_updated': '2025-11-17',
    'environment': 'PRODUCTION',
    'support': 'https://github.com/Nemick'
}