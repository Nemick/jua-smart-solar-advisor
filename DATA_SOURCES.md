# Solar Radiation Data Sources - Comparison Guide

## Overview
The Smart Energy Advisor uses solar radiation data to calculate system sizing and energy generation estimates. We support two data sources:

1. **Kenya Solar Atlas (Static JSON)** - Currently active
2. **NASA POWER API** - Available for future enhancements

---

## 1. Kenya Solar Atlas (Current Implementation)

### File Location
- `data/kenya_counties_irradiance.json`

### Data Format
```json
{
    "Nairobi": {
        "ghi_kwh_m2_day": 5.2,
        "lat": -1.2921,
        "lon": 36.8219
    },
    "Mombasa": {
        "ghi_kwh_m2_day": 5.5,
        "lat": -4.0546,
        "lon": 39.6636
    }
    // ... more counties
}
```

### Key Metrics
| Metric | Value |
|--------|-------|
| **Coverage** | 9 major Kenyan counties |
| **Data Type** | Global Horizontal Irradiance (GHI) |
| **Unit** | kWh/m²/day |
| **Update Frequency** | Static (annual review) |
| **Granularity** | County level |
| **Historical Data** | Not included |
| **Weather Data** | No |

### Counties Included
| County | GHI (kWh/m²/day) | Coordinates |
|--------|-----------------|-------------|
| Nairobi | 5.2 | -1.29°, 36.82° |
| Mombasa | 5.5 | -4.05°, 39.66° |
| Kisumu | 4.8 | -0.09°, 34.77° |
| Nakuru | 5.1 | -0.30°, 36.08° |
| Eldoret | 4.9 | 0.51°, 35.27° |
| Marsabit | 6.0 | 2.35°, 37.99° |
| Turkana | 5.8 | 3.50°, 35.50° |
| Garissa | 5.7 | -0.45°, 39.64° |
| All_Counties | 5.2 | 0.00°, 37.00° (average) |

### How We Use It
1. User selects their county
2. We retrieve the corresponding GHI value
3. Calculate system size needed: `Required_kW = Annual_Consumption / (GHI × Efficiency × Performance_Ratio × 365)`
4. Display in Quick Estimate section of Tab 1

### Advantages
✓ **Fast** - No API calls needed
✓ **Reliable** - Based on Kenya Solar Atlas
✓ **Offline** - Works without internet
✓ **Accurate** - County-level data for Kenya
✓ **Free** - No licensing costs

### Limitations
✗ **Limited Coverage** - Only 9 counties
✗ **Static** - No seasonal variations
✗ **No Weather** - No temperature, humidity, wind data
✗ **Lower Precision** - County-level only, not exact location

---

## 2. NASA POWER API (Future Integration)

### API Endpoint
```
https://power.larc.nasa.gov/api/temporal/daily/point
```

### Implementation Details
See: `utils/nasa_power_api.py`

### Data Parameters Available
| Parameter | Description | Units |
|-----------|-------------|-------|
| `ALLSKY_SFC_SW_DWN` | All-sky shortwave radiation (actual conditions) | kWh/m² |
| `CLRSKY_SFC_SW_DWN` | Clear-sky shortwave radiation (reference) | kWh/m² |
| `T2M` | Temperature at 2m height | °C |
| `T2M_MAX` | Maximum temperature | °C |
| `T2M_MIN` | Minimum temperature | °C |
| `RH2M` | Relative humidity | % |
| `WS10M` | Wind speed at 10m | m/s |

### Key Features
| Metric | Value |
|--------|-------|
| **Coverage** | Global (any lat/lon) |
| **Data Type** | Daily irradiance + weather |
| **Update Frequency** | Daily (1-3 day lag) |
| **Granularity** | Exact coordinates |
| **Historical Data** | 30+ years available |
| **Weather Data** | Yes (temp, humidity, wind) |
| **Real-time** | Yes (daily updates) |

### Usage Example
```python
from utils.nasa_power_api import fetch_by_address

# Fetch data for a specific location
address = "Nairobi, Kenya"
df = fetch_by_address(
    address,
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Returns DataFrame with daily irradiance data
```

### Advantages
✓ **Global Coverage** - Works anywhere in the world
✓ **Precise** - Exact lat/lon coordinates
✓ **Dynamic** - Real-time daily updates
✓ **Weather Data** - Temperature, humidity, wind
✓ **Historical** - 30+ years of data
✓ **Free** - NASA POWER API is free to use
✓ **Validation** - Can verify Atlas estimates

### Limitations
✗ **API Latency** - 1-3 day lag on updates
✗ **Internet Required** - Requires live API connection
✗ **External Dependency** - Relies on NASA servers
✗ **Rate Limiting** - Has usage limits
✗ **Complexity** - Requires location lookup

---

## Comparison: When to Use Each

### Use **Kenya Solar Atlas (Current)**
- Quick estimates for initial planning
- County-level analysis
- Offline capability needed
- Fast response required
- Standard residential sizing
- **Best for**: Tab 1 Quick Estimate

### Use **NASA POWER API (Future)**
- Precise site-specific analysis
- Exact location coordinates available
- Weather data needed for calculations
- Seasonal performance projection
- Before final installation
- Validation against Atlas data
- **Best for**: Tab 5 detailed comparison, site surveys

---

## Graph Comparison Features (Tab 5)

The new **Radiation Data Comparison** tab provides:

1. **Data Source Overview**
   - Kenya Solar Atlas summary
   - NASA POWER API summary

2. **County-by-County Comparison**
   - Select any county
   - View GHI value from Atlas
   - Calculate annual radiation
   - Estimate 1kW system output

3. **All Counties Chart**
   - Visual comparison of all 9 counties
   - Color-coded by radiation level
   - Interactive bar chart

4. **Data Source Details Table**
   - Feature comparison
   - Update frequency
   - Coverage area
   - Best use cases

5. **NASA POWER Integration Info**
   - How to use API
   - Available parameters
   - Use case recommendations

---

## Implementation in App.py

### Loading Data
```python
@st.cache_data
def load_all_data():
    data["ghi"] = load_json_data("kenya_counties_irradiance.json")
    return data

GHI_DATA = data.get("ghi", {})
```

### Getting GHI for Location
```python
def get_ghi_for_location(location):
    return GHI_DATA.get(location, {"ghi_kwh_m2_day": 5.0})
```

### Using in Calculations
```python
ghi_value = get_ghi_for_location(selected_county)
annual_yield_per_kw = ghi_value * module_efficiency * performance_ratio * 365
```

---

## Future Enhancements

### Phase 1 (Current)
✓ Kenya Solar Atlas JSON data
✓ Tab 1: Quick Estimate with Atlas data
✓ Tab 5: Data comparison visualization

### Phase 2 (Planned)
- [ ] Add NASA POWER API integration
- [ ] Fetch real-time data for selected county
- [ ] Compare NASA vs Atlas data
- [ ] Show seasonal variations
- [ ] Weather-adjusted efficiency calculations

### Phase 3 (Advanced)
- [ ] Microclimate analysis
- [ ] Terrain shading effects
- [ ] Multiple-year historical trends
- [ ] Export detailed radiation reports
- [ ] Integration with site survey data

---

## Data Quality & Accuracy

### Kenya Solar Atlas
- **Source**: Ministry of Energy, Kenya Solar Atlas
- **Validation**: Cross-checked with NASA POWER data
- **Accuracy**: ±5% typical error
- **Update Cycle**: Annual

### NASA POWER
- **Source**: NASA Langley Research Center
- **Validation**: Satellite observations + ground stations
- **Accuracy**: ±3-5% typical error
- **Update Frequency**: Daily

### Combined Approach
Using both sources provides:
1. Quick baseline (Atlas)
2. Precise validation (NASA)
3. Enhanced accuracy through comparison
4. Confidence in system sizing

---

## References

1. **Kenya Solar Atlas**: https://www.irena.org/countries/Kenya
2. **NASA POWER Project**: https://power.larc.nasa.gov/
3. **EPRA Tariffs**: https://www.epra.go.ke/
4. **Gemini API**: https://ai.google.dev/
5. **Smart Energy Advisor**: GitHub (this project)

---

## Support

For questions about:
- **Data accuracy**: Contact Kenya Ministry of Energy
- **NASA POWER API**: Visit https://power.larc.nasa.gov/docs/
- **This app**: See Tab 6 (About & Resources)

