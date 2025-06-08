#!/usr/bin/env python3
import json
import subprocess

# Read public cases
with open('public_cases.json', 'r') as f:
    public_cases = json.load(f)

five_day_results = []

for i, case in enumerate(public_cases):
    case_num = i + 1
    days = case['input']['trip_duration_days'] 
    
    if days != 5:
        continue
        
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    # Run algorithm
    result = subprocess.run(['./run.sh', str(days), str(miles), str(receipts)], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        algorithm_result = float(result.stdout.strip())
        absolute_error = abs(algorithm_result - expected)
        
        five_day_results.append({
            'case': case_num,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'calculated': algorithm_result,
            'error': absolute_error
        })

# Sort by error
five_day_results.sort(key=lambda x: x['error'], reverse=True)

print('📊 CURRENT 5-DAY PERFORMANCE')
print('=' * 35)
print(f'Total 5-day cases: {len(five_day_results)}')
avg_error = sum(r['error'] for r in five_day_results) / len(five_day_results)
print(f'Average error: ${avg_error:.2f}')

print(f'\nWorst 8 5-day cases:')
for i, case in enumerate(five_day_results[:8]):
    print(f'{i+1:2d}. Case {case["case"]:3d}: {case["miles"]:4.0f}mi, ${case["receipts"]:6.0f}r → Expected: ${case["expected"]:7.2f}, Got: ${case["calculated"]:7.2f}, Error: ${case["error"]:6.2f}')

print(f'\nBest 8 5-day cases:')
best_cases = sorted(five_day_results, key=lambda x: x['error'])[:8]
for i, case in enumerate(best_cases):
    print(f'{i+1:2d}. Case {case["case"]:3d}: {case["miles"]:4.0f}mi, ${case["receipts"]:6.0f}r → Expected: ${case["expected"]:7.2f}, Got: ${case["calculated"]:7.2f}, Error: ${case["error"]:6.2f}')