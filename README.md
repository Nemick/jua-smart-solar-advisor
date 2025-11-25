# ☀️ Jua Smart - Solar Energy Advisor for Kenya

![Jua Smart Banner](assets/logos/jua_smart_logo.png)

**Jua Smart** (Jua means "sun" in Swahili) is an intelligent solar energy advisor designed specifically for Kenyan homes and businesses. Get AI-powered solar system recommendations with real EPRA tariffs, county-specific solar data, and accurate financial projections.

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python)](https://www.python.org)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=flat&logo=google)](https://ai.google.dev)

---

## ✨ Features

- 🌍 **Kenya-Specific Data**: Real EPRA electricity tariffs (2024-2026) and county-by-county solar irradiance
- 🤖 **AI-Powered Recommendations**: Detailed system designs powered by Google Gemini
- 🔋 **Battery Calculator**: Compare Lithium (LiFePO4), Gel, and Lead-Acid batteries with automatic sizing
- 📊 **Financial Projections**: 25-year ROI analysis, payback periods, and savings calculations
- 📍 **NASA POWER Integration**: Get precise solar data for your exact location
- ⚖️ **System Comparison**: Compare different system sizes side-by-side
- 💬 **Chat Advisor**: Ask questions about solar energy in Kenya
- 📥 **Export Reports**: Download your analysis for offline review

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/jua-smart-solar-advisor.git
   cd jua-smart-solar-advisor
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\\venv\\Scripts\\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Get your free Gemini API key at: https://aistudio.google.com/app/apikey
   
   Add it to `.env`:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   
   The app will automatically open at http://localhost:8501

---

## 📖 How to Use

### Step 1: Input Your Energy Needs

Choose your method:
- **Monthly Bill**: Enter your KPLC bill amount or kWh consumption
- **Appliance List**: Select appliances and add custom ones

Select your location:
- **County Selection**: Quick option using Kenya Solar Atlas
- **Address Input**: More accurate using NASA POWER satellite data

### Step 2: Configure Your System

- **System Type**: Hybrid (with backup), Off-grid, or Grid-tied
- **Battery Type**: Choose Lithium, Gel, or Lead-Acid
- **Backup Duration**: Select 4, 8, 12, or 24 hours

### Step 3: Get AI Recommendations

Click **"Generate AI Report"** to get:
- Detailed system design (panels, inverter, batteries)
- Equipment recommendations with market prices
- 25-year financial projections
- Installation guidelines
- Maintenance schedule

### Step 4: Compare & Decide

Use additional tools:
- **Quick Calculator**: Test different scenarios
- **Compare Systems**: Side-by-side comparison
- **Chat Advisor**: Ask questions

---

## 📁 Project Structure

```
jua-smart-solar-advisor/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration and constants
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment variables
├── .gitignore                      # Git ignore file
│
├── assets/                         # Brand assets
│   ├── logos/                      # Logos and banners
│   └── icons/                      # Icons and favicon
│
├── data/                           # Data files
│   ├── epra_tariffs_2024_2026.json
│   ├── equipment_catalog.json
│   ├── baseline_assumptions.json
│   ├── kenya_counties_irradiance.json
│   └── kenya_counties.geojson
│
├── utils/                          # Utility modules
│   ├── cost_calculator.py          # Cost calculations
│   ├── gemini_handler.py           # AI integration
│   ├── battery_calculator.py       # Battery sizing
│   ├── nasa_power_api.py           # NASA API integration
│   ├── visualizations.py           # Plotly charts
│   └── data_validator.py           # Validation logic
│
└── prompts/                        # AI prompts
    └── system_prompts.py           # Gemini system prompts
```

---


## 🛠️ Tech Stack

- **Framework**: Streamlit
- **AI**: Google Gemini (gemini-1.5-flash)
- **Visualizations**: Plotly
- **Data Processing**: Pandas, NumPy
- **Geospatial**: NASA POWER API, Kenya Solar Atlas
- **Deployment**: Streamlit Cloud (recommended)

---

## 📊 Data Sources

- 🇰🇪 **Kenya Solar Atlas**: County-level solar irradiance data
- ⚡ **EPRA**: Official electricity tariffs (2024-2026)
- 🌍 **NASA POWER**: Real-time satellite solar data
- 🏢 **Market Surveys**: Local equipment prices from Kenyan suppliers

---

## ⚠️ Disclaimer

This tool provides **estimates** for planning purposes:
- Actual results depend on installation quality, roof angle, shading, and weather
- Electricity rates may change over time
- Always get professional quotes from licensed installers before making decisions
- This is NOT a replacement for professional assessment

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Kenya Solar Atlas for county irradiance data
- EPRA for official electricity tariff information
- NASA POWER for satellite solar data
- Google Gemini for AI capabilities
- The Kenyan solar community for market insights

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/jua-smart-solar-advisor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/jua-smart-solar-advisor/discussions)

---

## 🌟 Show Your Support

If this project helped you, please give it a ⭐ on GitHub!

---

<div align="center">
  <p><strong>Jua Smart v2.1</strong></p>
  <p>Powering Kenya with Solar Intelligence ☀️</p>
  <p>Made with ❤️ in Kenya 🇰🇪</p>
</div>
