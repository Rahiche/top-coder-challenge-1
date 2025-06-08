#!/usr/bin/env python3
"""
Simple analysis of day 1 data to find patterns
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

print(f"Analyzing {len(day1_cases)} day 1 cases...")

# Let's analyze a few sample cases to understand the pattern
print("\nSample cases analysis:")
for i in range(min(10, len(day1_cases))):
    case = day1_cases[i]
    miles = case['miles']
    receipts = case['receipts']
    expected = case['expected']
    
    # Try to reverse engineer: if formula is base + miles*m_rate + receipts*r_rate
    # Let's test different combinations
    print(f"Case {case['case']}: {miles}mi, ${receipts}r → ${expected}")
    
    # Test ratio approaches
    per_mile = expected / miles if miles > 0 else 0
    per_receipt = expected / receipts if receipts > 0 else 0
    per_total = expected / (miles + receipts)
    
    print(f"  Per mile: ${per_mile:.3f}, Per receipt: ${per_receipt:.3f}, Per total: ${per_total:.3f}")

# Let's look at some patterns
print("\n" + "="*50)
print("LOOKING FOR PATTERNS")

# Check if there's a simple formula like: expected ≈ a + b*miles + c*receipts
# We can use least squares manually

# Simple correlation check
def correlation(x_values, y_values):
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x * x for x in x_values)
    sum_y2 = sum(y * y for y in y_values)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
    
    if denominator == 0:
        return 0
    return numerator / denominator

miles_list = [case['miles'] for case in day1_cases]
receipts_list = [case['receipts'] for case in day1_cases]
expected_list = [case['expected'] for case in day1_cases]

miles_corr = correlation(miles_list, expected_list)
receipts_corr = correlation(receipts_list, expected_list)

print(f"Correlation - Miles to Expected: {miles_corr:.3f}")
print(f"Correlation - Receipts to Expected: {receipts_corr:.3f}")

# Look at specific ranges
print(f"\nRANGE ANALYSIS:")

# Low miles cases
low_miles_cases = [case for case in day1_cases if case['miles'] < 200]
print(f"Low miles (<200): {len(low_miles_cases)} cases")
if low_miles_cases:
    avg_expected = sum(case['expected'] for case in low_miles_cases) / len(low_miles_cases)
    avg_miles = sum(case['miles'] for case in low_miles_cases) / len(low_miles_cases)
    avg_receipts = sum(case['receipts'] for case in low_miles_cases) / len(low_miles_cases)
    print(f"  Avg: {avg_miles:.0f}mi, ${avg_receipts:.0f}r → ${avg_expected:.2f}")
    
    # Show a few examples
    for case in low_miles_cases[:3]:
        print(f"    Case {case['case']}: {case['miles']}mi, ${case['receipts']}r → ${case['expected']}")

# High miles cases  
high_miles_cases = [case for case in day1_cases if case['miles'] >= 800]
print(f"High miles (≥800): {len(high_miles_cases)} cases")
if high_miles_cases:
    avg_expected = sum(case['expected'] for case in high_miles_cases) / len(high_miles_cases)
    avg_miles = sum(case['miles'] for case in high_miles_cases) / len(high_miles_cases)
    avg_receipts = sum(case['receipts'] for case in high_miles_cases) / len(high_miles_cases)
    print(f"  Avg: {avg_miles:.0f}mi, ${avg_receipts:.0f}r → ${avg_expected:.2f}")
    
    for case in high_miles_cases[:3]:
        print(f"    Case {case['case']}: {case['miles']}mi, ${case['receipts']}r → ${case['expected']}")

# Let's try to manually find the best coefficients
print(f"\nMANUAL COEFFICIENT SEARCH:")

best_error = float('inf')
best_formula = None

# Try different base values
for base in range(0, 200, 25):
    # Try different mileage rates
    for m_rate in [x/100 for x in range(20, 120, 10)]:  # 0.20 to 1.10
        # Try different receipt rates
        for r_rate in [x/100 for x in range(20, 80, 5)]:  # 0.20 to 0.75
            
            total_error = 0
            perfect_matches = 0
            
            for case in day1_cases:
                calculated = base + case['miles'] * m_rate + case['receipts'] * r_rate
                error = abs(calculated - case['expected'])
                total_error += error
                
                if error <= 0.01:
                    perfect_matches += 1
            
            avg_error = total_error / len(day1_cases)
            
            # Check if this is better
            if perfect_matches > 0 or avg_error < best_error:
                if perfect_matches > 0:  # Prioritize perfect matches
                    best_error = avg_error
                    best_formula = (base, m_rate, r_rate, perfect_matches)
                    print(f"Found formula with {perfect_matches} perfect matches: {base} + {m_rate:.2f}*miles + {r_rate:.2f}*receipts (avg error: ${avg_error:.2f})")
                elif avg_error < best_error:
                    best_error = avg_error
                    best_formula = (base, m_rate, r_rate, perfect_matches)

if best_formula:
    base, m_rate, r_rate, perfect = best_formula
    print(f"\nBEST FORMULA FOUND:")
    print(f"${base} + ${m_rate:.2f} * miles + ${r_rate:.2f} * receipts")
    print(f"Average error: ${best_error:.2f}")
    print(f"Perfect matches: {perfect}")
    
    # Test this formula on worst cases
    print(f"\nTesting on worst current cases:")
    test_cases = [
        {'case': 996, 'miles': 1082, 'receipts': 1809.49, 'expected': 446.94},
        {'case': 581, 'miles': 250, 'receipts': 1300, 'expected': 1145.33},
        {'case': 983, 'miles': 309, 'receipts': 1211, 'expected': 1110.55}
    ]
    
    for case in test_cases:
        calculated = base + case['miles'] * m_rate + case['receipts'] * r_rate
        error = abs(calculated - case['expected'])
        print(f"  Case {case['case']}: {case['miles']}mi, ${case['receipts']}r → Expected: ${case['expected']}, Calculated: ${calculated:.2f}, Error: ${error:.2f}")
else:
    print("No good formula found with this approach")