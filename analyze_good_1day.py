#!/usr/bin/env python3
import json
import subprocess

# Read public cases and find 1-day cases with low errors
with open('public_cases.json', 'r') as f:
    public_cases = json.load(f)

good_cases = []

for i, case in enumerate(public_cases):
    case_num = i + 1
    if case['input']['trip_duration_days'] != 1:
        continue
        
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    result = subprocess.run(['./run.sh', '1', str(miles), str(receipts)], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        calculated = float(result.stdout.strip())
        error = abs(calculated - expected)
        
        if error <= 50:  # Good cases
            good_cases.append({
                'case': case_num,
                'miles': miles,
                'receipts': receipts,
                'expected': expected,
                'calculated': calculated,
                'error': error
            })

print('🎯 BEST 1-DAY CASES (error ≤ $50):')
print('=' * 40)
good_cases.sort(key=lambda x: x['error'])

for case in good_cases[:10]:
    print(f'Case {case["case"]:3d}: {case["miles"]:4.0f}mi, ${case["receipts"]:6.0f}r → Expected: ${case["expected"]:7.2f}, Got: ${case["calculated"]:7.2f}, Error: ${case["error"]:5.2f}')

if good_cases:
    print(f'\nTotal good cases: {len(good_cases)}/92 ({len(good_cases)/92*100:.1f}%)')
    
    # Analyze patterns in good cases
    avg_miles = sum(c['miles'] for c in good_cases) / len(good_cases)
    avg_receipts = sum(c['receipts'] for c in good_cases) / len(good_cases)
    avg_expected = sum(c['expected'] for c in good_cases) / len(good_cases)
    
    print(f'\nPatterns in good cases:')
    print(f'Average miles: {avg_miles:.0f}')
    print(f'Average receipts: ${avg_receipts:.0f}')
    print(f'Average expected: ${avg_expected:.2f}')
else:
    print('No cases with error ≤ $50 found!')