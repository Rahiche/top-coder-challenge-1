import json

# Read the first 50 cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

cases = data[:50]

# Analyze each case
analysis = []
for i, case in enumerate(cases):
    inp = case['input']
    output = case['expected_output']
    
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    per_diem = output / days
    
    analysis.append({
        'case': i + 1,
        'days': days,
        'miles': miles,
        'receipts': receipts,
        'output': output,
        'per_diem': round(per_diem, 2),
        'output_per_mile': round(output / miles, 2) if miles > 0 else 0,
        'receipts_ratio': round(output / receipts, 2) if receipts > 0 else 0
    })

# Group by days to find patterns
by_days = {}
for a in analysis:
    days = a['days']
    if days not in by_days:
        by_days[days] = []
    by_days[days].append(a)

# Print analysis
print("DETAILED ANALYSIS OF FIRST 50 CASES")
print("=" * 80)

for a in analysis[:20]:  # First 20 for detail
    print(f"Case {a['case']}:")
    print(f"  Input: {a['days']} days, {a['miles']} miles, ${a['receipts']:.2f} receipts")
    print(f"  Output: ${a['output']:.2f}")
    print(f"  Per diem: ${a['per_diem']:.2f}")
    print(f"  Per mile: ${a['output_per_mile']:.2f}")
    print(f"  Output/Receipts ratio: {a['receipts_ratio']:.2f}")
    print()

# Look for patterns by trip duration
print("\nPATTERNS BY TRIP DURATION:")
print("=" * 80)

for days in sorted(by_days.keys()):
    cases_for_days = by_days[days]
    print(f"\n{days}-day trips ({len(cases_for_days)} cases):")
    
    per_diems = [c['per_diem'] for c in cases_for_days]
    miles_list = [c['miles'] for c in cases_for_days]
    receipts_list = [c['receipts'] for c in cases_for_days]
    outputs = [c['output'] for c in cases_for_days]
    
    print(f"  Per diem range: ${min(per_diems):.2f} - ${max(per_diems):.2f}")
    print(f"  Miles range: {min(miles_list)} - {max(miles_list)}")
    print(f"  Receipts range: ${min(receipts_list):.2f} - ${max(receipts_list):.2f}")
    print(f"  Output range: ${min(outputs):.2f} - ${max(outputs):.2f}")
    
    # Show some examples
    print(f"  Examples:")
    for c in cases_for_days[:3]:
        print(f"    - {c['miles']} miles, ${c['receipts']:.2f} receipts -> ${c['output']:.2f} (${c['per_diem']:.2f}/day)")

# Try to find base rates
print("\nLOOKING FOR BASE RATES:")
print("=" * 80)

# Look at 1-day trips with low receipts
one_day_low_receipts = [c for c in by_days.get(1, []) if c['receipts'] < 10]
print(f"\n1-day trips with receipts < $10:")
for c in one_day_low_receipts:
    print(f"  {c['miles']} miles, ${c['receipts']:.2f} receipts -> ${c['output']:.2f}")

# Look for mileage patterns
print("\nMILEAGE IMPACT ANALYSIS:")
print("=" * 80)

# Group 1-day trips by similar receipt amounts
one_day = by_days.get(1, [])
receipt_groups = {}
for c in one_day:
    bucket = int(c['receipts'] / 5) * 5  # Group in $5 buckets
    if bucket not in receipt_groups:
        receipt_groups[bucket] = []
    receipt_groups[bucket].append(c)

for bucket in sorted(receipt_groups.keys()):
    if len(receipt_groups[bucket]) > 1:
        print(f"\n1-day trips with receipts ~${bucket}-${bucket+5}:")
        for c in sorted(receipt_groups[bucket], key=lambda x: x['miles']):
            print(f"  {c['miles']} miles, ${c['receipts']:.2f} receipts -> ${c['output']:.2f}")

# Look at 5-day trips with high variation
print("\n5-DAY TRIP PATTERNS:")
print("=" * 80)
five_day = by_days.get(5, [])
if five_day:
    # Sort by receipts
    five_day_sorted = sorted(five_day, key=lambda x: x['receipts'])
    print("\nSorted by receipts:")
    for c in five_day_sorted[:10]:
        print(f"  {c['miles']} miles, ${c['receipts']:.2f} receipts -> ${c['output']:.2f} (${c['per_diem']:.2f}/day)")
    
    # Calculate potential formulas
    print("\nTrying to reverse engineer formula for 5-day trips:")
    for c in five_day_sorted[:5]:
        base = 100 * c['days']  # Assume $100 base per day
        mile_contrib = c['output'] - base - c['receipts']
        mile_rate = mile_contrib / c['miles'] if c['miles'] > 0 else 0
        print(f"  Case: {c['miles']} mi, ${c['receipts']:.2f} receipts -> ${c['output']:.2f}")
        print(f"    If base=$100/day: mileage contribution = ${mile_contrib:.2f} (${mile_rate:.2f}/mile)")