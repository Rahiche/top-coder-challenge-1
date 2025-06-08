#!/usr/bin/env python3
"""
Test different approaches for day 1 cases to achieve near 0 error
"""

import json
import math

# Read public cases
with open('public_cases.json', 'r') as f:
    public_cases = json.load(f)

# Get day 1 cases
day1_cases = []
for i, case in enumerate(public_cases):
    if case['input']['trip_duration_days'] == 1:
        day1_cases.append({
            'case': i + 1,
            'miles': case['input']['miles_traveled'],
            'receipts': case['input']['total_receipts_amount'],
            'expected': case['expected_output']
        })

def test_approach(name, formula_func):
    """Test a formula approach on all day 1 cases"""
    errors = []
    perfect_matches = 0
    close_matches = 0
    
    for case in day1_cases:
        calculated = formula_func(case['miles'], case['receipts'])
        error = abs(calculated - case['expected'])
        errors.append(error)
        
        if error <= 0.01:
            perfect_matches += 1
        if error <= 1.00:
            close_matches += 1
    
    avg_error = sum(errors) / len(errors)
    max_error = max(errors)
    
    print(f"\n{name}:")
    print(f"  Average error: ${avg_error:.2f}")
    print(f"  Max error: ${max_error:.2f}")
    print(f"  Perfect matches (≤$0.01): {perfect_matches} ({perfect_matches/len(day1_cases)*100:.1f}%)")
    print(f"  Close matches (≤$1.00): {close_matches} ({close_matches/len(day1_cases)*100:.1f}%)")
    
    return avg_error, perfect_matches

# Approach 1: Simple linear regression based
def approach1_linear(miles, receipts):
    # Try to find optimal coefficients
    return 200 + miles * 0.8 + receipts * 0.4

# Approach 2: Tiered receipt system
def approach2_tiered(miles, receipts):
    base = 150
    mileage = miles * 0.75
    
    if receipts <= 500:
        receipt_component = receipts * 0.8
    elif receipts <= 1500:
        receipt_component = 500 * 0.8 + (receipts - 500) * 0.6
    else:
        receipt_component = 500 * 0.8 + 1000 * 0.6 + (receipts - 1500) * 0.4
    
    return base + mileage + receipt_component

# Approach 3: Regression analysis on worst cases
def approach3_regression(miles, receipts):
    # Based on pattern analysis
    base = 100
    
    # Higher mileage coefficient for better matching
    mileage = miles * 0.9
    
    # More generous receipt reimbursement
    receipt_component = receipts * 0.5
    
    # Special adjustment for high receipt cases
    if receipts > 1500:
        receipt_component += (receipts - 1500) * 0.1
    
    return base + mileage + receipt_component

# Approach 4: Per-mile base with receipt multiplier
def approach4_per_mile_base(miles, receipts):
    # Higher base calculation
    base = 50 + miles * 0.2  # Base increases with miles
    
    mileage = miles * 0.7
    receipt_component = receipts * 0.55
    
    return base + mileage + receipt_component

# Approach 5: Square root scaling for high values
def approach5_sqrt_scaling(miles, receipts):
    base = 120
    
    # Use sqrt scaling to dampen high values
    mileage = miles * 0.8 if miles <= 500 else 500 * 0.8 + (miles - 500) * 0.6
    
    receipt_component = receipts * 0.6 if receipts <= 1000 else 1000 * 0.6 + (receipts - 1000) * 0.4
    
    return base + mileage + receipt_component

# Approach 6: Analyze specific problem cases and create targeted formula
def approach6_targeted(miles, receipts):
    # Look at worst cases and create targeted fixes
    
    # Base amount
    base = 80
    
    # Mileage component 
    if miles <= 200:
        mileage = miles * 1.0  # Higher rate for low miles
    elif miles <= 600:
        mileage = 200 * 1.0 + (miles - 200) * 0.8
    else:
        mileage = 200 * 1.0 + 400 * 0.8 + (miles - 600) * 0.6
    
    # Receipt component - more generous across the board
    if receipts <= 1000:
        receipt_component = receipts * 0.65
    elif receipts <= 2000:
        receipt_component = 1000 * 0.65 + (receipts - 1000) * 0.45
    else:
        receipt_component = 1000 * 0.65 + 1000 * 0.45 + (receipts - 2000) * 0.25
    
    return base + mileage + receipt_component

# Approach 7: Pattern-based formula from error analysis  
def approach7_pattern_based(miles, receipts):
    # Analyze patterns in the data
    
    # Different base for different ranges
    if miles < 100 and receipts > 1500:
        # Low miles, high receipts - needs high reimbursement
        base = 50
        mileage = miles * 0.5
        receipt_component = receipts * 0.75
    elif miles > 700 and receipts > 1200:
        # High miles, high receipts - needs penalty
        base = 100
        mileage = miles * 0.65
        receipt_component = receipts * 0.45
    elif miles > 800:
        # High miles cases
        base = 120
        mileage = miles * 0.7
        receipt_component = receipts * 0.5
    else:
        # Standard cases
        base = 100
        mileage = miles * 0.8
        receipt_component = receipts * 0.6
    
    return base + mileage + receipt_component

# Approach 8: Machine learning inspired - polynomial features
def approach8_polynomial(miles, receipts):
    # Add interaction terms and polynomial features
    base = 75
    
    # Linear terms
    linear_miles = miles * 0.75
    linear_receipts = receipts * 0.55
    
    # Interaction term
    interaction = (miles * receipts) / 10000  # Scale down the interaction
    
    # Quadratic terms (small coefficients)
    quad_miles = (miles ** 2) / 100000
    quad_receipts = (receipts ** 2) / 1000000
    
    return base + linear_miles + linear_receipts + interaction - quad_miles - quad_receipts

# Test all approaches
print("Testing different approaches for day 1 cases:")
print("=" * 50)

approaches = [
    ("Approach 1: Linear Regression", approach1_linear),
    ("Approach 2: Tiered Receipt System", approach2_tiered),
    ("Approach 3: Regression Analysis", approach3_regression),
    ("Approach 4: Per-Mile Base", approach4_per_mile_base),
    ("Approach 5: Square Root Scaling", approach5_sqrt_scaling),
    ("Approach 6: Targeted Formula", approach6_targeted),
    ("Approach 7: Pattern-Based", approach7_pattern_based),
    ("Approach 8: Polynomial Features", approach8_polynomial)
]

best_approach = None
best_avg_error = float('inf')
best_perfect_matches = 0

for name, func in approaches:
    avg_error, perfect_matches = test_approach(name, func)
    
    # Consider an approach better if it has more perfect matches or significantly lower average error
    if perfect_matches > best_perfect_matches or (perfect_matches == best_perfect_matches and avg_error < best_avg_error):
        best_approach = name
        best_avg_error = avg_error
        best_perfect_matches = perfect_matches

print(f"\n" + "=" * 50)
print(f"BEST APPROACH: {best_approach}")
print(f"Average error: ${best_avg_error:.2f}")
print(f"Perfect matches: {best_perfect_matches}")