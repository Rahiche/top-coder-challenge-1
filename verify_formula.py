#!/usr/bin/env python3
import json

def test_specific_formula():
    """Test a specific formula that seems to work for high-error cases"""
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
        data = json.load(f)
    
    print("="*80)
    print("TESTING SPECIFIC FORMULA ON ALL CASES")
    print("="*80)
    
    # Based on the analysis, try this formula:
    # Base: $120 * days + $0.58 * miles
    # If receipts > $800: subtract 0.3 * (receipts - 800)
    
    def calculate_reimbursement(days, miles, receipts):
        base = 120 * days + 0.58 * miles
        if receipts > 800:
            penalty = 0.3 * (receipts - 800)
            return base - penalty
        else:
            return base
    
    print("Formula: $120*days + $0.58*miles - 0.3*max(0, receipts-800)")
    print()
    
    exact_matches = 0
    close_matches = 0
    total_error = 0
    large_errors = []
    
    for i, case in enumerate(data):
        inp = case['input']
        expected = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        predicted = calculate_reimbursement(days, miles, receipts)
        error = abs(predicted - expected)
        total_error += error
        
        if error < 0.01:
            exact_matches += 1
        elif error < 1.0:
            close_matches += 1
        elif error > 50:  # Large errors
            large_errors.append((i, days, miles, receipts, expected, predicted, error))
    
    avg_error = total_error / len(data)
    
    print(f"Results on {len(data)} cases:")
    print(f"Exact matches (< $0.01): {exact_matches}")
    print(f"Close matches (< $1.00): {close_matches}")
    print(f"Average error: ${avg_error:.2f}")
    print(f"Large errors (> $50): {len(large_errors)}")
    print()
    
    if large_errors:
        print("Cases with large errors:")
        for i, (case_idx, days, miles, receipts, expected, predicted, error) in enumerate(large_errors[:10]):
            print(f"  Case {case_idx}: {days}d, {miles}m, ${receipts:.2f}r → Expected: ${expected:.2f}, Got: ${predicted:.2f}, Error: ${error:.2f}")
    
    print("\n" + "="*80)
    print("TESTING ALTERNATIVE FORMULAS")
    print("="*80)
    
    # Test other promising formulas
    formulas = [
        ("$110*days + $0.57*miles - 0.6*max(0, receipts-500)", lambda d,m,r: 110*d + 0.57*m - (0.6*max(0, r-500))),
        ("$100*days + $0.6*miles - 0.3*max(0, receipts-800)", lambda d,m,r: 100*d + 0.6*m - (0.3*max(0, r-800))),
        ("$130*days + $0.55*miles - 0.3*max(0, receipts-1000)", lambda d,m,r: 130*d + 0.55*m - (0.3*max(0, r-1000))),
        ("min($120*days + $0.58*miles, 0.4*receipts)", lambda d,m,r: min(120*d + 0.58*m, 0.4*r)),
        ("min($120*days + $0.58*miles, 0.3*receipts)", lambda d,m,r: min(120*d + 0.58*m, 0.3*r)),
    ]
    
    for formula_desc, formula_func in formulas:
        exact_matches = 0
        close_matches = 0
        total_error = 0
        
        for case in data:
            inp = case['input']
            expected = case['expected_output']
            
            days = inp['trip_duration_days']
            miles = inp['miles_traveled']
            receipts = inp['total_receipts_amount']
            
            try:
                predicted = formula_func(days, miles, receipts)
                error = abs(predicted - expected)
                total_error += error
                
                if error < 0.01:
                    exact_matches += 1
                elif error < 1.0:
                    close_matches += 1
            except:
                continue
        
        avg_error = total_error / len(data)
        print(f"{formula_desc}:")
        print(f"  Exact: {exact_matches}, Close: {close_matches}, Avg Error: ${avg_error:.2f}")
        print()
    
    print("="*80)
    print("ANALYZING SPECIFIC HIGH-ERROR CASES")
    print("="*80)
    
    # Test the specific cases mentioned in the original request
    target_cases = [995, 683, 151, 710, 547]
    
    for case_idx in target_cases:
        case = data[case_idx]
        inp = case['input']
        expected = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        
        print(f"Case {case_idx}: {days} days, {miles} miles, ${receipts:.2f} receipts")
        print(f"  Expected: ${expected:.2f}")
        
        for formula_desc, formula_func in formulas:
            try:
                predicted = formula_func(days, miles, receipts)
                error = abs(predicted - expected)
                print(f"  {formula_desc}: ${predicted:.2f} (error: ${error:.2f})")
            except:
                print(f"  {formula_desc}: ERROR")
        print()

if __name__ == "__main__":
    test_specific_formula()