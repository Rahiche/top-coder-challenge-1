import json

with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

# Find cases with 800+ miles
high_mileage_cases = []
for case in data:
    miles = case['input']['miles_traveled']
    if miles >= 800:
        days = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        output = case['expected_output']
        high_mileage_cases.append({
            'miles': miles,
            'days': days, 
            'receipts': receipts,
            'output': output
        })

# Sort by miles
high_mileage_cases.sort(key=lambda x: x['miles'])

print(f'Found {len(high_mileage_cases)} cases with 800+ miles')
print()

# Analyze patterns by looking at different ranges
print("=== ANALYSIS BY MILEAGE RANGES ===")
ranges = [
    (800, 850, "800-850 miles"),
    (850, 900, "850-900 miles"), 
    (900, 950, "900-950 miles"),
    (950, 1000, "950-1000 miles"),
    (1000, 1100, "1000-1100 miles"),
    (1100, 1200, "1100-1200 miles"),
    (1200, float('inf'), "1200+ miles")
]

for min_miles, max_miles, label in ranges:
    range_cases = [c for c in high_mileage_cases if min_miles <= c['miles'] < max_miles]
    if range_cases:
        print(f"\n{label}: {len(range_cases)} cases")
        rates = []
        for case in range_cases[:5]:  # Show first 5 in each range
            miles_component = case['output'] - case['receipts']
            per_mile_rate = miles_component / case['miles'] if case['miles'] > 0 else 0
            rates.append(per_mile_rate)
            print(f"  {case['miles']:4.0f} miles, {case['days']:2d} days, output: ${case['output']:7.2f}, rate: ${per_mile_rate:.4f}/mile")
        
        if rates:
            avg_rate = sum(rates) / len(rates)
            print(f"  Avg rate in sample: ${avg_rate:.4f}/mile")

# Look for short vs long trips with high mileage
print("\n=== SHORT vs LONG TRIPS (800+ miles) ===")
short_trips = [c for c in high_mileage_cases if c['days'] <= 3]
long_trips = [c for c in high_mileage_cases if c['days'] >= 10]

print(f"\nShort trips (1-3 days): {len(short_trips)} cases")
for case in short_trips[:10]:
    miles_component = case['output'] - case['receipts']
    per_mile_rate = miles_component / case['miles']
    print(f"  {case['miles']:4.0f} miles, {case['days']} days, rate: ${per_mile_rate:.4f}/mile")

print(f"\nLong trips (10+ days): {len(long_trips)} cases") 
for case in long_trips[:10]:
    miles_component = case['output'] - case['receipts']
    per_mile_rate = miles_component / case['miles']
    print(f"  {case['miles']:4.0f} miles, {case['days']} days, rate: ${per_mile_rate:.4f}/mile")

# Calculate average rates
if short_trips:
    short_rates = [(c['output'] - c['receipts']) / c['miles'] for c in short_trips]
    avg_short_rate = sum(short_rates) / len(short_rates)
    print(f"\nAverage rate for short high-mileage trips: ${avg_short_rate:.4f}/mile")

if long_trips:
    long_rates = [(c['output'] - c['receipts']) / c['miles'] for c in long_trips]
    avg_long_rate = sum(long_rates) / len(long_rates)
    print(f"Average rate for long high-mileage trips: ${avg_long_rate:.4f}/mile")