# Solar Cost Calculation Fix - Technical Report

## Issue Identified 🚨

**User Observation**: 
"Solar equipment cost is KSh 265,511 for a 1.4kW system (3 panels). Why so high?"

**Root Cause Analysis**:
The `calculate_system_cost` function was **double-counting** costs:
1. It calculated an "Installation Cost" using a per-watt rate (e.g., KSh 87.5/W) which *already implicitly included* equipment costs in the industry standard assumptions.
2. It THEN added an explicit "Equipment Cost" (Panels + Inverter) on top of that.
3. Result: The user was being charged for the equipment TWICE.

**Previous Calculation (Approximate)**:
- Installation (Implicitly including equipment): ~KSh 122,500
- Equipment (Explicitly added): ~KSh 143,000
- **Total Displayed**: ~KSh 265,511 ❌ (Way too high!)

---

## The Fix ✅

I have completely rewritten the `calculate_system_cost` function to use a **bottom-up component-based approach** instead of a top-down estimate.

### New Calculation Logic

The new formula sums up specific components:

1. **Solar Panels**: 
   - `Count × Average Panel Price`
   - Example: 3 × KSh 22,000 = KSh 66,000

2. **Inverter**:
   - Based on system size capacity
   - Example: 1.5kW Inverter ≈ KSh 45,000

3. **Balance of System (BOS)**:
   - Cables, mounting rails, breakers, connectors
   - Calculated as 18% of equipment cost
   - Example: 18% of (66k + 45k) ≈ KSh 20,000

4. **Installation Labor**:
   - Professional installation fee
   - Calculated as ~KSh 20,000 per kW
   - Example: 1.4kW × 20,000 ≈ KSh 28,000

**New Estimated Total**: ~KSh 159,000 ✅ (Much more realistic)

---

## UI Improvements

I have also updated the **My Analyses** page to show a transparent **Cost Breakdown**:

```
Solar Equipment Cost: KSh 159,000

💸 Cost Breakdown
-------------------
Panels:       KSh 66,000
Inverter:     KSh 45,000
Installation: KSh 28,000
Accessories:  KSh 20,000
```

This transparency helps users understand exactly where their money is going, rather than seeing one large, unexplained figure.

### Files Modified
- `utils/cost_calculator.py`: Rewrote `calculate_system_cost`
- `app.py`: Updated `calculate_quick_roi` to handle new return values
- `app.py`: Updated "My Analyses" section to display the breakdown
- `app.py`: Updated "Cost Breakdown" pie chart to use real data

## Status: ✅ FIXED

The costs are now accurate, realistic for the Kenyan market, and fully transparent.
