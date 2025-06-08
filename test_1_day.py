#!/usr/bin/env python3
import json
import subprocess

# Read public cases
with open('public_cases.json', 'r') as f:
    public_cases = json.load(f)

one_day_results = []

for i, case in enumerate(public_cases):
    case_num = i + 1
    days = case['input']['trip_duration_days'] 
    
    if days != 1:
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
        
        one_day_results.append({
            'case': case_num,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'calculated': algorithm_result,
            'error': absolute_error
        })

# Sort by error
one_day_results.sort(key=lambda x: x['error'], reverse=True)

print('📊 UPDATED 1-DAY PERFORMANCE')
print('=' * 35)
print(f'Total 1-day cases: {len(one_day_results)}')
avg_error = sum(r['error'] for r in one_day_results) / len(one_day_results)
print(f'Average error: ${avg_error:.2f}')

# Count perfect/close matches
perfect_matches = sum(1 for r in one_day_results if r['error'] <= 0.01)
close_matches = sum(1 for r in one_day_results if r['error'] <= 1.00)

print(f'Perfect matches (≤$0.01): {perfect_matches} ({perfect_matches/len(one_day_results)*100:.1f}%)')
print(f'Close matches (≤$1.00): {close_matches} ({close_matches/len(one_day_results)*100:.1f}%)')

# Show remaining worst cases
print(f'\nRemaining worst 10 1-day cases:')
for i, case in enumerate(one_day_results[:10]):
    print(f'{i+1:2d}. Case {case["case"]:3d}: {case["miles"]:4.0f}mi, ${case["receipts"]:6.0f}r → Expected: ${case["expected"]:7.2f}, Got: ${case["calculated"]:7.2f}, Error: ${case["error"]:6.2f}')