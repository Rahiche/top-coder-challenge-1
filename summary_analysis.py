import json

with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

print("="*70)
print("COMPREHENSIVE HIGH-MILEAGE ANALYSIS SUMMARY")
print("="*70)

# Get all high mileage cases (800+)
high_mileage_cases = [c for c in data if c['input']['miles_traveled'] >= 800]
capped_cases = [c for c in high_mileage_cases if c['input']['total_receipts_amount'] > c['expected_output']]
non_capped_cases = [c for c in high_mileage_cases if c['input']['total_receipts_amount'] <= c['expected_output']]

print(f"\n1. OVERVIEW OF HIGH MILEAGE (800+ miles) CASES:")
print(f"   • Total cases: {len(high_mileage_cases)}")
print(f"   • Non-capped cases: {len(non_capped_cases)} ({len(non_capped_cases)/len(high_mileage_cases)*100:.1f}%)")
print(f"   • Capped cases: {len(capped_cases)} ({len(capped_cases)/len(high_mileage_cases)*100:.1f}%)")

# Analyze effective rates
capped_rates = [(c['expected_output'] - c['input']['total_receipts_amount']) / c['input']['miles_traveled'] for c in capped_cases]
non_capped_rates = [(c['expected_output'] - c['input']['total_receipts_amount']) / c['input']['miles_traveled'] for c in non_capped_cases]

avg_capped = sum(capped_rates) / len(capped_rates) if capped_rates else 0
avg_non_capped = sum(non_capped_rates) / len(non_capped_rates) if non_capped_rates else 0

print(f"\n2. EFFECTIVE MILEAGE RATES:")
print(f"   • Non-capped high mileage: ${avg_non_capped:.4f}/mile")
print(f"   • Capped high mileage: ${avg_capped:.4f}/mile (negative due to caps)")
print(f"   • Overall high mileage: ${(sum(capped_rates) + sum(non_capped_rates)) / (len(capped_rates) + len(non_capped_rates)):.4f}/mile")

# Compare with lower mileage
lower_mileage_non_capped = [(c['expected_output'] - c['input']['total_receipts_amount']) / c['input']['miles_traveled'] 
                           for c in data 
                           if c['input']['miles_traveled'] < 800 and c['input']['total_receipts_amount'] <= c['expected_output']]
avg_lower = sum(lower_mileage_non_capped) / len(lower_mileage_non_capped) if lower_mileage_non_capped else 0

print(f"   • Lower mileage (<800): ${avg_lower:.4f}/mile")

# Key finding
print(f"\n3. KEY FINDING:")
if avg_non_capped > avg_lower:
    print(f"   ✓ HIGH MILEAGE GETS BETTER TREATMENT when not capped")
    print(f"     Premium: +${avg_non_capped - avg_lower:.4f}/mile")
else:
    print(f"   ✗ HIGH MILEAGE GETS WORSE TREATMENT even when not capped")
    print(f"     Penalty: ${avg_non_capped - avg_lower:.4f}/mile")

# Analyze by mileage tiers within high mileage
tiers = [
    (800, 900, "800-900 miles"),
    (900, 1000, "900-1000 miles"), 
    (1000, 1100, "1000-1100 miles"),
    (1100, 1200, "1100-1200 miles"),
    (1200, float('inf'), "1200+ miles")
]

print(f"\n4. HIGH MILEAGE TIERED RATES (non-capped only):")
for min_m, max_m, label in tiers:
    tier_cases = [c for c in non_capped_cases if min_m <= c['input']['miles_traveled'] < max_m]
    if tier_cases:
        tier_rates = [(c['expected_output'] - c['input']['total_receipts_amount']) / c['input']['miles_traveled'] for c in tier_cases]
        avg_tier = sum(tier_rates) / len(tier_rates)
        print(f"   • {label}: ${avg_tier:.4f}/mile ({len(tier_cases)} cases)")

# Analyze short vs long trips for high mileage
short_high = [c for c in non_capped_cases if c['input']['trip_duration_days'] <= 3]
long_high = [c for c in non_capped_cases if c['input']['trip_duration_days'] >= 10]

short_rates = [(c['expected_output'] - c['input']['total_receipts_amount']) / c['input']['miles_traveled'] for c in short_high]
long_rates = [(c['expected_output'] - c['input']['total_receipts_amount']) / c['input']['miles_traveled'] for c in long_high]

avg_short = sum(short_rates) / len(short_rates) if short_rates else 0
avg_long = sum(long_rates) / len(long_rates) if long_rates else 0

print(f"\n5. SHORT vs LONG HIGH-MILEAGE TRIPS (non-capped):")
print(f"   • Short trips (1-3 days): ${avg_short:.4f}/mile ({len(short_high)} cases)")
print(f"   • Long trips (10+ days): ${avg_long:.4f}/mile ({len(long_high)} cases)")

if avg_long > avg_short:
    print(f"   → Long high-mileage trips get +${avg_long - avg_short:.4f}/mile premium")
else:
    print(f"   → Short high-mileage trips get +${avg_short - avg_long:.4f}/mile premium")

# Final recommendations
print(f"\n6. IMPLICATIONS FOR TIERED SYSTEM:")
print(f"   • Current system appears to have diminishing returns for high mileage")
print(f"   • High mileage (800+) gets ~${avg_non_capped:.2f}/mile vs ${avg_lower:.2f}/mile for lower")
print(f"   • But this is still much better than a fixed low rate")
print(f"   • The system has reimbursement caps that kick in at high receipt amounts")
print(f"   • {len(capped_cases)/len(high_mileage_cases)*100:.0f}% of high-mileage cases hit these caps")

if avg_non_capped > 0.50:  # Assuming a reasonable base rate
    print(f"\n7. CONCLUSION:")
    print(f"   ✓ High mileage DOES get preferential treatment (${avg_non_capped:.4f}/mile)")
    print(f"   ✓ This is better than most simple tiered systems would provide")
    print(f"   ⚠  But much worse than low-mileage trips that get per-day allowances")
    print(f"   ⚠  Reimbursement caps significantly impact high-expense cases")
else:
    print(f"\n7. CONCLUSION:")
    print(f"   ✗ High mileage gets poor treatment (${avg_non_capped:.4f}/mile)")
    print(f"   ⚠  Your tiered system might actually be more generous")

print("="*70)