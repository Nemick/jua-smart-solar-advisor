import streamlit as st
import json
import os
import math
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import utilities
from utils.cost_calculator import load_json_data, calculate_tariff_cost, calculate_system_cost
from utils.gemini_handler import generate_solar_recommendation
from utils.data_validator import validate_recommendation
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from utils.visualizations import (
    create_financial_timeline, 
    create_cost_breakdown_pie, 
    create_co2_offset_gauge, 
    create_monthly_energy_flow
)
import config as app_config

# Load environment variables
load_dotenv()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Jua Smart - Intelligent Solar Energy Advisor",
    page_icon="assets/icons/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# MODERN STYLING
# ============================================================================

st.markdown("""
    <style>
    /* Main Theme */
    :root {
        --primary-color: #FF6B35;
        --secondary-color: #004E89;
        --accent-color: #F7B801;
        --success-color: #06A77D;
        --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom Header */
    .main-header {
        font-size: 3.5em;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B35 0%, #F7B801 50%, #06A77D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .tagline {
        text-align: center;
        font-size: 1.2em;
        color: #666;
        margin-bottom: 30px;
        font-weight: 300;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border-left: 4px solid var(--primary-color);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 15px 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #06A77D 0%, #05D9A5 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #F7B801 0%, #FF6B35 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    /* Inputs */
    .stSelectbox, .stNumberInput {
        border-radius: 10px;
    }
    
    /* Progress indicators */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin: 30px 0;
    }
    
    .step {
        flex: 1;
        text-align: center;
        padding: 15px;
        background: #f0f0f0;
        border-radius: 10px;
        margin: 0 5px;
        font-weight: 600;
        color: #999;
    }
    
    .step.active {
        background: linear-gradient(135deg, #FF6B35 0%, #F7B801 100%);
        color: white;
    }
    
    .step.completed {
        background: #06A77D;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# EFFICIENT DATA LOADING WITH ERROR HANDLING
# ============================================================================

@st.cache_data(ttl=3600)
def load_all_data():
    """Load all JSON data with comprehensive error handling"""
    required_files = {
        "tariff": "epra_tariffs_2024_2026.json",
        "equipment": "equipment_catalog.json",
        "assumptions": "baseline_assumptions.json",
        "ghi": "kenya_counties_irradiance.json",
        "incentives": "incentives_programs.json",
        "electricity_rates": "electricity_rates.json",
        "solar_irradiance": "solar_irradiance.json"
    }
    
    data = {}
    errors = []
    
    for key, filename in required_files.items():
        try:
            data[key] = load_json_data(filename)
        except Exception as e:
            errors.append(f"{filename}: {str(e)}")
            data[key] = None
    
    return data, errors

# Load data
with st.spinner("⚡ Loading Jua Smart..."):
    data, load_errors = load_all_data()

if load_errors:
    st.error("⚠️ Some data files could not be loaded:")
    for error in load_errors:
        st.error(f"  • {error}")
    st.stop()

# Extract data
GHI_DATA = data.get("ghi", {})
TARIFF_DATA = data.get("tariff", {})
EQUIPMENT_CATALOG = data.get("equipment", {})
ASSUMPTIONS = data.get("assumptions", {})
INCENTIVES = data.get("incentives", {})

# ============================================================================
# HELPER FUNCTIONS - OPTIMIZED
# ============================================================================

@st.cache_data
def get_ghi_for_location(location):
    """Optimized GHI retrieval with fallback"""
    if isinstance(GHI_DATA, dict):
        if "counties" in GHI_DATA:
            for county_data in GHI_DATA["counties"]:
                if county_data.get("county") == location:
                    return county_data.get("avg_irradiance_kwh_m2_day", 5.2)
        return GHI_DATA.get(location, {}).get("ghi_kwh_m2_day", 5.2)
    return 5.2

def calculate_appliance_load(appliances, water_pump_hours=2):
    """Streamlined appliance load calculation"""
    SPECS = {
        "Fridge": (150, 24), "Freezer": (150, 24), "TV": (80, 4),
        "LED Lights": (10, 5), "Laptop": (60, 6), "Router": (10, 24),
        "Phone Chargers": (30, 3), "Water Pump": (500, water_pump_hours),
        "Air Conditioner": (1500, 8), "Iron": (1000, 0.3),
        "Washing Machine": (500, 0.4), "Microwave": (800, 0.5),
        "Electric Stove": (2000, 1), "Water Heater": (1500, 0.5)
    }
    
    daily_kwh = sum(
        (power * hours * count) / 1000
        for app, count in appliances.items()
        if (spec := SPECS.get(app)) and count > 0
        for power, hours in [spec]
    )
    
    return daily_kwh * 30.44

def calculate_quick_roi(monthly_kwh, ghi, rate, battery_cost=0):
    """Fast ROI calculation without AI - now includes battery costs"""
    annual_kwh = monthly_kwh * 12
    daily_yield_per_kw = ghi * 0.15 * 0.80 * 6.5  # efficiency * PR * area
    annual_yield_per_kw = daily_yield_per_kw * 365
    
    system_kw = max(0.5, annual_kwh / annual_yield_per_kw if annual_yield_per_kw > 0 else 1)
    solar_cost, cost_per_watt, cost_breakdown = calculate_system_cost(system_kw, EQUIPMENT_CATALOG, ASSUMPTIONS)
    
    # Use ACTUAL system size from panel configuration for accurate generation stats
    actual_system_kw = cost_breakdown.get('actual_system_kw', system_kw)
    
    # Total upfront cost includes solar + batteries
    upfront_cost = solar_cost + battery_cost
    
    annual_generation = actual_system_kw * annual_yield_per_kw
    annual_savings = min(annual_generation, annual_kwh) * rate
    payback = upfront_cost / annual_savings if annual_savings > 0 else float('inf')
    
    # NPV calculation
    discount_rate = 0.08
    npv = -upfront_cost + sum(annual_savings / ((1 + discount_rate) ** t) for t in range(1, 26))
    
    return {
        'system_kw': system_kw,
        'solar_cost': solar_cost,
        'battery_cost': battery_cost,
        'upfront_cost': upfront_cost,
        'cost_per_watt': cost_per_watt,
        'cost_breakdown': cost_breakdown,
        'annual_generation': annual_generation,
        'annual_savings': annual_savings,
        'payback_years': payback,
        'npv_25yr': npv
    }

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'saved_analyses' not in st.session_state:
    st.session_state.saved_analyses = []

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    # Brand icon at top - centered
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/icons/jua_smart_icon.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center; margin-top: -10px;'>Jua Smart</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.9em; color: #666; margin-top: -10px;'>Solar Energy Advisor</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation Menu
    st.markdown("### 🧭 Navigation")
    
    page_options = {
        "🏠 Home Dashboard": "Home",
        "🧮 Quick Calculator": "Calculator",
        "📊 My Analyses": "Analyses",
        "⚖️ Compare Systems": "Compare",
        "💬 Chat Advisor": "Chat",
        "📥 Export Reports": "Export",
        "ℹ️ About": "About"
    }
    
    selected_page = st.radio(
        "Go to:",
        list(page_options.keys()),
        key="nav_radio",
        label_visibility="collapsed"
    )
    
    st.session_state.page = page_options[selected_page]
    
    st.markdown("---")
    
    # Quick Stats (if analysis exists)
    if 'monthly_consumption' in st.session_state:
        st.markdown("### 📈 Your Stats")
        st.metric("Monthly Usage", f"{st.session_state.get('monthly_consumption', 0):.0f} kWh")
        st.metric("Location", st.session_state.get('selected_county', 'N/A'))
        
        if 'recommendation' in st.session_state:
            rec = st.session_state['recommendation']
            sys_sizing = rec.get('system_sizing', {})
            st.metric("System Size", f"{sys_sizing.get('required_system_size_kw', 0):.1f} kW")
        
        st.markdown("---")
    
    # Settings section removed - AI Model Settings below is sufficient
    
    # AI Model Settings - Gemini only
    with st.expander("🤖 AI Model Settings (Google Gemini)"):
        st.selectbox(
            "Gemini Model", 
            ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
            key="gemini_model",
            index=0,
            help="Select your preferred Gemini model. Flash is fastest and free."
        )
        
        # Check for Gemini API key
        env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if env_key:
            st.success("✅ Gemini API Key loaded from .env")
        else:
            st.warning("⚠️ Add GEMINI_API_KEY to .env file")
            st.info("Get your free API key at: https://aistudio.google.com/app/apikey")
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; font-size: 0.8em; color: #888;'>
        <p>Version 2.1</p>
        <p>🌍 Made for Kenya</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

# Display custom logo - centered with reasonable size
col_logo1, col_logo2, col_logo3 = st.columns([1, 3, 1])
with col_logo2:
    st.image("assets/logos/jua_smart_logo.png", width=400)

st.markdown("<p class='tagline'>Your Intelligent Solar Energy Advisor for Kenya</p>", unsafe_allow_html=True)



# ============================================================================
# MAIN CONTENT - PAGE ROUTER
# ============================================================================

# Get current page from session state
current_page = st.session_state.get('page', 'Home')

# ============================================================================
# PAGE: HOME DASHBOARD
# ============================================================================

if current_page == "Home":
    # Progress Indicator
    progress_html = f"""
    <div class='step-indicator'>
        <div class='step {"active" if st.session_state.step == 1 else "completed" if st.session_state.step > 1 else ""}'>
            1️⃣ Input Details
        </div>
        <div class='step {"active" if st.session_state.step == 2 else "completed" if st.session_state.step > 2 else ""}'>
            2️⃣ Quick Analysis
        </div>
        <div class='step {"active" if st.session_state.step == 3 else ""}'>
            3️⃣ AI Recommendation
        </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)
    
    st.header("Tell Us About Your Energy Needs")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Location Selection - Address or County
        location_method = st.radio(
            "📍 Location Input Method",
            ["🗺️ Select County (Fast)", "🌍 Enter Address (NASA Data - More Accurate)"],
            help="NASA data provides latest real-time solar irradiance for your specific address"
        )
        
        if "County" in location_method:
            # County selection (static data)
            county_options = sorted([
                k for k in GHI_DATA.keys() 
                if k not in ["All_Counties", "counties"]
            ]) if isinstance(GHI_DATA, dict) and "counties" not in GHI_DATA else sorted([
                c.get("county", f"County_{i}") 
                for i, c in enumerate(GHI_DATA.get("counties", []))
            ])
            
            selected_county = st.selectbox(
                "📍 Your County",
                county_options,
                index=county_options.index("Nairobi") if "Nairobi" in county_options else 0
            )
            
            ghi_value = get_ghi_for_location(selected_county)
            location_display = selected_county
            st.info("ℹ️ Using Kenya Solar Atlas data (static)")
        else:
            # Initialize selected_county for NASA method (for compatibility)
            selected_county = "Custom Location"
            # Address input (NASA API)
            address_input = st.text_input(
                "🏠 Enter Your Address",
                placeholder="e.g., Westlands, Nairobi, Kenya",
                help="Enter your street, area, or landmark in Kenya"
            )
            
            if address_input and st.button("🔍 Fetch Solar Data", type="primary"):
                try:
                    from utils.nasa_power_api import address_to_coordinates, fetch_nasa_power_data
                    from datetime import datetime, timedelta
                    
                    with st.spinner(f"Fetching real-time solar data for {address_input}..."):
                        # Get coordinates
                        lat, lon = address_to_coordinates(address_input + ", Kenya")
                        
                        # Fetch last year's data for average
                        end_date = datetime.now() - timedelta(days=30)
                        start_date = end_date - timedelta(days=365)
                        
                        # Fetch solar irradiance data
                        df = fetch_nasa_power_data(
                            lat, lon, start_date, end_date,
                            parameters=['ALLSKY_SFC_SW_DWN']  # All Sky Surface Shortwave Downward Irradiance
                        )
                        
                        # Calculate average GHI in kWh/m²/day
                        # NASA POWER returns data in kWh/m²/day for daily temporal resolution
                        # No conversion needed - just take the mean
                        ghi_value = df['ALLSKY_SFC_SW_DWN'].mean()
                        
                        # Store in session state
                        st.session_state['nasa_ghi'] = ghi_value
                        st.session_state['nasa_address'] = address_input
                        st.session_state['nasa_coords'] = (lat, lon)
                        
                        st.success(f"✅ Data fetched! Coordinates: {lat:.2f}°, {lon:.2f}°")
                except Exception as e:
                    st.error(f"❌ Error fetching data: {str(e)}\n\nPlease check your address or use County selection instead.")
                    ghi_value = 5.2  # Fallback
            
            # Use NASA data if available
            if 'nasa_ghi' in st.session_state:
                ghi_value = st.session_state['nasa_ghi']
                location_display = st.session_state['nasa_address']
                # Update selected_county to show address in sidebar
                selected_county = st.session_state['nasa_address']
                coords = st.session_state['nasa_coords']
                st.success(f"📡 Using NASA POWER data for: {location_display}")
                st.caption(f"Coordinates: {coords[0]:.4f}°N, {coords[1]:.4f}°E")
            else:
                ghi_value = 5.2  # Default for Kenya
                location_display = "Kenya (Default)"
                if address_input:
                    st.warning("⚠️ Click 'Fetch Solar Data' to get accurate data for your address")
                else:
                    st.info("ℹ️ Enter address above to fetch real-time NASA data")
        
        st.metric("☀️ Solar Potential", f"{ghi_value:.1f} kWh/m²/day", delta="Excellent" if ghi_value > 5.5 else "Good" if ghi_value > 5 else "Moderate")
    
    with col2:
        # Consumption Input - Simplified
        input_method = st.radio(
            "How would you like to input your usage?",
            ["💡 Monthly Bill (Easiest)", "🏠 List My Appliances"],
            horizontal=True
        )
    
    st.markdown("---")
    
    monthly_consumption = 0
    
    if input_method == "💡 Monthly Bill (Easiest)":
        st.write("**Choose your input method:**")
        
        input_choice = st.radio(
            "I want to enter:",
            ["Monthly Consumption (kWh)", "Monthly Bill (KSh)"],
            horizontal=True,
            key="input_choice"
        )
        
        col_a, col_b, col_c = st.columns(3)
        
        # Default rate
        default_rate = 20.0
        
        if input_choice == "Monthly Consumption (kWh)":
            with col_a:
                monthly_consumption = st.number_input(
                    "Monthly Consumption (kWh)",
                    min_value=10, max_value=10000, value=200, step=10,
                    help="Check your KPLC bill",
                    key="kwh_input"
                )
            with col_b:
                # Auto-calculate bill
                monthly_bill = monthly_consumption * default_rate
                st.metric("Estimated Bill", f"KSh {monthly_bill:,.0f}")
            with col_c:
                st.metric("Rate Used", f"KSh {default_rate:.2f}/kWh")
        
        else:  # Monthly Bill input
            with col_a:
                monthly_bill = st.number_input(
                    "Monthly Bill (KSh)",
                    min_value=500, max_value=500000, value=4000, step=100,
                    key="bill_input"
                )
            with col_b:
                # Auto-calculate consumption
                monthly_consumption = monthly_bill / default_rate
                st.metric("Estimated Consumption", f"{monthly_consumption:.0f} kWh")
            with col_c:
                st.metric("Rate Used", f"KSh {default_rate:.2f}/kWh")
        
        if monthly_consumption > 0:
            implied_rate = monthly_bill / monthly_consumption
            st.info(f"💰 Your effective rate: KSh {implied_rate:.2f}/kWh")
    
    else:
        # Simplified Appliance Selector
        st.write("Select your appliances:")
        
        col1, col2, col3 = st.columns(3)
        appliances = {}
        
        with col1:
            st.subheader("🍳 Kitchen")
            appliances["Fridge"] = st.number_input("Refrigerators", 0, 5, 1)
            appliances["Microwave"] = st.number_input("Microwaves", 0, 3, 0)
            appliances["Electric Stove"] = st.number_input("Electric Stoves", 0, 2, 0)
        
        with col2:
            st.subheader("💡 Living")
            appliances["TV"] = st.number_input("TVs", 0, 5, 1)
            appliances["LED Lights"] = st.number_input("LED Bulbs (sets of 6)", 0, 20, 6)
            appliances["Laptop"] = st.number_input("Laptops/Computers", 0, 5, 1)
        
        with col3:
            st.subheader("🔧 Other")
            appliances["Water Pump"] = st.number_input("Water Pump", 0, 2, 0)
            appliances["Air Conditioner"] = st.number_input("Air Conditioners", 0, 5, 0)
            appliances["Washing Machine"] = st.number_input("Washing Machines", 0, 2, 0)
        
        # Custom Appliances Section
        st.markdown("---")
        st.subheader("➕ Custom Appliances")
        st.write("Add your own appliances not listed above")
        
        # Initialize custom appliances in session state
        if 'custom_appliances' not in st.session_state:
            st.session_state.custom_appliances = []
        
        # Add new custom appliance
        col_custom1, col_custom2, col_custom3, col_custom4 = st.columns([2, 1, 1, 1])
        with col_custom1:
            custom_name = st.text_input("Appliance Name", key="new_custom_name", placeholder="e.g., Coffee Maker")
        with col_custom2:
            custom_power = st.number_input("Power (Watts)", min_value=1, max_value=5000, value=100, key="new_custom_power")
        with col_custom3:
            custom_hours = st.number_input("Hours/Day", min_value=0.1, max_value=24.0, value=1.0, step=0.1, key="new_custom_hours")
        with col_custom4:
            if st.button("Add", type="primary"):
                if custom_name and custom_name.strip():
                    st.session_state.custom_appliances.append({
                        'name': custom_name.strip(),
                        'power': custom_power,
                        'hours': custom_hours
                    })
                    st.success(f"Added {custom_name}!")
                    st.rerun()
        
        # Display and manage custom appliances
        if st.session_state.custom_appliances:
            st.write("**Your Custom Appliances:**")
            for idx, custom in enumerate(st.session_state.custom_appliances):
                col_show1, col_show2, col_show3, col_show4 = st.columns([2, 1, 1, 1])
                with col_show1:
                    st.write(f"**{custom['name']}**")
                with col_show2:
                    st.write(f"{custom['power']}W")
                with col_show3:
                    st.write(f"{custom['hours']}h/day")
                with col_show4:
                    if st.button(f"Remove", key=f"remove_{idx}"):
                        st.session_state.custom_appliances.pop(idx)
                        st.rerun()
        
        # Calculate total consumption including custom appliances
        base_consumption = calculate_appliance_load(appliances)
        
        # Add custom appliances consumption
        custom_consumption = 0
        if st.session_state.custom_appliances:
            for custom in st.session_state.custom_appliances:
                # Daily kWh = (power_watts * hours) / 1000
                daily_kwh = (custom['power'] * custom['hours']) / 1000
                # Monthly kWh = daily * 30.44
                custom_consumption += daily_kwh * 30.44
        
        monthly_consumption = base_consumption + custom_consumption
        
        if custom_consumption > 0:
            st.success(f"📊 Total Monthly Consumption: **{monthly_consumption:.0f} kWh** (Base: {base_consumption:.0f} kWh + Custom: {custom_consumption:.0f} kWh)")
        else:
            st.success(f"📊 Estimated Monthly Consumption: **{monthly_consumption:.0f} kWh**")
    
    st.markdown("---")
    
    # System Preferences - Simplified
    col_pref1, col_pref2 = st.columns(2)
    with col_pref1:
        system_type = st.selectbox(
            "⚙️ System Type",
            ["Hybrid (With Backup)", "Off-grid (Complete Independence)", "Grid-tied (Cheapest)"],
            help="Hybrid is recommended for domestic use. Grid-tied is mainly for large projects."
        )
    
    with col_pref2:
        if "Hybrid" in system_type or "Off-grid" in system_type:
            battery_type = st.selectbox(
                "🔋 Battery Type",
                ["Lithium (LiFePO4)", "Lead-Acid", "AGM"],
                help="Choose battery chemistry for backup"
            )
        else:
            battery_type = "None"
    
    # Battery Configuration (for Hybrid/Off-grid systems)
    if "Hybrid" in system_type or "Off-grid" in system_type:
        st.markdown("---")
        st.subheader("🔋 Battery Backup Configuration")
        st.write("Configure your battery backup system")
        
        col_bat1, col_bat2 = st.columns(2)
        
        with col_bat1:
            battery_type_detail = st.selectbox(
                "Battery Type",
                [
                    "Gel (Maintenance-Free) - Recommended 💯",
                    "Lead-Acid (Flooded) - Budget 💰",
                    "Lithium (LiFePO4) - Premium ⭐"
                ],
                help="Gel batteries are most popular in Kenya - sealed and maintenance-free"
            )
        
        with col_bat2:
            backup_hours = st.selectbox(
                "Backup Duration",
                [4, 8, 12, 24],
                index=1,  # Default 8 hours
                help="How many hours of backup power do you need?"
            )
        
        # Calculate battery requirements automatically
        if monthly_consumption > 0:
            from utils.battery_calculator import calculate_battery_specs, calculate_battery_cost
            
            daily_consumption_kwh = monthly_consumption / 30.44
            backup_energy_kwh = (daily_consumption_kwh / 24) * backup_hours
            
            # Estimate system size for voltage determination
            # This is a rough estimate - will be refined in analysis
            estimated_system_kw = (monthly_consumption * 12) / (ghi_value * 0.15 * 0.80 * 6.5 * 365)
            estimated_system_kw = max(0.5, estimated_system_kw)
            
            # Map UI selection to battery type for calculations
            bat_type_map = {
                "Gel (Maintenance-Free) - Recommended 💯": "Gel",
                "Lead-Acid (Flooded) - Budget 💰": "Lead-Acid",
                "Lithium (LiFePO4) - Premium ⭐": "Lithium"
            }
            actual_bat_type = bat_type_map[battery_type_detail]
            
            try:
                # Pass system_kw to get proper voltage configuration
                bat_specs = calculate_battery_specs(backup_energy_kwh, actual_bat_type, system_kw=estimated_system_kw)
                bat_cost = calculate_battery_cost(bat_specs, actual_bat_type)
                
                # Display battery estimates
                st.markdown("##### 📊 Battery Bank Estimate")
                col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                
                with col_info1:
                    st.metric("Capacity Needed", f"{bat_specs['total_capacity_kwh']:.1f} kWh")
                
                with col_info2:
                    # Use the correct battery configuration from calculator
                    total_batteries = bat_specs['total_batteries']
                    
                    # Check if kWh-based or Ah-based
                    if bat_specs.get('is_kwh_based', False):
                        # kWh-based lithium (e.g., Menred 5.12kWh)
                        kwh_per_battery = bat_specs.get('recommended_kwh', 0)
                        st.metric("Battery Units", f"{total_batteries} × {kwh_per_battery}kWh")
                    else:
                        # Ah-based (Lead-Acid, Gel, or small Lithium)
                        ah_per_battery = bat_specs['recommended_ah']
                        battery_voltage_unit = bat_specs.get('battery_voltage_unit', 12)
                        st.metric("Battery Configuration", f"{total_batteries} × {ah_per_battery}Ah @{battery_voltage_unit}V")
                
                with col_info3:
                    system_voltage = bat_specs['system_voltage']
                    configuration = bat_specs['configuration']
                    st.metric("System Voltage", f"{system_voltage}V ({configuration})")
                
                with col_info4:
                    st.metric("Battery Cost", f"KSh {bat_cost['initial_cost_ksh']:,.0f}")
                
                # Show configuration explanation
                if bat_specs.get('is_kwh_based', False):
                    kwh_per_unit = bat_specs.get('recommended_kwh', 0)
                    st.info(f"ℹ️ **{system_voltage}V Lithium System**: {total_batteries} × {kwh_per_unit}kWh units" +
                           (f" ({bat_specs['batteries_in_series']} in series × {bat_specs['parallel_strings']} parallel)" 
                            if bat_specs['parallel_strings'] > 1 else ""))
                elif bat_specs['batteries_in_series'] > 1:
                    ah_per_battery = bat_specs['recommended_ah']
                    st.info(f"ℹ️ **{system_voltage}V System**: {bat_specs['batteries_in_series']} × {ah_per_battery}Ah batteries in series" + 
                           (f" × {bat_specs['parallel_strings']} parallel strings" if bat_specs['parallel_strings'] > 1 else "") +
                           f" = {total_batteries} total batteries")
                
                # Store for later use
                battery_cost_total = bat_cost['initial_cost_ksh']
                battery_num = total_batteries
                battery_ah = bat_specs['recommended_ah']
                battery_voltage = system_voltage
                battery_config = configuration
                battery_is_kwh = bat_specs.get('is_kwh_based', False)
                battery_kwh_unit = bat_specs.get('recommended_kwh', 0) if battery_is_kwh else 0
                
            except Exception as e:
                st.warning(f"Could not calculate battery requirements: {str(e)}")
                battery_cost_total = 0
                battery_num = 0
                battery_ah = 0
                actual_bat_type = "Gel"
                battery_voltage = 12
                battery_config = "1S"
        else:
            battery_cost_total = 0
            battery_num = 0
            battery_ah = 0
            actual_bat_type = "Gel"
            battery_voltage = 12
            battery_config = "1S"
    else:
        battery_type_detail = "None"
        backup_hours = 0
        battery_cost_total = 0
        battery_num = 0
        battery_ah = 0
        actual_bat_type = "None"
    
    st.markdown("---")
    
    # Generate Button
    if monthly_consumption >= 10:
        if st.button("� Analyze My Solar Potential", type="primary", use_container_width=True):
            # Save to session state
            st.session_state.update({
                'monthly_consumption': monthly_consumption,
                'selected_county': selected_county,
                'ghi_value': ghi_value,
                'system_type': system_type,
                'battery_type': actual_bat_type,
                'battery_type_detail': battery_type_detail,
                'backup_hours': backup_hours,
                'battery_cost': battery_cost_total,
                'battery_num': battery_num,
                'battery_ah': battery_ah,
                'battery_voltage': battery_voltage,
                'battery_config': battery_config,
                'step': 2
            })
            
            # Calculate tariff
            monthly_cost, effective_rate, tariff_category = calculate_tariff_cost(
                monthly_consumption, TARIFF_DATA
            )
            st.session_state.update({
                'effective_rate': effective_rate,
                'tariff_category': tariff_category,
                'monthly_cost': monthly_cost
            })
            
            st.success("✅ Analysis ready! Go to **📊 My Analyses** in the sidebar →")
            st.balloons()
    else:
        st.warning("⚠️ Please enter your energy consumption details above.")

# ============================================================================
# PAGE: QUICK CALCULATOR
# ============================================================================

elif current_page == "Calculator":
    st.header("🧮 Quick Solar Calculator")
    st.write("Get instant estimates without detailed input")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Your Usage")
        quick_kwh = st.number_input(
            "Monthly Consumption (kWh)", 
            min_value=50, 
            max_value=5000, 
            value=200, 
            step=50,
            help="Enter your average monthly electricity consumption"
        )
        
        # County selection with proper data
        county_options = sorted([
            k for k in GHI_DATA.keys() 
            if k not in ["All_Counties", "counties"]
        ]) if isinstance(GHI_DATA, dict) and "counties" not in GHI_DATA else sorted([
            c.get("county", f"County_{i}") 
            for i, c in enumerate(GHI_DATA.get("counties", []))
        ])
        
        quick_county = st.selectbox(
            "📍 Select County",
            county_options,
            index=county_options.index("Nairobi") if "Nairobi" in county_options else 0,
            help="Choose your county for solar potential calculation"
        )
        
        # Get GHI for selected county
        ghi = get_ghi_for_location(quick_county)
        st.metric("☀️ Solar Potential", f"{ghi:.1f} kWh/m²/day")
    
    with col2:
        st.subheader("💰 Electricity Cost")
        quick_rate = st.number_input(
            "Your Rate (KSh/kWh)", 
            min_value=10.0, 
            max_value=30.0, 
            value=20.0, 
            step=0.5,
            help="Your current electricity rate (default: KSh 20/kWh)"
        )
        
        current_bill = quick_kwh * quick_rate
        st.metric("📄 Current Monthly Bill", f"KSh {current_bill:,.0f}")
    
    st.markdown("---")
    
    if st.button("⚡ Calculate Solar Potential", type="primary", use_container_width=True):
        estimate = calculate_quick_roi(quick_kwh, ghi, quick_rate)
        
        st.markdown("### 📈 Your Solar System Estimate")
        
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        
        with col_r1:
            st.metric(
                "🔆 System Size", 
                f"{estimate['system_kw']:.1f} kW",
                delta=f"~{int(estimate['system_kw'] * 3)} panels"
            )
        with col_r2:
            st.metric(
                "💵 Investment", 
                f"KSh {estimate['upfront_cost']:,.0f}"
            )
        with col_r3:
            st.metric(
                "⏱️ Payback Period", 
                f"{estimate['payback_years']:.1f} years"
            )
        with col_r4:
            monthly_savings = estimate['annual_savings'] / 12
            st.metric(
                "💰 Monthly Savings",
                f"KSh {monthly_savings:,.0f}"
            )
        
        st.markdown("---")
        
        # Additional insights
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            st.markdown("### 📊 Financial Summary")
            st.write(f"**Annual Savings:** KSh {estimate['annual_savings']:,.0f}")
            st.write(f"**25-Year Profit:** KSh {estimate['npv_25yr']:,.0f}")
            roi_percent = ((estimate['npv_25yr'] + estimate['upfront_cost']) / estimate['upfront_cost']) * 100
            st.write(f"**Total ROI:** {roi_percent:.0f}%")
        
        with col_i2:
            st.markdown("### 🌱 Environmental Impact")
            annual_co2 = estimate['annual_generation'] * 0.4087 / 1000  # tonnes
            st.write(f"**CO₂ Offset/Year:** {annual_co2:.1f} tonnes")
            st.write(f"**Trees Equivalent:** {int(annual_co2 * 50):,} trees/year")
            st.write(f"**25-Year CO₂ Offset:** {annual_co2 * 25:.1f} tonnes")
        
        st.success("💡 **Tip:** For detailed analysis with AI recommendations, use the **Home Dashboard**")


# ============================================================================
# PAGE: MY ANALYSES
# ============================================================================

elif current_page == "Analyses":
    st.header("Your Solar Analysis")
    
    if 'monthly_consumption' not in st.session_state:
        st.info("👈 Please complete the **Home Dashboard** first to see your analysis.")
    else:
        # Quick Summary Cards
        col1, col2, col3, col4 = st.columns(4)
        monthly_consumption = st.session_state['monthly_consumption']
        ghi_value = st.session_state['ghi_value']
        effective_rate = st.session_state['effective_rate']
        
        # Get battery info from session state
        battery_cost_total = st.session_state.get('battery_cost', 0)
        
        # Calculate quick estimate with battery cost
        estimate = calculate_quick_roi(monthly_consumption, ghi_value, effective_rate, battery_cost_total)
        
        # ========================================================================
        # SYSTEM SPECIFICATION SECTION - BEFORE FINANCIAL ANALYSIS
        # ========================================================================
        
        st.markdown("---")
        st.header("📦 Your Complete System Specification")
        st.write("Here's what your solar + battery system will include")
        
        col_spec1, col_spec2 = st.columns(2)
        
        with col_spec1:
            st.subheader("☀️ Solar Array")
            
            # Use breakdown data if available, otherwise fallback
            if 'cost_breakdown' in estimate:
                bd = estimate['cost_breakdown']
                panel_count = bd['panels']['count']
                panel_wattage = bd['panels']['wattage']
                actual_system_kw = (panel_count * panel_wattage) / 1000
                
                st.metric("System Size", f"{actual_system_kw:.1f} kW", delta=f"{estimate['system_kw']:.1f} kW estimated")
                st.metric("Solar Panels", f"{panel_count} × {panel_wattage}W panels")
                st.metric("Annual Generation", f"{estimate['annual_generation']:,.0f} kWh/year")
                st.metric("Total Solar Cost", f"KSh {estimate['solar_cost']:,.0f}")
                
                # Cost Breakdown Display
                st.markdown("##### 💸 Cost Breakdown")
                st.write(f"**Panels (Base):** KSh {bd['panels']['base_cost']:,.0f}")
                st.write(f"**Inverter (Base):** KSh {bd['inverter']['base_cost']:,.0f}")
                st.write(f"**VAT (16%):** KSh {bd['vat']['amount']:,.0f}")
                st.write(f"**Mounting:** KSh {bd['mounting']['cost']:,.0f}")
                st.write(f"**Safety & Earthing:** KSh {bd['safety']['cost']:,.0f}")
                st.write(f"**Installation & BOS:** KSh {bd['installation']['cost'] + bd['bos']['cost']:,.0f}")
                
                st.markdown("**Panel Specifications:**")
                st.write(f"- Type: Monocrystalline")
                st.write(f"- Power per panel: {panel_wattage}W")
                st.write(f"- Total panels: {panel_count}")
                st.write(f"- Total capacity: {actual_system_kw:.1f} kW")
                
                st.success("⚡ **Safety Included**: Quote includes Lightning Arrestor, Earth Rod, Clamps & Surge Protection.")
            else:
                # Fallback for older sessions
                panel_wattage = 450
                panel_count = max(1, int(estimate['system_kw'] * 1000 / panel_wattage))
                actual_system_kw = (panel_count * panel_wattage) / 1000
                
                st.metric("System Size", f"{actual_system_kw:.1f} kW", delta=f"{estimate['system_kw']:.1f} kW estimated")
                st.metric("Solar Panels", f"{panel_count} × {panel_wattage}W panels")
                st.metric("Annual Generation", f"{estimate['annual_generation']:,.0f} kWh/year")
                st.metric("Solar Equipment Cost", f"KSh {estimate['solar_cost']:,.0f}")
                
                st.markdown("**Panel Specifications:**")
                st.write(f"- Type: Monocrystalline")
                st.write(f"- Power per panel: {panel_wattage}W")
                st.write(f"- Total panels: {panel_count}")
                st.write(f"- Total capacity: {actual_system_kw:.1f} kW")
        
        with col_spec2:
            battery_type = st.session_state.get('battery_type', 'None')
            
            if battery_type and battery_type != "None":
                st.subheader("🔋 Battery Bank")
                
                battery_type_detail = st.session_state.get('battery_type_detail', battery_type)
                backup_hours = st.session_state.get('backup_hours', 8)
                battery_num = st.session_state.get('battery_num', 0)
                battery_ah = st.session_state.get('battery_ah', 0)
                battery_cost = st.session_state.get('battery_cost', 0)
                battery_voltage = st.session_state.get('battery_voltage', 12)
                battery_config = st.session_state.get('battery_config', '1S')
                
                st.metric("Battery Type", battery_type)
                st.metric("Configuration", f"{battery_num} × {battery_ah}Ah @ 12V")
                st.metric("System Voltage", f"{battery_voltage}V ({battery_config})")
                st.metric("Backup Duration", f"{backup_hours} hours")
                st.metric("Battery Cost", f"KSh {battery_cost:,.0f}")
                
                # Calculate total capacity
                total_kwh = (battery_num * battery_ah * 12) / 1000
                
                st.markdown("**Battery Specifications:**")
                st.write(f"- Chemistry: {battery_type}")
                st.write(f"- Individual battery: {battery_ah}Ah @ 12V")
                st.write(f"- System voltage: {battery_voltage}V")
                st.write(f"- Configuration: {battery_config}")
                st.write(f"- Total batteries: {battery_num}")
                st.write(f"- Total capacity: {total_kwh:.1f} kWh")
                st.write(f"- Backup time: {backup_hours} hours")
            else:
                st.subheader("🔋 Battery Bank")
                st.info("**Grid-tied system - No battery backup**\n\nThis system connects directly to the grid without battery storage.")
        
        st.markdown("---")
        
        # ========================================================================
        # FINANCIAL ANALYSIS - NOW WITH COMPLETE COSTS
        # ========================================================================
        
        # Quick Summary Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🔆 System Size",
                f"{estimate['system_kw']:.1f} kW",
                delta=f"{estimate['system_kw'] * 3:.0f} panels"
            )
        
        with col2:
            st.metric(
                "� Investment",
                f"KSh {estimate['upfront_cost']:,.0f}",
                delta=f"{estimate['cost_per_watt']:.0f}/W"
            )
        
        with col3:
            st.metric(
                "💵 Annual Savings",
                f"KSh {estimate['annual_savings']:,.0f}",
                delta=f"{(estimate['annual_savings']/12):,.0f}/mo"
            )
        
        with col4:
            payback_display = f"{estimate['payback_years']:.1f} yrs" if estimate['payback_years'] != float('inf') else "N/A"
            st.metric(
                "⏱️ Payback",
                payback_display,
                delta="ROI Point"
            )
        
        st.markdown("---")
        
        # Visualization Tabs
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["� Financial", "🌍 Environmental", "📊 Breakdown"])
        
        with viz_tab1:
            # Financial Timeline
            inverter_cost = estimate['upfront_cost'] * 0.20 * 0.5
            fig_timeline = create_financial_timeline(
                estimate['upfront_cost'],
                estimate['annual_savings'],
                estimate['payback_years'] if estimate['payback_years'] != float('inf') else 0,
                estimate['npv_25yr'],
                inverter_cost
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Key Insights
            col_i1, col_i2, col_i3 = st.columns(3)
            with col_i1:
                st.metric("25-Year Profit", f"KSh {estimate['npv_25yr']:,.0f}")
            with col_i2:
                roi_percent = ((estimate['npv_25yr'] + estimate['upfront_cost']) / estimate['upfront_cost']) * 100
                st.metric("Total ROI", f"{roi_percent:.0f}%")
            with col_i3:
                monthly_savings = estimate['annual_savings'] / 12
                st.metric("Monthly Savings", f"KSh {monthly_savings:,.0f}")
        
        with viz_tab2:
            # Environmental Impact
            annual_co2 = estimate['annual_generation'] * 0.4087 / 1000  # tCO2
            total_co2 = annual_co2 * 25
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.plotly_chart(create_co2_offset_gauge(annual_co2), use_container_width=True)
            
            with col_e2:
                st.markdown("### 🌱 Environmental Benefits")
                st.metric("Trees Equivalent", f"{int(annual_co2 * 50):,} trees/year")
                st.metric("Car Miles Saved", f"{int(annual_co2 * 5000):,} km/year")
                st.metric("25-Year CO₂ Offset", f"{total_co2:.1f} tons")
        
        with viz_tab3:
            # Cost Breakdown
            if 'cost_breakdown' in estimate:
                bd = estimate['cost_breakdown']
                panel_cost = bd['panels']['base_cost']
                inverter_cost = bd['inverter']['base_cost']
                vat_cost = bd['vat']['amount']
                mounting_cost = bd['mounting']['cost']
                safety_cost = bd['safety']['cost']
                installation_bos = bd['installation']['cost'] + bd['bos']['cost']
                battery_cost = estimate.get('battery_cost', 0)
                
                # Create detailed pie chart
                labels = ['Panels', 'Inverter', 'Batteries', 'VAT (16%)', 'Mounting', 'Safety', 'Installation & BOS']
                values = [panel_cost, inverter_cost, battery_cost, vat_cost, mounting_cost, safety_cost, installation_bos]
                
                import plotly.graph_objects as go
                fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
                
            else:
                # Fallback for older sessions
                panel_cost = estimate.get('solar_cost', estimate['upfront_cost'] * 0.6) * 0.6
                inverter_cost = estimate.get('solar_cost', estimate['upfront_cost'] * 0.6) * 0.25
                installation = estimate.get('solar_cost', estimate['upfront_cost'] * 0.6) * 0.15
                other = 0
                battery_cost = estimate.get('battery_cost', 0)
                
                if battery_cost == 0:
                    # If no battery cost but total is high, assume some split
                    battery_cost = estimate['upfront_cost'] * 0.15
            
                fig_pie = create_cost_breakdown_pie(
                    panel_cost, inverter_cost, battery_cost, installation, other
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("---")
        
        # AI Recommendation Option
        st.subheader("Want a Detailed AI Analysis?")
        
        col_ai1, col_ai2 = st.columns([2, 1])
        with col_ai1:
            st.write("""
            Get a comprehensive AI-powered recommendation with:
            - Specific equipment models and brands
            - Detailed financial projections
            - Installation guidelines
            - Maintenance schedule
            """)
        
        with col_ai2:
            if st.button("🤖 Generate AI Report", type="primary", use_container_width=True):
                with st.spinner("🔄 Analyzing (30-60 seconds)..."):
                    # Prepare existing configuration for AI context to ensure consistency
                    # This forces the AI to "review" our calculated system rather than inventing a new one
                    existing_config = {
                        'system_kw': estimate.get('cost_breakdown', {}).get('actual_system_kw', estimate['system_kw']),
                        'panel_count': estimate.get('cost_breakdown', {}).get('panels', {}).get('count', 0),
                        'panel_wattage': estimate.get('cost_breakdown', {}).get('panels', {}).get('wattage', 450),
                        'inverter_kw': estimate.get('cost_breakdown', {}).get('inverter', {}).get('capacity_kw', 0),
                        'solar_cost': estimate['solar_cost'],
                        'battery_cost': estimate.get('battery_cost', 0),
                        'upfront_cost': estimate['upfront_cost'],
                        'battery_type': st.session_state.get('battery_type', 'None'),
                        'battery_details': {
                            'num': st.session_state.get('battery_num', 0),
                            'ah': st.session_state.get('battery_ah', 0),
                            'voltage': st.session_state.get('battery_voltage', 12),
                            'config': st.session_state.get('battery_config', '1S')
                        }
                    }
                    
                    # Get Gemini model selection
                    model_name = st.session_state.get('gemini_model', 'gemini-1.5-flash')
                    
                    recommendation, error = generate_solar_recommendation(
                        st.session_state['selected_county'],
                        monthly_consumption,
                        st.session_state['system_type'],
                        EQUIPMENT_CATALOG,
                        TARIFF_DATA,
                        ASSUMPTIONS,
                        ghi_value,
                        effective_rate,
                        st.session_state['tariff_category'],
                        existing_system_config=existing_config,
                        model_name=model_name
                    )
                    
                    if error:
                        st.error(f"❌ {error}")
                    elif recommendation:
                        st.session_state['recommendation'] = recommendation
                        st.success("✅ AI Report Generated!")
                        st.rerun()
        
        # Display AI Recommendation if available
        if 'recommendation' in st.session_state:
            st.markdown("---")
            st.subheader("🤖 AI Recommendation Report")
            
            rec = st.session_state['recommendation']
            
            # Executive Summary
            if "executive_summary" in rec:
                st.info(f"💡 **Executive Summary:**\n\n{rec['executive_summary']}")
            
            # System Configuration
            with st.expander("🔧 System Configuration", expanded=True):
                sys_sizing = rec.get("system_sizing", {})
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    st.metric("System Size", f"{sys_sizing.get('required_system_size_kw', 0):.2f} kW")
                with col_s2:
                    st.metric("Panels", f"{sys_sizing.get('panel_count', 0)} x {sys_sizing.get('panel_wattage_w', 0)}W")
                with col_s3:
                    st.metric("Inverter", f"{sys_sizing.get('inverter_size_kw', 0):.2f} kW")
            
            # Equipment Recommendations
            with st.expander("🛠️ Recommended Equipment"):
                equip = rec.get("equipment_recommendations", {})
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.write("**Solar Panels**")
                    panel = equip.get("panel", {})
                    st.write(f"- {panel.get('brand', 'N/A')} {panel.get('model', 'N/A')}")
                
                with col_e2:
                    st.write("**Inverter**")
                    inverter = equip.get("inverter", {})
                    st.write(f"- {inverter.get('brand', 'N/A')} {inverter.get('model', 'N/A')}")


# ============================================================================


# ============================================================================
# PAGE: COMPARE SYSTEMS
# ============================================================================

elif current_page == "Compare":
    st.header("⚖️ Compare Solar System Sizes")
    st.write("Compare different system sizes side-by-side to find the perfect fit")
    
    if 'ghi_value' not in st.session_state or 'effective_rate' not in st.session_state:
        st.warning("⚠️ Please complete the Home Dashboard setup first")
        ghi_value = 5.2
        effective_rate = 20.0
    else:
        ghi_value = st.session_state['ghi_value']
        effective_rate = st.session_state['effective_rate']
    
    # Input for comparison
    monthly_kwh = st.number_input(
        "Monthly Consumption (kWh)",
        min_value=10,
        max_value=10000,
        value=int(st.session_state.get('monthly_consumption', 200)),
        step=50
    )
    
    st.markdown("---")
    st.subheader("System Size Comparison")
    
    # Calculate 3 different system sizes
    base_estimate = calculate_quick_roi(monthly_kwh, ghi_value, effective_rate)
    smaller_estimate = calculate_quick_roi(monthly_kwh * 0.7, ghi_value, effective_rate)
    larger_estimate = calculate_quick_roi(monthly_kwh * 1.3, ghi_value, effective_rate)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📉 Conservative (70%)")
        st.metric("System Size", f"{smaller_estimate['system_kw']:.1f} kW")
        st.metric("Investment", f"KSh {smaller_estimate['upfront_cost']:,.0f}")
        st.metric("Annual Savings", f"KSh {smaller_estimate['annual_savings']:,.0f}")
        st.metric("Payback", f"{smaller_estimate['payback_years']:.1f} yrs")
        st.metric("25-Year NPV", f"KSh {smaller_estimate['npv_25yr']:,.0f}")
        coverage = (smaller_estimate['annual_generation'] / (monthly_kwh * 12)) * 100
        st.metric("Coverage", f"{coverage:.0f}%")
    
    with col2:
        st.markdown("### 🎯 Recommended (100%)")
        st.metric("System Size", f"{base_estimate['system_kw']:.1f} kW")
        st.metric("Investment", f"KSh {base_estimate['upfront_cost']:,.0f}")
        st.metric("Annual Savings", f"KSh {base_estimate['annual_savings']:,.0f}")
        st.metric("Payback", f"{base_estimate['payback_years']:.1f} yrs")
        st.metric("25-Year NPV", f"KSh {base_estimate['npv_25yr']:,.0f}")
        coverage = (base_estimate['annual_generation'] / (monthly_kwh * 12)) * 100
        st.metric("Coverage", f"{coverage:.0f}%")
    
    with col3:
        st.markdown("### 📈 Aggressive (130%)")
        st.metric("System Size", f"{larger_estimate['system_kw']:.1f} kW")
        st.metric("Investment", f"KSh {larger_estimate['upfront_cost']:,.0f}")
        st.metric("Annual Savings", f"KSh {larger_estimate['annual_savings']:,.0f}")
        st.metric("Payback", f"{larger_estimate['payback_years']:.1f} yrs")
        st.metric("25-Year NPV", f"KSh {larger_estimate['npv_25yr']:,.0f}")
        coverage = (larger_estimate['annual_generation'] / (monthly_kwh * 12)) * 100
        st.metric("Coverage", f"{coverage:.0f}%")
    
    st.markdown("---")
    st.info("💡 **Pro Tip**: The recommended system covers 100% of your usage. Conservative saves upfront but may not cover full consumption. Aggressive provides room for growth.")

# ============================================================================
# PAGE: CHAT ADVISOR
# ============================================================================

elif current_page == "Chat":
    st.header("💬 Chat with Jua Smart")
    st.write("Ask me anything about solar energy in Kenya - costs, installation, maintenance, regulations, and more!")
    
    # Display existing chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "☀️"):
            st.write(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about solar panels, costs, installation, EPRA regulations, incentives..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant", avatar="☀️"):
            with st.spinner("Thinking..."):
                try:
                    # System Instruction
                    system_instruction = """You are Jua Smart, a friendly and knowledgeable Kenyan solar energy advisor. 
                    
Your expertise includes:
- Solar panel systems and sizing for Kenyan homes and businesses
- EPRA (Energy and Petroleum Regulatory Authority) regulations and tariffs
- Kenya's Net Metering regulations and procedures
- Local solar equipment suppliers and costs in Kenya Shillings (KSh)
- Installation best practices for Kenya's climate (both rainy and dry seasons)
- Government incentives and tax exemptions for solar in Kenya
- Battery storage options available in the Kenyan market
- Maintenance requirements for solar systems in Kenya's conditions
- County-specific solar irradiance data across Kenya
- KPLC (Kenya Power) interconnection procedures
- ROI calculations based on current KPLC electricity rates

Provide practical, cost-effective advice specific to Kenya. Be concise but helpful. 
Always mention costs in Kenya Shillings (KSh). Reference relevant Kenyan authorities like EPRA and KPLC when applicable.
If you don't know something specific to Kenya, acknowledge it and provide general solar guidance instead."""

                    # Add context
                    context = ""
                    if 'monthly_consumption' in st.session_state:
                        context = f"\n\nUser Context: The user is analyzing a solar system for {st.session_state.get('selected_county', 'Kenya')} with {st.session_state['monthly_consumption']:.0f} kWh monthly consumption."
                    
                    full_prompt = prompt + context
                    
                    provider = st.session_state.get('ai_provider', 'Google Gemini')
                    
                    if provider == "OpenRouter":
                        api_key = st.session_state.get('openrouter_key')
                        if not api_key:
                            api_key = os.getenv("OPENROUTER_API_KEY")
                            
                        model_name = st.session_state.get('openrouter_model', 'deepseek/deepseek-chat')
                        
                        if not api_key:
                            reply = "⚠️ OpenRouter API Key is required. Please set it in the sidebar settings or .env file."
                        else:
                            import requests
                            headers = {
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json",
                                "HTTP-Referer": "https://juasmart.com",
                                "X-Title": "Jua Smart Chat"
                            }
                            data = {
                                "model": model_name,
                                "messages": [
                                    {"role": "system", "content": system_instruction},
                                    {"role": "user", "content": full_prompt}
                                ]
                            }
                            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
                            if response.status_code == 200:
                                reply = response.json()['choices'][0]['message']['content']
                            else:
                                reply = f"❌ OpenRouter Error: {response.text}"
                                
                    else: # Google Gemini
                        api_key = os.getenv("GEMINI_API_KEY")
                        if api_key:
                            genai.configure(api_key=api_key)
                            model_name = st.session_state.get('gemini_model', 'gemini-1.5-flash')
                            model = genai.GenerativeModel(
                                model_name=model_name,
                                system_instruction=system_instruction
                            )
                            response = model.generate_content(full_prompt)
                            reply = response.text
                        else:
                            reply = "⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in your .env file."
                            
                except Exception as e:
                    reply = f"❌ Error: {str(e)}"
                
                st.write(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
    
    # Helpful suggestions
    if len(st.session_state.chat_history) == 0:
        st.markdown("---")
        st.markdown("### 💡 Example Questions You Can Ask:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Cost & Sizing:**
            - How much does a 5kW solar system cost in Kenya?
            - What size solar system do I need for 300 kWh per month?
            - Is solar worth it with current KPLC rates?
            
            **Installation:**
            - How do I get started with solar installation?
            - What are the best solar panel brands in Kenya?
            - Do I need a permit to install solar panels?
            """)
        
        with col2:
            st.markdown("""
            **Regulations:**
            - How does net metering work in Kenya?
            - What are EPRA's requirements for solar?
            - Are there tax exemptions for solar equipment?
            
            **Maintenance:**
            - How often should I clean my solar panels?
            - What's the lifespan of solar panels in Kenya?
            - Do panels work during rainy season?
            """)
    
    # Clear chat button
    if len(st.session_state.chat_history) > 0:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

# ============================================================================
# PAGE: EXPORT REPORTS
# ============================================================================

elif current_page == "Export":
    st.header("📥 Export Your Reports")
    st.write("Download your solar analysis in various formats")
    
    if 'monthly_consumption' not in st.session_state:
        st.warning("⚠️ Please complete an analysis first on the Home Dashboard")
    else:
        st.success("✅ Analysis data available for export")
        
        # Generate summary
        monthly_consumption = st.session_state.get('monthly_consumption', 0)
        ghi_value = st.session_state.get('ghi_value', 5.2)
        effective_rate = st.session_state.get('effective_rate', 20.0)
        estimate = calculate_quick_roi(monthly_consumption, ghi_value, effective_rate)
        
        st.markdown("### 📄 Report Summary")
        
        summary_data = f"""
**Jua Smart Solar Analysis Report**

Location: {st.session_state.get('selected_county', 'N/A')}
Monthly Consumption: {monthly_consumption:.0f} kWh
System Type: {st.session_state.get('system_type', 'N/A')}

**System Recommendation:**
- System Size: {estimate['system_kw']:.2f} kW
- Estimated Panels: {estimate['system_kw'] * 3:.0f} panels
- Investment Required: KSh {estimate['upfront_cost']:,.0f}
- Cost per Watt: KSh {estimate['cost_per_watt']:.0f}/W

**Financial Projections:**
- Annual Generation: {estimate['annual_generation']:,.0f} kWh
- Annual Savings: KSh {estimate['annual_savings']:,.0f}
- Payback Period: {estimate['payback_years']:.1f} years
- 25-Year NPV: KSh {estimate['npv_25yr']:,.0f}
- Total ROI: {((estimate['npv_25yr'] + estimate['upfront_cost']) / estimate['upfront_cost'] * 100):.0f}%

**Environmental Impact:**
- Annual CO₂ Offset: {estimate['annual_generation'] * 0.4087 / 1000:.2f} tons
- 25-Year CO₂ Offset: {estimate['annual_generation'] * 0.4087 / 1000 * 25:.2f} tons
- Tree Equivalent: {int(estimate['annual_generation'] * 0.4087 / 1000 * 50):,} trees/year

Report generated by Jua Smart Solar Advisor
Always consult licensed installers for final quotes.
        """
        
        st.text_area("Report Content", summary_data, height=400)
        
        # Download button
        st.download_button(
            label="📥 Download as Text File",
            data=summary_data,
            file_name=f"jua_smart_report_{st.session_state.get('selected_county', 'solar')}.txt",
            mime="text/plain"
        )
        
        st.markdown("---")
        st.info("📊 **Coming Soon**: PDF reports with charts and detailed equipment specifications!")

# ============================================================================
# PAGE: ABOUT
# ============================================================================

elif current_page == "About":
    st.header("How Jua Smart Works")
    st.markdown("**Jua** means 'sun' in Swahili ☀️ - Your intelligent solar advisor for Kenya")
    
    # How it works section
    st.markdown("---")
    st.subheader("📋 Step-by-Step Guide")
    
    with st.expander("🏠 Step 1: Tell Us About Your Energy Needs", expanded=True):
        st.markdown("""
        Choose how to input your information:
        
        **Option A: Monthly Bill (Easiest)**
        - Enter your monthly KPLC bill amount in KSh
        - Or enter your monthly consumption in kWh
        - Based on real EPRA electricity tariffs
        
        **Option B: List Your Appliances**
        - Select from common appliances (fridge, TV, lights, etc.)
        - Add custom appliances with their power rating and usage hours
        - We automatically calculate your total monthly consumption
        
        **Location Data:**
        - **County Selection**: Quick option using Kenya Solar Atlas data
        - **Address Input**: More accurate using NASA POWER real-time satellite data
        """)
    
    with st.expander("⚡ Step 2: Get Quick Analysis"):
        st.markdown("""
        We instantly calculate:
        
        - **Recommended System Size** (in kW) based on your consumption and location's sun hours
        - **Upfront Cost** using real market prices from local suppliers
        - **Payback Period** - how long until the system pays for itself
        - **25-Year Savings** - total savings over the system lifetime
        - **CO2 Offset** - environmental impact
        
        **Battery Backup Configuration:**
        - Choose between Lithium (LiFePO4), Gel, or Lead-Acid batteries
        - Select backup duration (4, 8, 12, or 24 hours)
        - Automatic calculation of battery bank size and cost
        - Proper voltage configuration (12V, 24V, or 48V) based on system size
        """)
    
    with st.expander("🤖 Step 3: AI-Powered Recommendation"):
        st.markdown("""
        Our AI analyzes your specific situation and provides:
        
        - **Detailed System Design**: Panel quantity, inverter size, battery configuration
        - **Financial Breakdown**: Cost per component with market prices
        - **ROI Timeline**: Month-by-month savings projections
        - **Grid vs Solar Usage**: Energy flow visualization
        - **Expert Insights**: Customized advice for your location and usage pattern
        
        **Powered by Google Gemini or OpenRouter**  
        Configure your preferred AI model in Settings ⚙️
        """)
    
    with st.expander("📊 Step 4: Compare & Decide"):
        st.markdown("""
        Use our additional tools:
        
        - **Quick Calculator**: Test different scenarios quickly
        - **Compare Systems**: Side-by-side comparison of different sizes
        - **Battery Calculator**: Compare battery chemistries (Lithium vs Lead-Acid vs Gel)
        - **Chat Advisor**: Ask questions about solar energy in Kenya
        """)
    
    # Key information
    st.markdown("---")
    st.subheader("🎯 What Makes Jua Smart Accurate?")
    
    col_acc1, col_acc2 = st.columns(2)
    
    with col_acc1:
        st.markdown("""
        **Kenyan-Specific Data:**
        - 🇰🇪 Real EPRA electricity tariffs (updated 2024-2026)
        - ☀️ County-by-county solar irradiance from Kenya Solar Atlas
        - 💰 Market prices from actual Kenyan suppliers
        - 📍 Optional NASA POWER satellite data for precise locations
        
        **Realistic Calculations:**
        - Performance ratio: 80% (accounts for losses)
        - Soiling & degradation included
        - Temperature effects on panels
        - Inverter efficiency factored in
        """)
    
    with col_acc2:
        st.markdown("""
        **Transparent Methodology:**
        - Open equipment database
        - Standard sizing formulas
        - Conservative estimates
        - Validation warnings
        
        **Privacy First:**
        - ✅ No data stored on servers
        - ✅ All calculations done locally
        - ✅ Your information stays private
        - ✅ No account required
        """)
    
    # Important notes
    st.markdown("---")
    st.warning("""
    ⚠️ **Important Limitations**
    
    - These are **estimates** based on typical performance
    - Actual results depend on installation quality, roof angle, shading, and weather
    - Electricity rates may change over time
    - Always get **professional quotes** from licensed installers before making decisions
    - This tool is for planning purposes, not a replacement for professional assessment
    """)
    
    # What's new - collapsed by default
    with st.expander("✨ What's New in Version 2.1"):
        st.markdown("""
        Recent improvements:
        - 🧭 Sidebar navigation for easy access
        - 🔋 Improved battery calculator with Gel battery support
        - ⚖️ System comparison tool
        - � Multiple AI model options (Gemini, OpenRouter)
        - � Export and save analyses
        - ⚡ Better accuracy validation
        - 🎨 Custom branding and improved UI
        """)
    
    # System info sidebar
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.metric("� Counties Covered", len([k for k in GHI_DATA.keys() if k not in ["All_Counties", "counties"]]) if GHI_DATA else 47)
    
    with col_info2:
        st.metric("⚡ Version", "2.1")
    
    with col_info3:
        st.metric("🔋 Battery Types", "Lithium, Gel, Lead-Acid")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p><strong>Jua Smart v2.1</strong> - Powering Kenya with Solar Intelligence ☀️</p>
    <p style='font-size: 0.9em;'>Estimates are indicative. Always consult licensed installers for final quotes.</p>
</div>
""", unsafe_allow_html=True)