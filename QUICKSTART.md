# Smart Energy Advisor - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.14+
- Windows/Mac/Linux
- Internet connection (for Gemini API)
- GEMINI_API_KEY environment variable

### Installation
```bash
cd E:\Zindi\SmartEnergyAdvisor_Completed
pip install -r requirements.txt
streamlit run app.py
```

### Access the App
Open your browser and go to: **http://localhost:8501**

---

## 📱 App Navigation

### Tab 1: 📊 Input & Quick Analysis
**Purpose**: Gather energy details and get instant ROI preview

**What to do**:
1. Select your county (affects solar irradiance value)
2. Choose input method:
   - **Current Electricity Bill** (recommended): Enter monthly kWh and bill amount
   - **Appliance-by-Appliance**: Select all appliances you use
3. System calculates monthly consumption
4. View current tariff, category, and monthly bill
5. Select system type (grid-tied, hybrid, off-grid)
6. **Quick Estimate** shows instant payback period and system size

**Output**:
- System size (kW)
- Upfront cost (KSh)
- Annual savings (KSh)
- Payback period (years)
- Cost breakdown pie chart
- 25-year financial timeline

---

### Tab 2: 🔍 Detailed AI Recommendation
**Purpose**: Get AI-powered system configuration and equipment selection

**What to do**:
1. Make sure you've entered energy details in Tab 1
2. Click **"🚀 Generate AI Recommendation"** button
3. Wait 15-30 seconds for AI analysis
4. Review recommended equipment:
   - Solar panels (model, wattage, count)
   - Inverter (type, capacity)
   - Battery (if applicable)
   - Cables, breakers, mounting

**Output**:
- System configuration details
- Equipment specifications
- Equipment pricing breakdown
- Validation checks
- Installation timeline

**Note**: Requires GEMINI_API_KEY to be set. If API fails, use Tab 1 Quick Estimate.

---

### Tab 3: 📈 Financial Analysis
**Purpose**: Detailed 25-year financial projections

**What to do**:
1. Generate AI recommendation in Tab 2 first
2. This tab auto-populates with financial data

**Output**:
- NPV (Net Present Value) for 25 years
- Payback period highlighted
- Annual savings progression
- Cumulative savings chart
- Financing options (PayGo, bank loans)

**Key Metrics**:
- Upfront cost
- Annual savings
- Operating costs
- Inverter replacement year 10
- Total 25-year savings

---

### Tab 4: 🌍 Environmental Impact
**Purpose**: See CO₂ offset and environmental benefits

**What to do**:
1. Generate AI recommendation in Tab 2 first
2. View environmental impact

**Output**:
- Annual CO₂ offset (tons)
- 25-year CO₂ offset (tons)
- Fun comparisons:
  - Trees planted equivalent
  - km car driving avoided
  - Homes powered
- CO₂ gauge visual
- Monthly energy generation chart

---

### Tab 5: ☀️ Radiation Data Comparison
**Purpose**: Compare solar irradiance data sources

**What to do**:
1. Review data source overview (Kenya Atlas vs NASA POWER)
2. Select a county to compare
3. View GHI data and calculations
4. Compare all counties in chart
5. Read technical details about each source

**Output**:
- GHI values by county
- Data source comparison table
- Interactive bar chart
- Annual radiation calculations
- 1kW system output estimate

**Key Learning**:
- Kenya Solar Atlas: Fast, county-level, static
- NASA POWER API: Precise, global, real-time (future)

---

### Tab 6: ℹ️ About & Resources
**Purpose**: System information and documentation

**Contents**:
- System description
- Technology stack
- Data assumptions
- Financing & incentives
- Disclaimer
- System version & status
- Privacy policy
- Next steps guide

---

## 🎯 Common Workflows

### Workflow A: Quick ROI Check
1. Go to Tab 1
2. Select county and enter consumption (from bill)
3. View Quick Estimate
4. Get instant payback period
5. **Time**: 2-3 minutes

### Workflow B: Detailed Analysis
1. Tab 1: Enter energy details
2. Tab 2: Generate AI recommendation
3. Tab 3: Review 25-year financials
4. Tab 4: Check environmental benefits
5. **Time**: 15-20 minutes

### Workflow C: Data Validation
1. Tab 1: Enter your data
2. Tab 5: Check solar radiation values
3. Compare with NASA POWER (future)
4. Validate system sizing
5. **Time**: 10 minutes

---

## 💡 Input Tips

### Energy Consumption
**Best Practice**: Use your **actual electricity bill**
- More accurate than estimating
- Accounts for seasonal variations
- Reflects your actual behavior

**How to find on your bill**:
- KPLC bill: Look for "Energy Used" or "Units Consumed" in kWh
- Should be under 30 kWh (lifeline) to 500+ kWh (commercial)

### Appliance Calculator
**When to use**: If you don't have a bill or want detailed breakdown

**Tips**:
- Include ALL appliances (even small ones add up)
- Be honest about usage hours
- LED lights consume much less than incandescent
- Fridges run 24/7 but compressor cycles
- Water pumps variable - set realistic hours/day

### County Selection
**Coverage**:
- 9 major counties included
- More coming soon
- Highest GHI: Marsabit (6.0 kWh/m²/day)
- Lowest GHI: Kisumu (4.8 kWh/m²/day)

---

## 💰 Financial Terms

| Term | Definition |
|------|-----------|
| **NPV** | Net Present Value - total profit in today's money |
| **Payback Period** | Years until system pays for itself |
| **ROI** | Return on Investment - total profit as % |
| **LCOE** | Levelized Cost of Energy per kWh |
| **IRR** | Internal Rate of Return - annual profit % |
| **Upfront Cost** | Total initial system investment |
| **Annual Savings** | Money saved on electricity per year |

---

## ⚠️ Important Notes

### System Limitations
- Estimates based on current data (subject to change)
- Actual costs vary by installer and region
- Weather affects real performance
- Tariffs may change annually
- Government policies may change

### Before Installation
✓ Get physical site survey
✓ Check roof condition and shading
✓ Verify local permits required
✓ Compare quotes from 3+ installers
✓ Check installer credentials
✓ Review warranty details
✓ Plan for maintenance schedule

### Data Privacy
- ✓ No personal data stored
- ✓ Calculations run locally
- ✓ Only Gemini API calls go to cloud
- ✓ Your inputs not saved
- ✓ Energy data anonymized

---

## 🔧 Troubleshooting

### "API Error: Gemini API key not found"
- Check `.env` file exists in project root
- Verify `GEMINI_API_KEY` is set correctly
- Restart Streamlit after setting key
- Use Tab 1 Quick Estimate as alternative

### "Error loading data files"
- Check all JSON files exist in `data/` folder
- Verify JSON syntax (use online validator)
- Ensure files are readable
- Restart Streamlit

### "App runs slowly"
- First load is slower (caching)
- Gemini API calls can take 20-30 seconds
- Clear browser cache
- Restart Streamlit

### "Numbers seem too high/low"
- Check your consumption input (most common issue)
- Verify county selection (GHI varies by region)
- Compare against historical bills
- Check tariff category (lifeline vs ordinary)

---

## 📊 Data Sources

| Data | Source | Update |
|------|--------|--------|
| Solar Irradiance | Kenya Solar Atlas | Annual |
| Electricity Tariff | EPRA 2024-2026 | Annual |
| Equipment Prices | Local market data | Quarterly |
| Incentives | ICTA, KETRACO | As announced |

---

## 🚀 Next Steps

1. **Try Tab 1**: Get your Quick Estimate
2. **Generate Recommendation**: Use Tab 2 for detailed plan
3. **Review Financials**: Tab 3 shows your money back timeline
4. **Check Environment**: Tab 4 shows CO₂ savings
5. **Contact Installer**: Get actual site survey and quote
6. **Compare Offers**: Use system sizing from app for comparison
7. **Install**: Proceed with trusted installer

---

## 📞 Support

**For App Issues**:
- Check Tab 6 (About & Resources)
- Review this guide
- Check DATA_SOURCES.md for technical details

**For Solar Questions**:
- Contact: Kenya Solar Energy Association
- Website: https://kaseakenya.org/
- Hotline: Check local installers

**For EPRA Tariffs**:
- Website: https://www.epra.go.ke/
- Contact: EPRA Customer Care

---

## 📝 Version Info

**Current Version**: 1.2.0 (Smart Energy Advisor)

**Last Updated**: November 24, 2025

**Technology**:
- Framework: Streamlit
- Backend: Python 3.14
- AI: Google Gemini 2.5 Flash
- Visualizations: Plotly
- Data: Kenya Solar Atlas + EPRA

---

Happy planning! 🌞⚡

