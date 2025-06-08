#!/usr/bin/env python3
import json

with open('public_cases.json', 'r') as f:
    data = json.load(f)

three_day_cases = [case for case in data if case['input']['trip_duration_days'] == 3]

print('=== 3-DAY TRIP CAPS AND LIMITS ANALYSIS ===')

# Let's look at high mileage cases to see if there's a mileage cap
print('High mileage cases (>500 miles):')
high_mileage = []
for case in three_day_cases:
    inp = case['input']
    if inp['miles_traveled'] > 500:
        high_mileage.append(case)

high_mileage.sort(key=lambda x: x['input']['miles_traveled'])

for case in high_mileage:
    inp = case['input']
    out = case['expected_output']
    per_day = out / 3
    mileage_per_dollar = inp['miles_traveled'] / out
    
    print(f'Miles: {inp["miles_traveled"]:4.0f}, Receipts: ${inp["total_receipts_amount"]:7.2f}, '
          f'Output: ${out:7.2f}, Per-day: ${per_day:6.2f}, Miles/\$: {mileage_per_dollar:.3f}')

print()
print('=== HIGH RECEIPT CASES ANALYSIS ===')
print('High receipt cases (>$1000):')

high_receipt = []
for case in three_day_cases:
    inp = case['input']
    if inp['total_receipts_amount'] > 1000:
        high_receipt.append(case)

high_receipt.sort(key=lambda x: x['input']['total_receipts_amount'])

for case in high_receipt[:15]:  # Show first 15
    inp = case['input']
    out = case['expected_output']
    per_day = out / 3
    receipt_ratio = out / inp['total_receipts_amount'] if inp['total_receipts_amount'] > 0 else 0
    
    print(f'Receipts: ${inp["total_receipts_amount"]:7.2f}, Miles: {inp["miles_traveled"]:3.0f}, '
          f'Output: ${out:7.2f}, Per-day: ${per_day:6.2f}, Ratio: {receipt_ratio:.3f}')

print()
print('=== RECEIPT RATIO ANALYSIS ===')

# Look for receipt ratio patterns - is there a cap or different treatment?
receipt_ratios = []
for case in three_day_cases:
    inp = case['input']
    out = case['expected_output']
    if inp['total_receipts_amount'] > 0:
        ratio = out / inp['total_receipts_amount']
        receipt_ratios.append((ratio, inp['total_receipts_amount'], out))

receipt_ratios.sort(key=lambda x: x[1])  # Sort by receipt amount

print('Receipt ratios by receipt amount:')
for i, (ratio, receipts, output) in enumerate(receipt_ratios):
    if i % 10 == 0 or receipts > 1000:  # Show every 10th case or high receipt cases
        print(f'Receipts: ${receipts:7.2f}, Output: ${output:7.2f}, Ratio: {ratio:.3f}')

print()
print('=== LOOKING FOR RECEIPT CAPS ===')

# Check if there's a pattern where receipts above a certain amount have diminishing returns
receipt_categories = [
    (0, 200),
    (200, 500), 
    (500, 1000),
    (1000, 1500),
    (1500, 2500),
    (2500, float('inf'))
]

for min_r, max_r in receipt_categories:
    cases_in_range = []
    for case in three_day_cases:
        receipts = case['input']['total_receipts_amount']
        if min_r <= receipts < max_r:
            cases_in_range.append(case)
    
    if cases_in_range:
        ratios = []
        for case in cases_in_range:
            inp = case['input']
            out = case['expected_output']
            ratio = out / inp['total_receipts_amount']
            ratios.append(ratio)
        
        avg_ratio = sum(ratios) / len(ratios)
        print(f'Receipts ${min_r}-${max_r if max_r != float("inf") else "∞"}: '
              f'{len(cases_in_range)} cases, avg ratio: {avg_ratio:.3f}')

print()
print('=== POTENTIAL TIERED FORMULA ANALYSIS ===')

# Maybe there are different rates for different receipt ranges
# Let's see if we can find a pattern

# Look at cases with similar miles but different receipt amounts to isolate receipt component
print('Cases with similar mileage (50-100 miles) to isolate receipt effects:')

similar_mile_cases = []
for case in three_day_cases:
    inp = case['input']
    if 50 <= inp['miles_traveled'] <= 100:
        similar_mile_cases.append(case)

similar_mile_cases.sort(key=lambda x: x['input']['total_receipts_amount'])

base_case = None
for case in similar_mile_cases:
    inp = case['input']
    out = case['expected_output']
    
    if base_case is None:
        base_case = case
        print(f'Base case: Miles={inp["miles_traveled"]}, Receipts=${inp["total_receipts_amount"]:.2f}, Output=${out:.2f}')
    else:
        base_inp = base_case['input']
        base_out = base_case['expected_output']
        
        receipt_diff = inp['total_receipts_amount'] - base_inp['total_receipts_amount']
        output_diff = out - base_out
        mile_diff = inp['miles_traveled'] - base_inp['miles_traveled']
        
        if receipt_diff > 0:
            effective_receipt_rate = output_diff / receipt_diff
            print(f'Miles={inp["miles_traveled"]} (+{mile_diff}), Receipts=${inp["total_receipts_amount"]:.2f} (+${receipt_diff:.2f}), '
                  f'Output=${out:.2f} (+${output_diff:.2f}), Eff. rate: {effective_receipt_rate:.3f}')