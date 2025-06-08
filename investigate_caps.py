import json

with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

print("=== INVESTIGATING REIMBURSEMENT CAPS ===")

# The negative rates suggest there might be reimbursement caps
# Let's analyze this by looking at the relationship between receipts and output

print("\nCases where receipts > output (suggesting caps):")
capped_cases = []
for case in data:
    miles = case['input']['miles_traveled']
    days = case['input']['trip_duration_days'] 
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    
    if receipts > output:
        capped_cases.append(case)

print(f"Found {len(capped_cases)} cases where receipts > output")

# Look at high mileage capped cases
high_mileage_capped = [c for c in capped_cases if c['input']['miles_traveled'] >= 800]
print(f"High mileage capped cases: {len(high_mileage_capped)}")

# Analyze the pattern
print("\nSample of high-mileage capped cases:")
for i, case in enumerate(high_mileage_capped[:10]):
    miles = case['input']['miles_traveled']
    days = case['input']['trip_duration_days']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    excess_receipts = receipts - output
    print(f"{i+1:2d}. {miles:4.0f} miles, {days:2d} days, receipts: ${receipts:7.2f}, output: ${output:7.2f}, excess: ${excess_receipts:6.2f}")

# Look for patterns in the caps
print("\n=== ANALYZING CAP PATTERNS ===")

# Group by trip duration to see if caps are per-day based
caps_by_duration = {}
for case in high_mileage_capped:
    days = case['input']['trip_duration_days']
    output = case['expected_output']
    
    if days not in caps_by_duration:
        caps_by_duration[days] = []
    caps_by_duration[days].append(output)

print("\nCap amounts by trip duration (for high-mileage capped cases):")
for days in sorted(caps_by_duration.keys()):
    outputs = caps_by_duration[days]
    min_cap = min(outputs)
    max_cap = max(outputs)
    avg_cap = sum(outputs) / len(outputs)
    print(f"{days:2d} days: {len(outputs):2d} cases, caps range ${min_cap:7.2f} - ${max_cap:7.2f}, avg ${avg_cap:7.2f}")

# Let's also look at non-capped high mileage cases to see what normal reimbursement looks like
print("\n=== NON-CAPPED HIGH MILEAGE CASES ===")
high_mileage_cases = [c for c in data if c['input']['miles_traveled'] >= 800]
non_capped_high = [c for c in high_mileage_cases if c['input']['total_receipts_amount'] <= c['expected_output']]

print(f"Non-capped high mileage cases: {len(non_capped_high)}")

# Look at effective per-mile rates for non-capped cases
print("\nSample non-capped high mileage cases:")
for i, case in enumerate(non_capped_high[:10]):
    miles = case['input']['miles_traveled']
    days = case['input']['trip_duration_days']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    miles_component = output - receipts
    rate = miles_component / miles
    print(f"{i+1:2d}. {miles:4.0f} miles, {days:2d} days, receipts: ${receipts:7.2f}, output: ${output:7.2f}, rate: ${rate:.4f}/mile")

# Calculate average rates for different groups
capped_high_rates = []
non_capped_high_rates = []

for case in high_mileage_capped:
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    rate = (output - receipts) / miles
    capped_high_rates.append(rate)

for case in non_capped_high:
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    rate = (output - receipts) / miles
    non_capped_high_rates.append(rate)

avg_capped_rate = sum(capped_high_rates) / len(capped_high_rates) if capped_high_rates else 0
avg_non_capped_rate = sum(non_capped_high_rates) / len(non_capped_high_rates) if non_capped_high_rates else 0

print(f"\nAverage effective rate for capped high-mileage cases: ${avg_capped_rate:.4f}/mile")
print(f"Average effective rate for non-capped high-mileage cases: ${avg_non_capped_rate:.4f}/mile")
print(f"Difference: ${avg_non_capped_rate - avg_capped_rate:.4f}/mile")

# Look at what happens when we exclude capped cases
print(f"\nKey insight: When high receipts hit reimbursement caps,")
print(f"the effective mileage rate becomes negative (${avg_capped_rate:.4f}/mile)")
print(f"But for normal cases, high mileage gets ${avg_non_capped_rate:.4f}/mile")