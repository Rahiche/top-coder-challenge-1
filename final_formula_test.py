#!/usr/bin/env python3
import json

def load_cases(filename: str) -> list:
    """Load test cases from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def test_exact_formulas(cases: list) -> None:
    """Test the formulas that worked exactly for multiple cases"""
    
    # Extract formulas from the analysis
    exact_formulas = [
        (70, 0.76, 0.7),   # cases 18, 36
        (80, 0.62, 0.7),   # cases 22, 39  
        (95, 0.42, 0.67),  # cases 22, 35
        (190, 0.92, 0.25), # cases 22, 33
        (50, 0.68, 0.67),  # cases 24, 31
        (65, 0.76, 0.7),   # cases 25, 30
        (85, 0.46, 0.8),   # cases 25, 33
        (65, 0.78, 0.2),   # cases 26, 32
        (60, 0.8, 0.4),    # cases 27, 35
        (75, 0.32, 1.0),   # cases 27, 39
        (70, 0.58, 0.67),  # cases 28, 47
        (190, 0.46, 0.3),  # cases 28, 30
        (50, 0.56, 0.75),  # cases 29, 31
        (115, 0.74, 0.25), # cases 29, 46
        (145, 0.62, 0.4),  # cases 30, 37
        (95, 0.46, 0.5),   # cases 31, 46
        (105, 0.5, 0.4),   # cases 31, 35
        (50, 0.6, 0.9),    # cases 37, 40
        (85, 0.42, 0.75),  # cases 40, 49
        (70, 0.68, 0.33),  # cases 48, 50
    ]
    
    print("=== TESTING EXACT FORMULAS ON ALL CASES ===\n")
    
    best_formula = None
    best_exact_count = 0
    
    for daily, mileage, receipt in exact_formulas:
        exact_count = 0
        close_count = 0
        errors = []
        
        for case in cases:
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            predicted = days * daily + miles * mileage + receipts * receipt
            error = abs(predicted - expected)
            errors.append(error)
            
            if error < 0.01:
                exact_count += 1
            elif error < 1.0:
                close_count += 1
        
        avg_error = sum(errors) / len(errors)
        
        print(f"{daily}*days + {mileage}*miles + {receipt}*receipts:")
        print(f"  Exact matches: {exact_count}")
        print(f"  Close matches (< $1): {close_count}")
        print(f"  Average error: ${avg_error:.2f}")
        
        if exact_count > best_exact_count:
            best_exact_count = exact_count
            best_formula = (daily, mileage, receipt)
        
        print()
    
    if best_formula:
        print(f"=== BEST EXACT FORMULA: {best_formula[0]}*days + {best_formula[1]}*miles + {best_formula[2]}*receipts ===")
        print(f"Exact matches: {best_exact_count}")
        
        # Show the exact matches
        print(f"\nExact matches:")
        count = 0
        for i, case in enumerate(cases):
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            predicted = days * best_formula[0] + miles * best_formula[1] + receipts * best_formula[2]
            
            if abs(predicted - expected) < 0.01:
                print(f"  Case {i+1}: {days} days, {miles} miles, ${receipts:.2f} receipts -> ${expected:.2f}")
                count += 1
                if count >= 10:  # Show first 10
                    break

def comprehensive_formula_search(cases: list, max_test_cases: int = 100) -> None:
    """Do a comprehensive search for the best formula"""
    print(f"\n=== COMPREHENSIVE SEARCH (first {max_test_cases} cases) ===\n")
    
    best_exact = 0
    best_formula = None
    formulas_with_exact_matches = []
    
    # More systematic search
    for daily in range(50, 201, 5):  # 50 to 200 in steps of 5
        for mileage_cents in range(30, 101, 2):  # 0.30 to 1.00 in steps of 0.02
            mileage = mileage_cents / 100.0
            for receipt_factor in [0, 0.1, 0.2, 0.25, 0.3, 0.33, 0.4, 0.5, 0.6, 0.67, 0.7, 0.75, 0.8, 0.9, 1.0]:
                
                exact_count = 0
                test_cases = cases[:max_test_cases]
                
                for case in test_cases:
                    days = case['input']['trip_duration_days']
                    miles = case['input']['miles_traveled']
                    receipts = case['input']['total_receipts_amount']
                    expected = case['expected_output']
                    
                    predicted = days * daily + miles * mileage + receipts * receipt_factor
                    
                    if abs(predicted - expected) < 0.01:
                        exact_count += 1
                
                if exact_count > 0:
                    formulas_with_exact_matches.append((daily, mileage, receipt_factor, exact_count))
                
                if exact_count > best_exact:
                    best_exact = exact_count
                    best_formula = (daily, mileage, receipt_factor)
    
    # Sort by exact matches
    formulas_with_exact_matches.sort(key=lambda x: x[3], reverse=True)
    
    print("Top formulas with exact matches:")
    for i, (daily, mileage, receipt, count) in enumerate(formulas_with_exact_matches[:20]):
        print(f"  {daily}*days + {mileage}*miles + {receipt}*receipts: {count} exact matches")
    
    if best_formula:
        print(f"\n=== BEST FORMULA FROM SEARCH: {best_formula[0]}*days + {best_formula[1]}*miles + {best_formula[2]}*receipts ===")
        print(f"Exact matches in first {max_test_cases} cases: {best_exact}")
        
        # Test on all cases
        exact_all = 0
        close_all = 0
        errors_all = []
        
        for case in cases:
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            predicted = days * best_formula[0] + miles * best_formula[1] + receipts * best_formula[2]
            error = abs(predicted - expected)
            errors_all.append(error)
            
            if error < 0.01:
                exact_all += 1
            elif error < 1.0:
                close_all += 1
        
        avg_error_all = sum(errors_all) / len(errors_all)
        print(f"On all {len(cases)} cases:")
        print(f"  Exact matches: {exact_all}")
        print(f"  Close matches (< $1): {close_all}")
        print(f"  Average error: ${avg_error_all:.2f}")

def main():
    # Load cases
    cases = load_cases('public_cases.json')
    print(f"Total cases: {len(cases)}")
    
    # Test the exact formulas we found
    test_exact_formulas(cases)
    
    # Do comprehensive search
    comprehensive_formula_search(cases, 200)

if __name__ == "__main__":
    main()