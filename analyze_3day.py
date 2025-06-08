#!/usr/bin/env python3
import json

with open('public_cases.json', 'r') as f:
    data = json.load(f)

three_day_cases = [case for case in data if case['input']['trip_duration_days'] == 3]

print('=== MILEAGE RATE ANALYSIS FOR 3-DAY TRIPS ===')
print(f'Total 3-day cases: {len(three_day_cases)}')
print()

print('Cases with receipts < $25:')
base_cases = []
for case in three_day_cases:
    inp = case['input']
    out = case['expected_output']
    if inp['total_receipts_amount'] < 25:
        base_cases.append(case)
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        per_day = out / 3
        print(f'Miles: {miles:3d}, Receipts: ${receipts:5.2f}, Per-day: ${per_day:6.2f}, Total: ${out:6.2f}')

print()
if len(base_cases) >= 2:
    case1 = base_cases[0]
    case2 = base_cases[1]
    
    miles1 = case1['input']['miles_traveled']
    output1 = case1['expected_output']
    
    miles2 = case2['input']['miles_traveled'] 
    output2 = case2['expected_output']
    
    if miles2 != miles1:
        rate_per_mile = (output2 - output1) / (miles2 - miles1)
        base_3_day = output1 - (miles1 * rate_per_mile)
        
        print(f'Using cases with miles {miles1} and {miles2}:')
        print(f'Estimated rate per mile: ${rate_per_mile:.4f}')
        print(f'Estimated base for 3 days: ${base_3_day:.2f}')
        print(f'Estimated base per day: ${base_3_day/3:.2f}')
        print()
        
        # Test on more low-receipt cases
        print('Testing formula on low-receipt cases:')
        for i, case in enumerate(base_cases):
            inp = case['input']
            actual = case['expected_output']
            predicted = base_3_day + (inp['miles_traveled'] * rate_per_mile)
            
            print(f'Case {i+1}: Miles={inp["miles_traveled"]}, Receipts=${inp["total_receipts_amount"]:.2f}')
            print(f'  Actual: ${actual:.2f}, Predicted: ${predicted:.2f}, Diff: ${abs(actual-predicted):.2f}')

print()
print('=== RECEIPT ANALYSIS ===')
# Group cases by receipt ranges
receipt_ranges = [
    (0, 50, 'Low'),
    (50, 200, 'Med-Low'), 
    (200, 500, 'Medium'),
    (500, 1000, 'Med-High'),
    (1000, float('inf'), 'High')
]

for min_r, max_r, label in receipt_ranges:
    cases_in_range = []
    for case in three_day_cases:
        receipts = case['input']['total_receipts_amount']
        if min_r <= receipts < max_r:
            cases_in_range.append(case)
    
    if cases_in_range:
        per_day_rates = [case['expected_output'] / 3 for case in cases_in_range]
        print(f'{label} receipts (${min_r}-${max_r if max_r != float("inf") else "∞"}): {len(cases_in_range)} cases')
        print(f'  Per-day range: ${min(per_day_rates):.2f} - ${max(per_day_rates):.2f}')
        print(f'  Average per-day: ${sum(per_day_rates)/len(per_day_rates):.2f}')