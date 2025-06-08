#!/usr/bin/env python3
"""
Analyze CSV data by duration without pandas dependency.
"""

import csv
from collections import defaultdict

def analyze_durations():
    """Get overview of all durations and their performance."""
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # Group by duration
    by_duration = defaultdict(list)
    for row in data:
        duration = int(row['trip_duration_days'])
        by_duration[duration].append({
            'case': int(row['case_number']),
            'miles': float(row['miles_traveled']),
            'receipts': float(row['total_receipts_amount']),
            'expected': float(row['expected_output']),
            'calculated': float(row['algorithm_result']),
            'error': float(row['absolute_error'])
        })
    
    print("📊 TRIP DURATION ANALYSIS")
    print("=" * 40)
    
    durations = sorted(by_duration.keys())
    for duration in durations:
        cases = by_duration[duration]
        avg_error = sum(case['error'] for case in cases) / len(cases)
        min_error = min(case['error'] for case in cases)
        max_error = max(case['error'] for case in cases)
        
        print(f"{duration} days: {len(cases)} cases, "
              f"avg error: ${avg_error:.2f}, "
              f"range: ${min_error:.2f}-${max_error:.2f}")
    
    return by_duration, durations

def analyze_single_duration(duration, cases):
    """Detailed analysis of a single duration."""
    
    print(f"\n🔍 DETAILED ANALYSIS: {duration}-DAY TRIPS")
    print("=" * 50)
    
    # Sort by error (best to worst)
    cases_sorted = sorted(cases, key=lambda x: x['error'])
    
    total_cases = len(cases)
    avg_error = sum(case['error'] for case in cases) / total_cases
    median_error = cases_sorted[total_cases // 2]['error']
    
    print(f"Total cases: {total_cases}")
    print(f"Average error: ${avg_error:.2f}")
    print(f"Median error: ${median_error:.2f}")
    
    # Show best cases
    print(f"\n🎯 BEST CASES (5 lowest errors):")
    for i, case in enumerate(cases_sorted[:5]):
        print(f"   {i+1}. Case {case['case']}: {case['miles']:.0f}mi, ${case['receipts']:.0f}r")
        print(f"      Expected: ${case['expected']:.2f}, Got: ${case['calculated']:.2f}, Error: ${case['error']:.2f}")
    
    # Show worst cases
    print(f"\n❌ WORST CASES (5 highest errors):")
    for i, case in enumerate(cases_sorted[-5:]):
        print(f"   {i+1}. Case {case['case']}: {case['miles']:.0f}mi, ${case['receipts']:.0f}r")
        print(f"      Expected: ${case['expected']:.2f}, Got: ${case['calculated']:.2f}, Error: ${case['error']:.2f}")
    
    # Pattern analysis
    over_calc = sum(1 for case in cases if case['calculated'] > case['expected'])
    under_calc = total_cases - over_calc
    
    print(f"\n📈 CALCULATION BIAS:")
    print(f"   Over-calculated: {over_calc}/{total_cases} ({over_calc/total_cases*100:.1f}%)")
    print(f"   Under-calculated: {under_calc}/{total_cases} ({under_calc/total_cases*100:.1f}%)")
    
    # Look for patterns in best vs worst
    best_quartile = cases_sorted[:total_cases//4]
    worst_quartile = cases_sorted[-total_cases//4:]
    
    best_avg_miles = sum(case['miles'] for case in best_quartile) / len(best_quartile)
    best_avg_receipts = sum(case['receipts'] for case in best_quartile) / len(best_quartile)
    worst_avg_miles = sum(case['miles'] for case in worst_quartile) / len(worst_quartile)
    worst_avg_receipts = sum(case['receipts'] for case in worst_quartile) / len(worst_quartile)
    
    print(f"\n🔍 PATTERN ANALYSIS:")
    print(f"   Best quartile avg: {best_avg_miles:.0f} miles, ${best_avg_receipts:.0f} receipts")
    print(f"   Worst quartile avg: {worst_avg_miles:.0f} miles, ${worst_avg_receipts:.0f} receipts")
    
    if worst_avg_receipts > best_avg_receipts * 1.5:
        print("   ⚠️  HIGH RECEIPTS correlated with high errors")
    
    if worst_avg_miles > best_avg_miles * 1.5:
        print("   ⚠️  HIGH MILEAGE correlated with high errors")
    
    return cases_sorted

def reverse_engineer_formula(duration, cases_sorted):
    """Try to reverse engineer the correct formula from best cases."""
    
    print(f"\n🔬 REVERSE ENGINEERING {duration}-DAY FORMULA:")
    print("=" * 45)
    
    # Use the 5 best cases to try to understand the pattern
    best_cases = cases_sorted[:5]
    
    print("Analyzing best cases for formula patterns...")
    
    for i, case in enumerate(best_cases):
        days = duration
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        calculated = case['calculated']
        
        print(f"\nCase {i+1}: {miles:.0f}mi, ${receipts:.0f}r → ${expected:.2f}")
        
        # Try to work backwards from expected output
        if days == 1:
            # Test different base amounts
            for base in [70, 75, 80, 85, 90]:
                for mile_rate in [0.55, 0.60, 0.65]:
                    remainder = expected - base - (miles * mile_rate)
                    if receipts > 0:
                        receipt_factor = remainder / receipts
                        if 0.3 <= receipt_factor <= 0.7:
                            print(f"      Possible: ${base} + {miles:.0f}×${mile_rate:.2f} + ${receipts:.0f}×{receipt_factor:.3f} = ${expected:.2f}")
        
        elif days == 2:
            # Test different base amounts for 2-day trips
            for base in [160, 170, 180]:
                for mile_rate in [0.65, 0.69, 0.75]:
                    remainder = expected - base - (miles * mile_rate)
                    if receipts > 0:
                        receipt_factor = remainder / receipts
                        if 0.3 <= receipt_factor <= 1.2:
                            print(f"      Possible: ${base} + {miles:.0f}×${mile_rate:.2f} + ${receipts:.0f}×{receipt_factor:.3f} = ${expected:.2f}")

def suggest_improvements(duration, cases_sorted):
    """Suggest specific improvements for this duration."""
    
    print(f"\n💡 IMPROVEMENT SUGGESTIONS FOR {duration}-DAY TRIPS:")
    print("=" * 55)
    
    # Analyze the patterns and suggest specific changes
    worst_cases = cases_sorted[-10:]  # Look at 10 worst cases
    
    high_receipt_errors = [case for case in worst_cases if case['receipts'] > 1000]
    high_mile_errors = [case for case in worst_cases if case['miles'] > 500]
    
    if len(high_receipt_errors) > 5:
        avg_receipt_error = sum(case['error'] for case in high_receipt_errors) / len(high_receipt_errors)
        print(f"1. HIGH RECEIPT PENALTY NEEDED:")
        print(f"   {len(high_receipt_errors)} high-receipt cases (>$1000) have avg error ${avg_receipt_error:.2f}")
        print(f"   Suggest: Lower receipt cap or add penalty for receipts > $1000")
    
    if len(high_mile_errors) > 5:
        avg_mile_error = sum(case['error'] for case in high_mile_errors) / len(high_mile_errors)
        print(f"2. HIGH MILEAGE ADJUSTMENT NEEDED:")
        print(f"   {len(high_mile_errors)} high-mileage cases (>500mi) have avg error ${avg_mile_error:.2f}")
        print(f"   Suggest: Lower mileage rate for high distances")
    
    # Check calculation bias
    over_calc = sum(1 for case in cases_sorted if case['calculated'] > case['expected'])
    if over_calc > len(cases_sorted) * 0.6:
        print(f"3. OVER-CALCULATION BIAS:")
        print(f"   {over_calc}/{len(cases_sorted)} cases over-calculated")
        print(f"   Suggest: Reduce base rate or receipt factors")
    elif over_calc < len(cases_sorted) * 0.4:
        print(f"3. UNDER-CALCULATION BIAS:")
        print(f"   {len(cases_sorted) - over_calc}/{len(cases_sorted)} cases under-calculated")
        print(f"   Suggest: Increase base rate or receipt factors")

if __name__ == "__main__":
    # Get overview
    by_duration, durations = analyze_durations()
    
    print(f"\n{'='*60}")
    print("SYSTEMATIC ANALYSIS BY DURATION")
    print("We'll analyze each duration separately, starting with the best performers")
    print(f"{'='*60}")
    
    # Sort durations by average error to start with best performing
    duration_errors = []
    for duration in durations:
        cases = by_duration[duration]
        avg_error = sum(case['error'] for case in cases) / len(cases)
        duration_errors.append((avg_error, duration))
    
    duration_errors.sort()  # Start with lowest average error
    
    for avg_error, duration in duration_errors:
        cases = by_duration[duration]
        
        # Detailed analysis
        cases_sorted = analyze_single_duration(duration, cases)
        
        # Try to reverse engineer
        reverse_engineer_formula(duration, cases_sorted)
        
        # Suggest improvements
        suggest_improvements(duration, cases_sorted)
        
        print(f"\n{'='*60}")
        response = input(f"Analysis complete for {duration}-day trips (avg error: ${avg_error:.2f}). Continue to next duration? (y/n): ")
        if response.lower() != 'y':
            break
    
    print("\nAnalysis complete!")