"""
Accuracy Validator for Solar Recommendations
Validates AI-generated recommendations and provides confidence scores
"""

def validate_system_sizing(system_kw, monthly_consumption_kwh, ghi):
    """
    Validates if system size is appropriate for consumption
    Returns: (is_valid, warning_message, confidence_score)
    """
    annual_consumption = monthly_consumption_kwh * 12
    
    # Expected generation per kW (kWh/year)
    expected_generation_per_kw = ghi * 365 * 0.75  # 75% efficiency factor
    expected_total_generation = system_kw * expected_generation_per_kw
    
    coverage_ratio = expected_total_generation / annual_consumption if annual_consumption > 0 else 0
    
    warnings = []
    confidence = 1.0
    
    # Check for oversizing
    if coverage_ratio > 1.5:
        warnings.append(f"⚠️ System may be oversized ({coverage_ratio:.1%} of consumption)")
        confidence -= 0.2
    
    # Check for undersizing
    if coverage_ratio < 0.7:
        warnings.append(f"⚠️ System may be undersized ({coverage_ratio:.1%} of consumption)")
        confidence -= 0.15
    
    # Optimal range
    if 0.9 <= coverage_ratio <= 1.2:
        warnings.append(f"✅ Optimal sizing ({coverage_ratio:.1%} coverage)")
    
    return len(warnings) == 1 and "✅" in warnings[0], warnings, max(0, min(1, confidence))


def validate_payback_period(payback_years):
    """
    Validates if payback period is realistic
    Returns: (is_valid, warning_message, confidence_score)
    """
    warnings = []
    confidence = 1.0
    
    if payback_years < 3:
        warnings.append("⚠️ Payback period seems too optimistic (< 3 years)")
        confidence = 0.4
    elif payback_years > 15:
        warnings.append("⚠️ Payback period is very long (> 15 years)")
        confidence = 0.5
    elif 5 <= payback_years <= 10:
        warnings.append("✅ Realistic payback period (5-10 years)")
        confidence = 1.0
    else:
        confidence = 0.8
    
    return 3 <= payback_years <= 15, warnings, confidence


def validate_cost_per_watt(cost_per_watt):
    """
    Validates if cost per watt is within market range for Kenya
    Returns: (is_valid, warning_message, confidence_score)
    """
    warnings = []
    confidence = 1.0
    
    # Typical range in Kenya: 55-120 KSh/W
    if cost_per_watt < 55:
        warnings.append("⚠️ Cost seems too low - verify equipment quality")
        confidence = 0.5
    elif cost_per_watt > 150:
        warnings.append("⚠️ Cost is higher than market average")
        confidence = 0.6
    elif 70 <= cost_per_watt <= 110:
        warnings.append("✅ Cost is within typical market range")
        confidence = 1.0
    else:
        confidence = 0.8
    
    is_valid = 55 <= cost_per_watt <= 150
    
    return is_valid, warnings, confidence


def validate_ghi_location(ghi, location):
    """
    Validates if GHI value is reasonable for Kenya
    Returns: (is_valid, warning_message, confidence_score)
    """
    warnings = []
    confidence = 1.0
    
    # Kenya's GHI typically ranges from 4.5 to 6.5 kWh/m²/day
    if ghi < 4.5:
        warnings.append(f"⚠️ Low solar potential in {location} (GHI: {ghi:.1f})")
        confidence = 0.7
    elif ghi >= 5.5:
        warnings.append(f"✅ Excellent solar potential in {location} (GHI: {ghi:.1f})")
        confidence = 1.0
    else:
        warnings.append(f"✅ Good solar potential in {location} (GHI: {ghi:.1f})")
        confidence = 0.9
    
    is_valid = ghi >= 4.0
    
    return is_valid, warnings, confidence


def calculate_overall_confidence(validation_results):
    """
    Calculates overall confidence score from multiple validation results
    Returns: (overall_confidence, confidence_level, color)
    """
    confidences = [result[2] for result in validation_results if len(result) >= 3]
    
    if not confidences:
        return 0.5, "Moderate", "orange"
    
    overall = sum(confidences) / len(confidences)
    
    if overall >= 0.85:
        return overall, "High", "green"
    elif overall >= 0.7:
        return overall, "Good", "lightgreen"
    elif overall >= 0.5:
        return overall, "Moderate", "orange"
    else:
        return overall, "Low", "red"


def get_confidence_stars(confidence):
    """
    Converts confidence score to star rating
    Returns: star string (e.g., "⭐⭐⭐⭐⭐")
    """
    stars = int(round(confidence * 5))
    return "⭐" * stars + "☆" * (5 - stars)


def validate_recommendation(recommendation, monthly_consumption_kwh, ghi, location):
    """
    Main validation function for solar recommendations
    Returns: dict with validation results and overall confidence
    """
    results = {
        'validations': [],
        'warnings': [],
        'overall_confidence': 0.0,
        'confidence_level': 'Unknown',
        'confidence_stars': '',
        'color': 'gray'
    }
    
    try:
        # Extract values from recommendation
        system_sizing = recommendation.get('system_sizing', {})
        financial = recommendation.get('financial_analysis', {})
        
        system_kw = system_sizing.get('required_system_size_kw', 0)
        payback_years = financial.get('payback_period_years', 0)
        total_cost = financial.get('total_upfront_cost_ksh', 0)
        
        cost_per_watt = total_cost / (system_kw * 1000) if system_kw > 0 else 0
        
        # Run validations
        validation_list = []
        
        # System sizing
        valid_sizing, sizing_warnings, sizing_conf = validate_system_sizing(
            system_kw, monthly_consumption_kwh, ghi
        )
        validation_list.append((valid_sizing, sizing_warnings, sizing_conf))
        results['warnings'].extend(sizing_warnings)
        
        # Payback period
        valid_payback, payback_warnings, payback_conf = validate_payback_period(payback_years)
        validation_list.append((valid_payback, payback_warnings, payback_conf))
        results['warnings'].extend(payback_warnings)
        
        # Cost per watt
        valid_cost, cost_warnings, cost_conf = validate_cost_per_watt(cost_per_watt)
        validation_list.append((valid_cost, cost_warnings, cost_conf))
        results['warnings'].extend(cost_warnings)
        
        # GHI/Location
        valid_ghi, ghi_warnings, ghi_conf = validate_ghi_location(ghi, location)
        validation_list.append((valid_ghi, ghi_warnings, ghi_conf))
        results['warnings'].extend(ghi_warnings)
        
        # Calculate overall confidence
        overall_conf, conf_level, color = calculate_overall_confidence(validation_list)
        
        results['overall_confidence'] = overall_conf
        results['confidence_level'] = conf_level
        results['confidence_stars'] = get_confidence_stars(overall_conf)
        results['color'] = color
        results['validations'] = validation_list
        
    except Exception as e:
        results['warnings'].append(f"⚠️ Validation error: {str(e)}")
        results['confidence_level'] = "Unknown"
    
    return results
