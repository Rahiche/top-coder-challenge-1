#!/usr/bin/env python3
import json

def analyze_final_algorithm():
    """Final analysis to determine the exact algorithm"""
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
        data = json.load(f)
    
    print("="*80)
    print("FINAL ALGORITHM ANALYSIS")
    print("="*80)
    
    # Based on the analysis, it looks like there might be different formulas for different cases
    # Let me test a segmented approach
    
    target_cases = [995, 683, 151, 710, 547]
    
    print("PATTERN ANALYSIS OF HIGH-ERROR CASES:")
    print()
    
    for case_idx in target_cases:
        case = data[case_idx]
        inp = case['input']
        expected = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        print(f"Case {case_idx}: {days}d, {miles}m, ${receipts:.2f}r → ${expected:.2f}")
        
        # What we found works for each case:
        if case_idx == 995:  # 1 day, 1082 miles, $1809.49 → $446.94
            # Works: $100*days + $0.6*miles - 0.3*max(0, receipts-800) = $446.35
            print("  Best formula: $100*days + $0.6*miles - 0.3*max(0, receipts-800)")
            result = 100*days + 0.6*miles - 0.3*max(0, receipts-800)
            print(f"  Result: ${result:.2f} (error: ${abs(result-expected):.2f})")
            
        elif case_idx == 683:  # 8 days, 795 miles, $1645.99 → $644.69
            # Works: $110*days + $0.57*miles - 0.6*max(0, receipts-500) = $645.56
            print("  Best formula: $110*days + $0.57*miles - 0.6*max(0, receipts-500)")
            result = 110*days + 0.57*miles - 0.6*max(0, receipts-500)
            print(f"  Result: ${result:.2f} (error: ${abs(result-expected):.2f})")
            
        elif case_idx == 151:  # 4 days, 69 miles, $2321.49 → $322.00
            # Works: $130*days + $0.55*miles - 0.3*max(0, receipts-1000) = $161.50 (still error)
            print("  Best formula: $130*days + $0.55*miles - 0.3*max(0, receipts-1000)")
            result = 130*days + 0.55*miles - 0.3*max(0, receipts-1000)
            print(f"  Result: ${result:.2f} (error: ${abs(result-expected):.2f})")
            
        elif case_idx == 710:  # 5 days, 516 miles, $1878.49 → $669.85
            # Works: $130*days + $0.55*miles - 0.3*max(0, receipts-1000) = $670.25
            print("  Best formula: $130*days + $0.55*miles - 0.3*max(0, receipts-1000)")
            result = 130*days + 0.55*miles - 0.3*max(0, receipts-1000)
            print(f"  Result: ${result:.2f} (error: ${abs(result-expected):.2f})")
            
        elif case_idx == 547:  # 8 days, 482 miles, $1411.49 → $631.81
            # Works: $110*days + $0.57*miles - 0.6*max(0, receipts-500) = $607.85
            print("  Best formula: $110*days + $0.57*miles - 0.6*max(0, receipts-500)")
            result = 110*days + 0.57*miles - 0.6*max(0, receipts-500)
            print(f"  Result: ${result:.2f} (error: ${abs(result-expected):.2f})")
        
        print()
    
    print("="*80)
    print("HYPOTHESIS: MULTIPLE FORMULAS BASED ON CONDITIONS")
    print("="*80)
    
    # Test if different formulas apply based on trip characteristics
    
    def test_segmented_formula(days, miles, receipts):
        # Try different formulas based on conditions
        
        # For very high mileage (1000+)
        if miles >= 1000:
            return 100 * days + 0.6 * miles - 0.3 * max(0, receipts - 800)
        
        # For long trips (8+ days) with medium/high mileage
        elif days >= 8 and miles >= 400:
            return 110 * days + 0.57 * miles - 0.6 * max(0, receipts - 500)
        
        # For trips with very high receipts (2000+)
        elif receipts >= 2000:
            return 130 * days + 0.55 * miles - 0.3 * max(0, receipts - 1000)
        
        # For medium-high receipt trips (1500-2000)
        elif receipts >= 1500:
            return 130 * days + 0.55 * miles - 0.3 * max(0, receipts - 1000)
        
        # Default case
        else:
            return 120 * days + 0.58 * miles - 0.2 * max(0, receipts - 600)
    
    print("Testing segmented formula approach:")
    print()
    
    exact_matches = 0
    close_matches = 0
    errors = []
    
    for i, case in enumerate(data):
        inp = case['input']
        expected = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        predicted = test_segmented_formula(days, miles, receipts)
        error = abs(predicted - expected)
        errors.append(error)
        
        if error < 0.01:
            exact_matches += 1
        elif error < 1.0:
            close_matches += 1
    
    avg_error = sum(errors) / len(errors)
    
    print(f"Segmented formula results:")
    print(f"Exact matches: {exact_matches}")
    print(f"Close matches: {close_matches}")
    print(f"Average error: ${avg_error:.2f}")
    print()
    
    # Test on our specific problematic cases
    print("Results on high-error cases:")
    for case_idx in target_cases:
        case = data[case_idx]
        inp = case['input']
        expected = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        predicted = test_segmented_formula(days, miles, receipts)
        error = abs(predicted - expected)
        
        print(f"Case {case_idx}: Expected ${expected:.2f}, Got ${predicted:.2f}, Error: ${error:.2f}")
    
    print("\n" + "="*80)
    print("SIMPLIFIED UNIFIED FORMULA TEST")
    print("="*80)
    
    # Test one unified formula that might work reasonably well
    def unified_formula(days, miles, receipts):
        base = 120 * days + 0.58 * miles
        if receipts > 1000:
            penalty = 0.4 * (receipts - 1000)
            return base - penalty
        else:
            return base
    
    print("Testing unified formula: $120*days + $0.58*miles - 0.4*max(0, receipts-1000)")
    
    exact_matches = 0
    close_matches = 0
    errors = []
    large_errors = []
    
    for i, case in enumerate(data):
        inp = case['input']
        expected = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        predicted = unified_formula(days, miles, receipts)
        error = abs(predicted - expected)
        errors.append(error)
        
        if error < 0.01:
            exact_matches += 1
        elif error < 1.0:
            close_matches += 1
        elif error > 100:
            large_errors.append((i, error))
    
    avg_error = sum(errors) / len(errors)
    
    print(f"Unified formula results:")
    print(f"Exact matches: {exact_matches}")
    print(f"Close matches: {close_matches}")
    print(f"Average error: ${avg_error:.2f}")
    print(f"Large errors (>$100): {len(large_errors)}")
    
    print("\nResults on high-error cases:")
    for case_idx in target_cases:
        case = data[case_idx]
        inp = case['input']
        expected = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        predicted = unified_formula(days, miles, receipts)
        error = abs(predicted - expected)
        
        print(f"Case {case_idx}: Expected ${expected:.2f}, Got ${predicted:.2f}, Error: ${error:.2f}")

if __name__ == "__main__":
    analyze_final_algorithm()