# Realistic Battery Sizing - Implementation Guide

## Real-World Battery Constraints

### Lead-Acid & Gel Batteries

**Voltage**: ALWAYS 12V (no exceptions)

**Standard Sizes**:
- 50Ah
- 80Ah
- 100Ah
- 120Ah
- 150Ah
- **200Ah (MAXIMUM)**

**Key Limitation**: Very rare to find Lead-Acid or Gel batteries above 200Ah unless custom-manufactured.

### Lithium Batteries (More Flexible)

**Two Categories**:

#### 1. Ah-Based Lithium (Small Systems)
**Voltage Options**: 12V or 24V individual units
**Standard Sizes**: 50Ah, 100Ah, 150Ah, 200Ah, 300Ah

**Use When**: System < 2.5kWh backup needed

#### 2. kWh-Based Lithium (Larger Systems)
**Examples**:
- Menred 5.12kWh battery
- 2.56kWh, 7.68kWh, 10.24kWh, 15.36kWh, 20.48kWh modules

**Voltage**: Typically 48V or 51.2V (integrated)

**Use When**: System >= 2.5kWh backup needed

---

## Implementation Logic

### Decision Tree

```
Is battery Lithium?
├─ Yes
│  ├─ Backup needed >= 2.5kWh?
│  │  ├─ Yes → Use kWh-based batteries (5.12kWh Menred, etc.)
│  │  └─ No → Use Ah-based batteries (12V units, 50-300Ah)
│  └─
└─ No (Lead-Acid or Gel)
   └─ ALWAYS use 12V, max 200Ah
      └─ Need more capacity? Add parallel strings
```

### Examples

#### Example 1: Small Gel System
```
System: 1.2kW (12V system)
Backup needed: 1.5kWh
Battery type: Gel

Calculation:
- Gel: 12V only, max 200Ah
- Capacity at 12V: 1.5kWh = 125Ah
- Standard size: 150Ah
- Config: 1 battery in series, 1 parallel
Result: 1 × 150Ah @ 12V ✅
```

#### Example 2: Medium Lead-Acid System
```
System: 3kW (24V system)
Backup needed: 4kWh
Battery type: Lead-Acid

Calculation:
- Lead-Acid: 12V only, max 200Ah
- System needs 24V → 2 in series
- Capacity at 12V: 4kWh = 333Ah per string
- Max size: 200Ah → need 2 parallel strings
- Config: 2 in series × 2 parallel
Result: 4 × 200Ah @ 12V (2P2S, 24V system) ✅
```

#### Example 3: Large Lithium System (kWh-based)
```
System: 7kW (48V system)
Backup needed: 12kWh
Battery type: Lithium

Calculation:
- Lithium >= 2.5kWh → Use kWh-based
- System needs 48V → 4 in series (but kWh units handle this internally)
- Choose 5.12kWh units
- Need: 12kWh / 5.12kWh ≈ 2.34 → 3 units needed
- Config: Depends on battery BMS configuration
Result: 3 × 5.12kWh Menred batteries ✅
```

#### Example 4: Small Lithium System (Ah-based)
```
System: 2kW (24V system)
Backup needed: 2kWh
Battery type: Lithium

Calculation:
- Lithium < 2.5kWh → Use Ah-based
- System needs 24V → 2 in series
- Capacity at 12V: 2kWh = 167Ah per string
- Standard size: 200Ah
- Config: 2 in series × 1 parallel
Result: 2 × 200Ah @ 12V (2S, 24V system) ✅
```

---

## Code Implementation

### Updated `calculate_battery_specs()` Function

```python
def calculate_battery_specs(backup_energy_kwh, battery_type, system_kw=None):
    # ... DoD and voltage determination ...
    
    is_lithium = 'Lithium' in battery_type
    
    if is_lithium:
        if total_capacity_kwh >= 2.5:
            # kWh-based lithium
            kwh_sizes = [2.56, 5.12, 7.68, 10.24, 15.36, 20.48]
            recommended_kwh = select_appropriate_size(kwh_sizes, total_capacity_kwh)
            # Calculate number needed...
            return {..., 'is_kwh_based': True, 'recommended_kwh': ...}
        else:
            # Ah-based lithium (50, 100, 150, 200, 300Ah)
            standard_sizes = [50, 100, 150, 200, 300]
            recommended_ah = select_appropriate_size(standard_sizes, capacity_ah)
            return {..., 'is_kwh_based': False, 'recommended_ah': ...}
    
    else:  # Lead-Acid or Gel
        # ALWAYS 12V, max 200Ah
        standard_sizes = [50, 80, 100, 120, 150, 200]
        recommended_ah = min(select_appropriate_size(standard_sizes, capacity_ah), 200)
        
        # If need more than 200Ah per string, add parallel strings
        if capacity_ah > 200:
            parallel_strings = ceil(capacity_ah / 200)
            recommended_ah = 200
        
        return {..., 'battery_voltage_unit': 12, 'is_kwh_based': False}
```

---

## UI Display Logic

### Home Dashboard Display

**For kWh-based Lithium**:
```
Battery Units: 3 × 5.12kWh
System Voltage: 48V (4S)
ℹ️ 48V Lithium System: 3 × 5.12kWh units
```

**For Ah-based (Lead-Acid/Gel/Small Lithium)**:
```
Battery Configuration: 4 × 200Ah @12V
System Voltage: 24V (2S)
ℹ️ 24V System: 2 × 200Ah batteries in series = 4 total batteries
```

---

## Standard Battery Sizes Reference

### Lead-Acid (Flooded)
| Ah | Voltage | Price Range (KSh) | Notes |
|----|---------|-------------------|-------|
| 50 | 12V | 6,000-8,000 | Rare |
| 80 | 12V | 10,000-12,000 | Small systems |
| 100 | 12V | 12,000-15,000 | Common |
| 120 | 12V | 14,000-17,000 | Less common |
| 150 | 12V | 17,000-20,000 | Popular mid-size |
| 200 | 12V | 18,000-26,000 | **Maximum standard** |

### Gel (Maintenance-Free)
| Ah | Voltage | Price Range (KSh) | Notes |
|----|---------|-------------------|-------|
| 50 | 12V | 18,000-22,000 | Rare |
| 80 | 12V | 20,000-24,000 | Uncommon |
| 100 | 12V | 22,000-28,000 | Entry level |
| 120 | 12V | 26,000-32,000 | Less common |
| 150 | 12V | 28,000-35,000 | Very popular |
| 200 | 12V | 35,000-42,000 | **Maximum standard** |

### Lithium (Ah-based)
| Ah | Voltage | Price Range (KSh) | Notes |
|----|---------|-------------------|-------|
| 50 | 12V | 25,000-30,000 | Small backup |
| 100 | 12V | 52,000-60,000 | Common |
| 150 | 12V | 75,000-85,000 | Mid-range |
| 200 | 12V | 95,000-110,000 | Popular |
| 300 | 12V | 140,000-160,000 | Large capacity |

### Lithium (kWh-based)
| Capacity | Price Range (KSh) | Notes |
|----------|-------------------|-------|
| 2.56kWh | 120,000-140,000 | Small modular |
| 5.12kWh | 220,000-280,000 | **Menred standard** |
| 7.68kWh | 330,000-400,000 | Medium |
| 10.24kWh | 450,000-550,000 | Large |
| 15.36kWh | 650,000-800,000 | Very large |
| 20.48kWh | 850,000-1,050,000 | Commercial |

---

## Benefits of This Approach

✅ **Realistic**: Uses actual available battery sizes
✅ **Market-Accurate**: Reflects Kenya solar battery market
✅ **Installation-Ready**: Installer knows exactly what to order
✅ **Cost-Accurate**: Pricing matches real products
✅ **Flexible**: Handles both Ah and kWh specifications
✅ **Scalable**: Easy to add new battery models

---

## Testing Scenarios

### Test 1: Small Gel System
```
Input: 1kW system, 8hr backup, Gel
Expected: 2 × 80Ah @ 12V (12V system)
```

### Test 2: Medium Lead-Acid System
```
Input: 3kW system, 12hr backup, Lead-Acid
Expected: 4 × 200Ah @ 12V (24V, 2P2S)
```

### Test 3: Large Lithium System (kWh)
```
Input: 8kW system, 10hr backup, Lithium
Expected: 4 × 5.12kWh or 2 × 10.24kWh
```

### Test 4: Small Lithium System (Ah)
```
Input: 1.5kW system, 6hr backup, Lithium
Expected: 2 × 100Ah @ 12V (24V, 2S)
```

---

## Status: ✅ COMPLETE

Battery calculator now uses realistic, market-available battery sizes that installers can actually purchase and install!
