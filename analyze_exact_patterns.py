#!/usr/bin/env python3
"""
Analyze exact patterns by looking at successful cases and working backwards
"""

import json

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

print(f"Analyzing {len(day1_cases)} day 1 cases for exact patterns...")

# Look for cases where expected/miles ratio or expected/receipts ratio might reveal patterns
print("\nDetailed ratio analysis:")

# Calculate various ratios for each case
for case in day1_cases[:20]:  # Look at first 20 cases
    miles = case['miles']
    receipts = case['receipts']
    expected = case['expected']
    
    print(f"\nCase {case['case']}: {miles}mi, ${receipts:.2f}r → ${expected:.2f}")
    
    # If we assume formula is: base + miles*m_coeff + receipts*r_coeff
    # Let's try to see what base would be needed for different coefficient assumptions
    
    # Try common coefficient combinations
    test_combinations = [
        (0.5, 0.5),   # Equal weight
        (0.6, 0.45),  # Slight mileage bias
        (1.0, 0.5),   # Strong mileage bias
        (0.8, 0.6),   # Both relatively high
        (0.4, 0.7),   # Receipt bias
    ]
    
    for m_coeff, r_coeff in test_combinations:
        implied_base = expected - (miles * m_coeff + receipts * r_coeff)
        print(f"  If {m_coeff:.1f}*mi + {r_coeff:.1f}*rec, base = ${implied_base:.2f}")

# Let's try a different approach - look for non-linear patterns
print(f"\n" + "="*60)
print("CHECKING FOR NON-LINEAR PATTERNS")

# Check if there are thresholds or tiers
print("\nLooking for threshold effects...")

# Group by receipt ranges and see if there are different patterns
receipt_ranges = [
    (0, 100, "Very Low"),
    (100, 500, "Low"), 
    (500, 1000, "Medium"),
    (1000, 1500, "High"),
    (1500, 3000, "Very High")
]

for min_r, max_r, label in receipt_ranges:
    cases_in_range = [case for case in day1_cases if min_r <= case['receipts'] < max_r]
    if cases_in_range:
        print(f"\n{label} receipts (${min_r}-${max_r}): {len(cases_in_range)} cases")
        
        # Calculate average ratios within this range
        avg_expected = sum(case['expected'] for case in cases_in_range) / len(cases_in_range)
        avg_miles = sum(case['miles'] for case in cases_in_range) / len(cases_in_range)
        avg_receipts = sum(case['receipts'] for case in cases_in_range) / len(cases_in_range)
        
        print(f"  Average: {avg_miles:.0f}mi, ${avg_receipts:.0f}r → ${avg_expected:.2f}")
        
        # Show ratios
        if avg_miles > 0:
            print(f"  Expected/Miles ratio: {avg_expected/avg_miles:.3f}")
        if avg_receipts > 0:
            print(f"  Expected/Receipts ratio: {avg_expected/avg_receipts:.3f}")
        
        # Show a few examples
        for case in cases_in_range[:3]:
            print(f"    Case {case['case']}: {case['miles']}mi, ${case['receipts']:.0f}r → ${case['expected']:.2f}")

# Check for patterns based on mileage ranges
print(f"\n" + "-"*40)
print("MILEAGE RANGE ANALYSIS")

mileage_ranges = [
    (0, 100, "Very Low"),
    (100, 300, "Low"),
    (300, 600, "Medium"), 
    (600, 900, "High"),
    (900, 1200, "Very High")
]

for min_m, max_m, label in mileage_ranges:
    cases_in_range = [case for case in day1_cases if min_m <= case['miles'] < max_m]
    if cases_in_range:
        print(f"\n{label} mileage ({min_m}-{max_m}mi): {len(cases_in_range)} cases")
        
        avg_expected = sum(case['expected'] for case in cases_in_range) / len(cases_in_range)
        avg_miles = sum(case['miles'] for case in cases_in_range) / len(cases_in_range)
        avg_receipts = sum(case['receipts'] for case in cases_in_range) / len(cases_in_range)
        
        print(f"  Average: {avg_miles:.0f}mi, ${avg_receipts:.0f}r → ${avg_expected:.2f}")
        
        # Show ratios
        if avg_miles > 0:
            print(f"  Expected/Miles ratio: {avg_expected/avg_miles:.3f}")
        if avg_receipts > 0:
            print(f"  Expected/Receipts ratio: {avg_expected/avg_receipts:.3f}")

# Let's look at specific extreme cases to understand them
print(f"\n" + "="*60)
print("EXTREME CASE ANALYSIS")

# Find cases with very different characteristics
extreme_cases = [
    # High miles, low receipts
    max(day1_cases, key=lambda c: c['miles'] if c['receipts'] < 500 else 0),
    # Low miles, high receipts  
    max(day1_cases, key=lambda c: c['receipts'] if c['miles'] < 200 else 0),
    # Both high
    max(day1_cases, key=lambda c: c['miles'] + c['receipts']),
    # Both low
    min(day1_cases, key=lambda c: c['miles'] + c['receipts'])
]

for case in extreme_cases:
    if case:  # Make sure we found a valid case
        print(f"\nExtreme case {case['case']}: {case['miles']}mi, ${case['receipts']:.2f}r → ${case['expected']:.2f}")
        
        # Calculate what the "effective rate" would be if split between miles and receipts
        total_input = case['miles'] + case['receipts']
        if total_input > 0:
            effective_rate = case['expected'] / total_input
            print(f"  Effective rate: ${effective_rate:.3f} per unit of (miles + receipts)")
        
        # Try to see what base would be needed for different scenarios
        print(f"  If base=50: need ${(case['expected']-50)/total_input:.3f} per unit")
        print(f"  If base=100: need ${(case['expected']-100)/total_input:.3f} per unit")
        print(f"  If base=150: need ${(case['expected']-150)/total_input:.3f} per unit")

# Final attempt: brute force search for exact matches
print(f"\n" + "="*60)
print("BRUTE FORCE EXACT MATCH SEARCH")

print("Searching for formulas that give exact matches...")

# Test every combination more systematically
exact_match_formulas = []

for base in range(0, 200, 5):
    for m_coeff in [x/20 for x in range(1, 40)]:  # 0.05 to 1.95 in steps of 0.05
        for r_coeff in [x/20 for x in range(1, 40)]:  # 0.05 to 1.95 in steps of 0.05
            
            exact_matches = 0
            close_matches = 0
            total_error = 0
            
            for case in day1_cases:
                calculated = base + case['miles'] * m_coeff + case['receipts'] * r_coeff
                error = abs(calculated - case['expected'])
                total_error += error
                
                if error <= 0.01:
                    exact_matches += 1
                elif error <= 1.0:
                    close_matches += 1
            
            if exact_matches > 0:
                avg_error = total_error / len(day1_cases)
                exact_match_formulas.append((base, m_coeff, r_coeff, exact_matches, close_matches, avg_error))

# Sort by number of exact matches, then by average error
exact_match_formulas.sort(key=lambda x: (-x[3], x[5]))

print(f"Found {len(exact_match_formulas)} formulas with exact matches:")
for base, m_coeff, r_coeff, exact, close, avg_err in exact_match_formulas[:10]:
    print(f"  ${base} + {m_coeff:.3f}*miles + {r_coeff:.3f}*receipts → {exact} exact, {close} close, avg error ${avg_err:.2f}")