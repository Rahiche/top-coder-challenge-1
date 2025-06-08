#!/usr/bin/env python3
import json

with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Get cases by duration
three_day_cases = [case for case in data if case['input']['trip_duration_days'] == 3]

print('=== 3-DAY TRIP FORMULA DERIVATION ===')

# From the analysis, we found these estimated base rates:
# 1-day: $117.24 per day
# 2-day: $101.76 per day  
# 3-day: $106.71 per day

# It seems like there might be a different base rate structure or the base rate isn't simply linear
print('Observed base rates per day:')
print('1-day trips: $117.24 per day')
print('2-day trips: $101.76 per day') 
print('3-day trips: $106.71 per day')
print()

# Let's assume for 3-day trips: base_per_day = $100 (round number close to observed)
BASE_PER_DAY_3DAY = 100
BASE_3DAY = BASE_PER_DAY_3DAY * 3

print(f'Testing with base per day = ${BASE_PER_DAY_3DAY} (total base = ${BASE_3DAY})')
print()

# Now let's try to derive mileage rate and receipt multiplier
print('=== MILEAGE RATE DERIVATION ===')

# Find cases with minimal receipts to isolate base + mileage
minimal_receipt_cases = []
for case in three_day_cases:
    inp = case['input']
    if inp['total_receipts_amount'] < 50:  # Very low receipts
        minimal_receipt_cases.append(case)

# Sort by miles to see mileage pattern
minimal_receipt_cases.sort(key=lambda x: x['input']['miles_traveled'])

print('Cases with minimal receipts (< $50), sorted by miles:')
for case in minimal_receipt_cases:
    inp = case['input']
    out = case['expected_output']
    estimated_mileage_component = out - BASE_3DAY
    rate_per_mile = estimated_mileage_component / inp['miles_traveled'] if inp['miles_traveled'] > 0 else 0
    
    print(f'Miles: {inp["miles_traveled"]:3d}, Receipts: ${inp["total_receipts_amount"]:5.2f}, '
          f'Output: ${out:6.2f}, Mileage component: ${estimated_mileage_component:6.2f}, '
          f'Rate per mile: ${rate_per_mile:.4f}')

# Try to find a consistent mileage rate
print()
print('=== LOOKING FOR MILEAGE RATE PATTERN ===')

# Let's try different possible mileage rates and see which one fits best
possible_rates = [0.4, 0.5, 0.55, 0.6, 0.65, 0.7]

for rate in possible_rates:
    print(f'\\nTesting mileage rate: ${rate:.2f} per mile')
    errors = []
    
    for case in minimal_receipt_cases:
        inp = case['input']
        out = case['expected_output']
        
        predicted = BASE_3DAY + (inp['miles_traveled'] * rate)
        error = abs(out - predicted)
        errors.append(error)
        
        if len(errors) <= 5:  # Show first 5 cases
            print(f'  Miles: {inp["miles_traveled"]:3d}, Actual: ${out:6.2f}, '
                  f'Predicted: ${predicted:6.2f}, Error: ${error:5.2f}')
    
    avg_error = sum(errors) / len(errors) if errors else 0
    print(f'  Average error: ${avg_error:.2f}')

print()
print('=== RECEIPT MULTIPLIER ANALYSIS ===')

# Once we have base + mileage, remaining should be receipt component
# Let's use a reasonable mileage rate (e.g., $0.6) and see receipt pattern
MILEAGE_RATE = 0.60

print(f'Using base=${BASE_3DAY}, mileage_rate=${MILEAGE_RATE:.2f}/mile')
print()

receipt_multipliers = []
for case in three_day_cases:
    inp = case['input']
    out = case['expected_output']
    
    base_plus_mileage = BASE_3DAY + (inp['miles_traveled'] * MILEAGE_RATE)
    receipt_component = out - base_plus_mileage
    
    if inp['total_receipts_amount'] > 0:
        multiplier = receipt_component / inp['total_receipts_amount']
        receipt_multipliers.append(multiplier)

if receipt_multipliers:
    print(f'Receipt multiplier statistics:')
    print(f'  Range: {min(receipt_multipliers):.4f} to {max(receipt_multipliers):.4f}')
    print(f'  Average: {sum(receipt_multipliers)/len(receipt_multipliers):.4f}')
    
    # Look for common values
    common_multipliers = []
    for mult in receipt_multipliers:
        if 0.4 <= mult <= 0.8:  # Reasonable range
            common_multipliers.append(mult)
    
    if common_multipliers:
        print(f'  Common range (0.4-0.8): {len(common_multipliers)} cases')
        print(f'  Average in range: {sum(common_multipliers)/len(common_multipliers):.4f}')

# Test the complete formula
print()
print('=== TESTING COMPLETE FORMULA ===')
RECEIPT_MULTIPLIER = 0.6  # Estimate from analysis

print(f'Formula: total = ${BASE_3DAY} + ({MILEAGE_RATE:.2f} * miles) + ({RECEIPT_MULTIPLIER:.2f} * receipts)')
print()
print('Testing on first 10 cases:')

for i, case in enumerate(three_day_cases[:10]):
    inp = case['input']
    actual = case['expected_output']
    
    predicted = BASE_3DAY + (MILEAGE_RATE * inp['miles_traveled']) + (RECEIPT_MULTIPLIER * inp['total_receipts_amount'])
    error = abs(actual - predicted)
    
    print(f'Case {i+1}: Miles={inp["miles_traveled"]:3d}, Receipts=${inp["total_receipts_amount"]:6.2f}')
    print(f'  Actual: ${actual:6.2f}, Predicted: ${predicted:6.2f}, Error: ${error:5.2f}')