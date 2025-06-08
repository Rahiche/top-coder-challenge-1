import json

with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

print("=== FINAL ANALYSIS: EFFECTIVE MILEAGE RATES BY RANGE (NON-CAPPED CASES) ===")

# Analyze non-capped cases across different mileage ranges
mileage_ranges = [
    (0, 200, "0-200 miles"),
    (200, 400, "200-400 miles"), 
    (400, 600, "400-600 miles"),
    (600, 800, "600-800 miles"),
    (800, 1000, "800-1000 miles"),
    (1000, 1200, "1000-1200 miles"),
    (1200, float('inf'), "1200+ miles")
]

for min_miles, max_miles, label in mileage_ranges:
    # Get non-capped cases in this range
    range_cases = []
    for case in data:
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        output = case['expected_output']
        
        # Only include non-capped cases
        if min_miles <= miles < max_miles and receipts <= output:
            days = case['input']['trip_duration_days']
            miles_component = output - receipts
            rate = miles_component / miles
            range_cases.append({
                'miles': miles,
                'days': days,
                'receipts': receipts,
                'output': output,
                'rate': rate
            })
    
    if range_cases:
        rates = [c['rate'] for c in range_cases]
        avg_rate = sum(rates) / len(rates)
        min_rate = min(rates)
        max_rate = max(rates)
        
        print(f"\n{label}: {len(range_cases)} non-capped cases")
        print(f"  Avg rate: ${avg_rate:.4f}/mile (range: ${min_rate:.4f} - ${max_rate:.4f})")
        
        # Show a few examples
        range_cases.sort(key=lambda x: x['rate'], reverse=True)
        print(f"  Top examples:")
        for i, case in enumerate(range_cases[:3]):
            print(f"    {case['miles']:4.0f} miles, {case['days']:2d} days, rate: ${case['rate']:.4f}/mile")

print("\n" + "="*60)
print("KEY FINDINGS:")

# Calculate overall stats for high mileage (800+) non-capped vs lower mileage
high_mileage_non_capped = []
lower_mileage_non_capped = []

for case in data:
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    
    # Only non-capped cases
    if receipts <= output:
        rate = (output - receipts) / miles
        if miles >= 800:
            high_mileage_non_capped.append(rate)
        else:
            lower_mileage_non_capped.append(rate)

avg_high = sum(high_mileage_non_capped) / len(high_mileage_non_capped) if high_mileage_non_capped else 0
avg_lower = sum(lower_mileage_non_capped) / len(lower_mileage_non_capped) if lower_mileage_non_capped else 0

print(f"\n1. Non-capped cases comparison:")
print(f"   High mileage (800+): {len(high_mileage_non_capped)} cases, avg rate: ${avg_high:.4f}/mile")
print(f"   Lower mileage (<800): {len(lower_mileage_non_capped)} cases, avg rate: ${avg_lower:.4f}/mile")

if avg_high > avg_lower:
    print(f"   => HIGH MILEAGE GETS BETTER TREATMENT: +${avg_high - avg_lower:.4f}/mile premium")
else:
    print(f"   => High mileage gets worse treatment: ${avg_high - avg_lower:.4f}/mile penalty")

# Analyze the impact of reimbursement caps
all_high_mileage = [c for c in data if c['input']['miles_traveled'] >= 800]
capped_high_mileage = [c for c in all_high_mileage if c['input']['total_receipts_amount'] > c['expected_output']]

print(f"\n2. Impact of reimbursement caps on high mileage:")
print(f"   Total high mileage cases: {len(all_high_mileage)}")
print(f"   Capped cases: {len(capped_high_mileage)} ({len(capped_high_mileage)/len(all_high_mileage)*100:.1f}%)")
print(f"   Non-capped cases: {len(high_mileage_non_capped)} ({len(high_mileage_non_capped)/len(all_high_mileage)*100:.1f}%)")

print(f"\n3. Effective rate difference:")
print(f"   Without caps, high mileage gets: ${avg_high:.4f}/mile")
print(f"   This is {'BETTER' if avg_high > avg_lower else 'WORSE'} than lower mileage at ${avg_lower:.4f}/mile")
print(f"   Premium/penalty: ${avg_high - avg_lower:.4f}/mile")

# Look at very high mileage (1000+) specifically  
very_high_non_capped = [rate for case in data 
                       if case['input']['miles_traveled'] >= 1000 
                       and case['input']['total_receipts_amount'] <= case['expected_output']
                       for rate in [(case['expected_output'] - case['input']['total_receipts_amount']) / case['input']['miles_traveled']]]

avg_very_high = sum(very_high_non_capped) / len(very_high_non_capped) if very_high_non_capped else 0

print(f"\n4. Very high mileage (1000+) non-capped analysis:")
print(f"   Cases: {len(very_high_non_capped)}")
print(f"   Average rate: ${avg_very_high:.4f}/mile")
print(f"   vs 800-1000 mile average: ~${avg_high:.4f}/mile")

if avg_very_high > avg_high:
    print(f"   => Very high mileage gets even better treatment!")
else:
    print(f"   => Very high mileage gets slightly worse treatment")