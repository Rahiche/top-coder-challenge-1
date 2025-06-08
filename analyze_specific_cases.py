#!/usr/bin/env python3

import json

def analyze_case_patterns():
    """Analyze specific patterns in public cases to refine the algorithm"""
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("Analyzing specific case patterns...")
    
    # Group cases by characteristics
    day_groups = {}
    mile_groups = {}
    receipt_groups = {}
    
    for case in cases:
        input_data = case['input']
        days = input_data['trip_duration_days']
        miles = input_data['miles_traveled']
        receipts = input_data['total_receipts_amount']
        expected = case['expected_output']
        
        # Group by days
        if days not in day_groups:
            day_groups[days] = []
        day_groups[days].append((miles, receipts, expected))
        
        # Group by mile ranges
        mile_range = (miles // 50) * 50
        if mile_range not in mile_groups:
            mile_groups[mile_range] = []
        mile_groups[mile_range].append((days, receipts, expected))
        
        # Group by receipt ranges  
        receipt_range = (int(receipts) // 10) * 10
        if receipt_range not in receipt_groups:
            receipt_groups[receipt_range] = []
        receipt_groups[receipt_range].append((days, miles, expected))
    
    # Analyze 1-day trips
    print("\n=== 1-DAY TRIP ANALYSIS ===")
    if 1 in day_groups:
        one_day = day_groups[1]
        print(f"Total 1-day trips: {len(one_day)}")
        
        # Sort by miles
        one_day.sort(key=lambda x: x[0])
        print("Sample 1-day trips (miles, receipts, expected):")
        for i in range(min(10, len(one_day))):
            miles, receipts, expected = one_day[i]
            # Simple calculation: base + mileage
            estimated_base = 100  # Base per diem
            estimated_mileage = miles * 0.58
            simple_total = estimated_base + estimated_mileage + receipts * 0.5
            print(f"  {miles:3d} miles, ${receipts:6.2f} receipts -> ${expected:7.2f} (simple est: ${simple_total:.2f})")
    
    # Analyze patterns by specific days
    print("\n=== DAILY PATTERNS ===")
    for days in sorted(day_groups.keys())[:10]:
        data = day_groups[days]
        if len(data) >= 5:
            avg_output = sum(x[2] for x in data) / len(data)
            avg_miles = sum(x[0] for x in data) / len(data)
            avg_receipts = sum(x[1] for x in data) / len(data)
            print(f"{days:2d} days: {len(data):3d} cases, avg output ${avg_output:6.2f}, avg miles {avg_miles:5.1f}, avg receipts ${avg_receipts:5.2f}")
    
    # Look for specific patterns
    print("\n=== SPECIFIC PATTERN ANALYSIS ===")
    
    # Find cases with similar inputs but different outputs
    similar_cases = []
    for i, case1 in enumerate(cases):
        for j, case2 in enumerate(cases[i+1:], i+1):
            input1 = case1['input']
            input2 = case2['input']
            
            # Check if inputs are very similar
            day_diff = abs(input1['trip_duration_days'] - input2['trip_duration_days'])
            mile_diff = abs(input1['miles_traveled'] - input2['miles_traveled'])
            receipt_diff = abs(input1['total_receipts_amount'] - input2['total_receipts_amount'])
            
            if day_diff <= 1 and mile_diff <= 10 and receipt_diff <= 5:
                output_diff = abs(case1['expected_output'] - case2['expected_output'])
                if output_diff > 20:  # Significant difference in output
                    similar_cases.append((input1, case1['expected_output'], input2, case2['expected_output'], output_diff))
    
    print(f"Found {len(similar_cases)} pairs of similar inputs with significant output differences:")
    for i, (inp1, out1, inp2, out2, diff) in enumerate(similar_cases[:5]):
        print(f"  Pair {i+1}:")
        print(f"    Case A: {inp1['trip_duration_days']} days, {inp1['miles_traveled']} miles, ${inp1['total_receipts_amount']:.2f} -> ${out1:.2f}")
        print(f"    Case B: {inp2['trip_duration_days']} days, {inp2['miles_traveled']} miles, ${inp2['total_receipts_amount']:.2f} -> ${out2:.2f}")
        print(f"    Difference: ${diff:.2f}")
    
    # Analyze receipt ending patterns (rounding bug)
    print("\n=== RECEIPT ENDING ANALYSIS ===")
    ending_patterns = {}
    for case in cases:
        receipts = case['input']['total_receipts_amount']
        ending = int((receipts * 100) % 100)
        
        if ending not in ending_patterns:
            ending_patterns[ending] = []
        ending_patterns[ending].append(case['expected_output'])
    
    # Look for patterns in specific endings
    for ending in [49, 99, 0, 50]:
        if ending in ending_patterns and len(ending_patterns[ending]) > 3:
            values = ending_patterns[ending]
            avg_value = sum(values) / len(values)
            print(f"  Receipts ending in .{ending:02d}: {len(values)} cases, avg output ${avg_value:.2f}")

if __name__ == "__main__":
    analyze_case_patterns()