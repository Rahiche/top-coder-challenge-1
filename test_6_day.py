#!/usr/bin/env python3
import json
import subprocess

def test_duration(days):
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)

    results = []
    for i, case in enumerate(public_cases):
        case_num = i + 1
        if case['input']['trip_duration_days'] != days:
            continue
            
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        result = subprocess.run(['./run.sh', str(days), str(miles), str(receipts)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            algorithm_result = float(result.stdout.strip())
            absolute_error = abs(algorithm_result - expected)
            
            results.append({
                'case': case_num,
                'miles': miles,
                'receipts': receipts,
                'expected': expected,
                'calculated': algorithm_result,
                'error': absolute_error
            })

    results.sort(key=lambda x: x['error'], reverse=True)
    
    print(f'📊 CURRENT {days}-DAY PERFORMANCE')
    print('=' * 35)
    print(f'Total {days}-day cases: {len(results)}')
    if results:
        avg_error = sum(r['error'] for r in results) / len(results)
        print(f'Average error: ${avg_error:.2f}')
        
        print(f'\nWorst 6 {days}-day cases:')
        for i, case in enumerate(results[:6]):
            print(f'{i+1:2d}. Case {case["case"]:3d}: {case["miles"]:4.0f}mi, ${case["receipts"]:6.0f}r → Expected: ${case["expected"]:7.2f}, Got: ${case["calculated"]:7.2f}, Error: ${case["error"]:6.2f}')

        print(f'\nBest 6 {days}-day cases:')
        best_cases = sorted(results, key=lambda x: x['error'])[:6]
        for i, case in enumerate(best_cases):
            print(f'{i+1:2d}. Case {case["case"]:3d}: {case["miles"]:4.0f}mi, ${case["receipts"]:6.0f}r → Expected: ${case["expected"]:7.2f}, Got: ${case["calculated"]:7.2f}, Error: ${case["error"]:6.2f}')
    else:
        print(f'No {days}-day cases found!')

# Test 6, 7, 8 day trips
for days in [6, 7, 8]:
    test_duration(days)
    print()