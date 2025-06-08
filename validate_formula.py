#!/usr/bin/env python3
import json
import random

def load_cases(filename: str) -> list:
    """Load test cases from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def test_best_formula(cases: list) -> None:
    """Test the best formula we found more thoroughly"""
    print("=== TESTING BEST FORMULA: 100*days + 0.58*miles + 0.6*receipts ===")
    
    exact_matches = 0
    close_matches = 0  # Within $1
    very_close_matches = 0  # Within $10
    errors = []
    large_errors = []
    
    for i, case in enumerate(cases):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = days * 100 + miles * 0.58 + receipts * 0.6
        error = abs(predicted - expected)
        errors.append(error)
        
        if error < 0.01:
            exact_matches += 1
        elif error < 1.0:
            close_matches += 1
        elif error < 10.0:
            very_close_matches += 1
        elif error > 100:
            large_errors.append({
                'case_idx': i,
                'input': case['input'],
                'expected': expected,
                'predicted': predicted,
                'error': error
            })
    
    avg_error = sum(errors) / len(errors)
    print(f"\nResults for {len(cases)} cases:")
    print(f"  Exact matches (< $0.01): {exact_matches}")
    print(f"  Close matches (< $1.00): {close_matches}")
    print(f"  Very close matches (< $10.00): {very_close_matches}")
    print(f"  Average error: ${avg_error:.2f}")
    print(f"  Large errors (> $100): {len(large_errors)}")
    
    if large_errors:
        print(f"\nFirst few large errors:")
        for i, err in enumerate(large_errors[:5]):
            inp = err['input']
            print(f"  Case {err['case_idx']}: {inp['trip_duration_days']} days, {inp['miles_traveled']} miles, ${inp['total_receipts_amount']:.2f} receipts")
            print(f"    Expected: ${err['expected']:.2f}, Predicted: ${err['predicted']:.2f}, Error: ${err['error']:.2f}")

def test_variations_of_best_formula(cases: list) -> None:
    """Test small variations around the best formula"""
    print("\n=== TESTING VARIATIONS OF BEST FORMULA ===")
    
    best_error = float('inf')
    best_params = None
    
    for daily_rate in [95, 100, 105]:
        for mileage_rate in [0.56, 0.58, 0.60]:
            for receipt_factor in [0.55, 0.6, 0.65]:
                errors = []
                exact_count = 0
                
                for case in cases:
                    days = case['input']['trip_duration_days']
                    miles = case['input']['miles_traveled']
                    receipts = case['input']['total_receipts_amount']
                    expected = case['expected_output']
                    
                    predicted = days * daily_rate + miles * mileage_rate + receipts * receipt_factor
                    error = abs(predicted - expected)
                    errors.append(error)
                    
                    if error < 0.01:
                        exact_count += 1
                
                avg_error = sum(errors) / len(errors)
                
                if avg_error < best_error:
                    best_error = avg_error
                    best_params = (daily_rate, mileage_rate, receipt_factor)
                
                print(f"{daily_rate}*days + {mileage_rate}*miles + {receipt_factor}*receipts: {exact_count} exact, avg error: ${avg_error:.2f}")
    
    print(f"\nBest variation: {best_params[0]}*days + {best_params[1]}*miles + {best_params[2]}*receipts")
    print(f"Best average error: ${best_error:.2f}")

def analyze_error_patterns(cases: list) -> None:
    """Analyze where the formula fails to see if there are patterns"""
    print("\n=== ANALYZING ERROR PATTERNS ===")
    
    # Group errors by various factors
    high_receipt_errors = []
    low_receipt_errors = []
    long_trip_errors = []
    short_trip_errors = []
    
    for case in cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = days * 100 + miles * 0.58 + receipts * 0.6
        error = abs(predicted - expected)
        
        if receipts > 500:
            high_receipt_errors.append(error)
        else:
            low_receipt_errors.append(error)
        
        if days > 7:
            long_trip_errors.append(error)
        else:
            short_trip_errors.append(error)
    
    print(f"High receipts (>$500): avg error ${sum(high_receipt_errors)/len(high_receipt_errors):.2f}")
    print(f"Low receipts (≤$500): avg error ${sum(low_receipt_errors)/len(low_receipt_errors):.2f}")
    print(f"Long trips (>7 days): avg error ${sum(long_trip_errors)/len(long_trip_errors):.2f}")
    print(f"Short trips (≤7 days): avg error ${sum(short_trip_errors)/len(short_trip_errors):.2f}")

def main():
    # Load cases
    cases = load_cases('public_cases.json')
    print(f"Total cases: {len(cases)}")
    
    # Test on first 100 cases for detailed analysis
    sample_cases = cases[:100]
    print(f"Analyzing first {len(sample_cases)} cases...")
    
    test_best_formula(sample_cases)
    test_variations_of_best_formula(sample_cases)
    analyze_error_patterns(sample_cases)
    
    # Test the best formula on all cases
    print(f"\n=== TESTING ON ALL {len(cases)} CASES ===")
    test_best_formula(cases)

if __name__ == "__main__":
    main()