#!/usr/bin/env python3
import json

with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Get all cases
one_day_cases = [case for case in data if case['input']['trip_duration_days'] == 1]
two_day_cases = [case for case in data if case['input']['trip_duration_days'] == 2]
three_day_cases = [case for case in data if case['input']['trip_duration_days'] == 3]

print('=== COMPREHENSIVE PATTERN ANALYSIS ===')
print(f'1-day cases: {len(one_day_cases)}')
print(f'2-day cases: {len(two_day_cases)}')
print(f'3-day cases: {len(three_day_cases)}')
print()

# Look for base rate pattern by finding minimal cases
def find_base_cases(cases, duration):
    print(f'=== {duration}-DAY BASE RATE ANALYSIS ===')
    
    # Find cases with low miles and low receipts
    minimal_cases = []
    for case in cases:
        inp = case['input']
        if inp['miles_traveled'] < 200 and inp['total_receipts_amount'] < 100:
            minimal_cases.append(case)
    
    # Sort by total output to see the pattern
    minimal_cases.sort(key=lambda x: x['expected_output'])
    
    print(f'Cases with < 200 miles and < $100 receipts (sorted by output):')
    for i, case in enumerate(minimal_cases[:15]):
        inp = case['input']
        out = case['expected_output']
        per_day = out / duration
        
        print(f'{i+1:2d}: Miles={inp["miles_traveled"]:3d}, Receipts=${inp["total_receipts_amount"]:5.2f}, '
              f'Total=${out:6.2f}, Per-day=${per_day:6.2f}')
    
    # Try to identify base rate
    if minimal_cases:
        lowest_case = minimal_cases[0]
        lowest_per_day = lowest_case['expected_output'] / duration
        print(f'\nLowest per-day rate: ${lowest_per_day:.2f}')
        
        # Look for approximate base rate
        base_candidates = []
        for case in minimal_cases[:10]:
            per_day = case['expected_output'] / duration
            base_candidates.append(per_day)
        
        # Find most common base rate (within small range)
        base_estimate = min(base_candidates)
        print(f'Estimated base per day: ${base_estimate:.2f}')
        print(f'Estimated base for {duration} days: ${base_estimate * duration:.2f}')
    
    print()

# Analyze each duration
find_base_cases(one_day_cases, 1)
find_base_cases(two_day_cases, 2)
find_base_cases(three_day_cases, 3)

# Focus on 3-day analysis
print('=== DETAILED 3-DAY FORMULA DERIVATION ===')

# Look at cases with very similar miles but different receipts
print('Cases with similar mileage (within 10 miles of each other):')

three_day_sorted = sorted(three_day_cases, key=lambda x: x['input']['miles_traveled'])
for i in range(len(three_day_sorted) - 1):
    case1 = three_day_sorted[i]
    case2 = three_day_sorted[i + 1]
    
    miles1 = case1['input']['miles_traveled']
    miles2 = case2['input']['miles_traveled']
    
    if abs(miles1 - miles2) <= 10:
        inp1 = case1['input']
        inp2 = case2['input']
        out1 = case1['expected_output']
        out2 = case2['expected_output']
        
        receipt_diff = inp2['total_receipts_amount'] - inp1['total_receipts_amount']
        output_diff = out2 - out1
        
        if receipt_diff > 0:
            receipt_impact = output_diff / receipt_diff
        else:
            receipt_impact = 0
            
        print(f'Miles ~{miles1}: Receipt diff=${receipt_diff:.2f}, Output diff=${output_diff:.2f}, '
              f'Impact per $ receipt={receipt_impact:.4f}')
        
        if i >= 5:  # Limit output
            break

print()
print('=== 3-DAY RECEIPT IMPACT ANALYSIS ===')

# Analyze receipt impact more systematically
receipt_impacts = []
for i, case1 in enumerate(three_day_cases):
    for j, case2 in enumerate(three_day_cases):
        if i >= j:
            continue
            
        inp1 = case1['input']
        inp2 = case2['input']
        
        # Only compare cases with similar mileage
        if abs(inp1['miles_traveled'] - inp2['miles_traveled']) <= 20:
            receipt_diff = inp2['total_receipts_amount'] - inp1['total_receipts_amount']
            output_diff = case2['expected_output'] - case1['expected_output']
            
            if abs(receipt_diff) > 10:  # Significant receipt difference
                impact = output_diff / receipt_diff if receipt_diff != 0 else 0
                receipt_impacts.append(impact)

if receipt_impacts:
    print(f'Receipt impact analysis from {len(receipt_impacts)} case pairs:')
    print(f'Receipt impact range: ${min(receipt_impacts):.4f} to ${max(receipt_impacts):.4f} per dollar')
    print(f'Average receipt impact: ${sum(receipt_impacts)/len(receipt_impacts):.4f} per dollar')