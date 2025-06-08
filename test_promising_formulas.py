#!/usr/bin/env python3
import json

def load_cases(filename: str) -> list:
    """Load test cases from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def test_formula(cases: list, daily_rate: int, mileage_rate: float, receipt_factor: float, max_cases: int = 100) -> tuple:
    """Test a specific formula and return accuracy metrics"""
    exact_matches = 0
    close_matches = 0  # within $1
    very_close_matches = 0  # within $10
    errors = []
    
    test_cases = cases[:max_cases]
    
    for case in test_cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = days * daily_rate + miles * mileage_rate + receipts * receipt_factor
        error = abs(predicted - expected)
        errors.append(error)
        
        if error < 0.01:
            exact_matches += 1
        elif error < 1.0:
            close_matches += 1
        elif error < 10.0:
            very_close_matches += 1
    
    avg_error = sum(errors) / len(errors) if errors else float('inf')
    return exact_matches, close_matches, very_close_matches, avg_error

def main():
    # Load cases
    cases = load_cases('public_cases.json')
    
    # Test the most promising formulas from the pattern discovery
    promising_formulas = [
        # Format: (daily_rate, mileage_rate, receipt_factor, description)
        (85, 0.68, 0.67, "85*days + 0.68*miles + 0.67*receipts - worked for 5 cases"),
        (90, 0.6, 0.6, "90*days + 0.6*miles + 0.6*receipts - worked for 3 cases"),
        (100, 0.66, 0.6, "100*days + 0.66*miles + 0.6*receipts - worked for 4 cases"),
        (100, 0.68, 0.6, "100*days + 0.68*miles + 0.6*receipts - worked for 4 cases"),
        (105, 0.64, 0.6, "105*days + 0.64*miles + 0.6*receipts - worked for 4 cases"),
        (110, 0.6, 0.6, "110*days + 0.6*miles + 0.6*receipts - worked for 4 cases"),
        (95, 0.76, 0.6, "95*days + 0.76*miles + 0.6*receipts - worked for 4 cases"),
        (130, 0.78, 0.4, "130*days + 0.78*miles + 0.4*receipts - worked for 4 cases"),
        (135, 0.44, 0.6, "135*days + 0.44*miles + 0.6*receipts - worked for 3 cases"),
    ]
    
    print("=== TESTING PROMISING FORMULAS ON FIRST 100 CASES ===\n")
    
    best_formula = None
    best_score = 0
    best_error = float('inf')
    
    for daily, mileage, receipt, description in promising_formulas:
        exact, close, very_close, avg_error = test_formula(cases, daily, mileage, receipt, 100)
        
        # Calculate a composite score (prioritizing exact matches)
        score = exact * 1000 + close * 100 + very_close * 10 - avg_error
        
        print(f"{daily}*days + {mileage}*miles + {receipt}*receipts:")
        print(f"  Exact matches: {exact}")
        print(f"  Close matches (< $1): {close}")
        print(f"  Very close (< $10): {very_close}")
        print(f"  Average error: ${avg_error:.2f}")
        print(f"  Score: {score:.2f}")
        print()
        
        if score > best_score or (score == best_score and avg_error < best_error):
            best_score = score
            best_error = avg_error
            best_formula = (daily, mileage, receipt)
    
    if best_formula:
        print(f"=== BEST FORMULA: {best_formula[0]}*days + {best_formula[1]}*miles + {best_formula[2]}*receipts ===")
        
        # Test on all cases
        print(f"\nTesting on all {len(cases)} cases:")
        exact, close, very_close, avg_error = test_formula(cases, best_formula[0], best_formula[1], best_formula[2], len(cases))
        print(f"  Exact matches: {exact}")
        print(f"  Close matches (< $1): {close}")
        print(f"  Very close (< $10): {very_close}")
        print(f"  Average error: ${avg_error:.2f}")
        
        # Show some exact matches if any
        if exact > 0:
            print(f"\nFirst few exact matches:")
            count = 0
            for i, case in enumerate(cases):
                if count >= 5:
                    break
                    
                days = case['input']['trip_duration_days']
                miles = case['input']['miles_traveled']
                receipts = case['input']['total_receipts_amount']
                expected = case['expected_output']
                
                predicted = days * best_formula[0] + miles * best_formula[1] + receipts * best_formula[2]
                
                if abs(predicted - expected) < 0.01:
                    print(f"  Case {i+1}: {days} days, {miles} miles, ${receipts:.2f} receipts -> ${expected:.2f}")
                    count += 1

if __name__ == "__main__":
    main()