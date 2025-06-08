#!/usr/bin/env python3
import json
import random

def load_cases(filename: str) -> list:
    """Load test cases from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def test_simple_formula_with_receipts_cap(cases: list) -> None:
    """Test if there's a simpler pattern based on receipts ranges"""
    print("=== TESTING CAPPED RECEIPTS FORMULAS ===")
    
    for daily_rate in [75, 100]:
        for mileage_rate in [0.5, 0.58]:
            for cap in [20, 25, 30, 50]:
                print(f"\nTesting: {daily_rate}*days + {mileage_rate}*miles + min(receipts, {cap})")
                
                correct = 0
                errors = []
                
                for case in cases:
                    days = case['input']['trip_duration_days']
                    miles = case['input']['miles_traveled']
                    receipts = case['input']['total_receipts_amount']
                    expected = case['expected_output']
                    
                    predicted = days * daily_rate + miles * mileage_rate + min(receipts, cap)
                    error = abs(predicted - expected)
                    errors.append(error)
                    
                    if error < 0.01:
                        correct += 1
                
                avg_error = sum(errors) / len(errors)
                print(f"  Results: {correct}/{len(cases)} exact, avg error: ${avg_error:.2f}")
                
                if avg_error < 100:  # If reasonably close
                    print(f"  This looks promising!")

def analyze_receipt_patterns_detailed(cases: list) -> None:
    """Look for more complex receipt patterns"""
    print("\n=== DETAILED RECEIPT PATTERN ANALYSIS ===")
    
    # Group by receipt amounts to see if there are thresholds
    receipt_groups = {}
    
    for case in cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        output = case['expected_output']
        
        # Calculate what the output would be with just daily and mileage
        base = days * 100 + miles * 0.58
        receipt_contribution = output - base
        
        # Round receipts to nearest 5 for grouping
        receipt_bucket = round(receipts / 5) * 5
        
        if receipt_bucket not in receipt_groups:
            receipt_groups[receipt_bucket] = []
        
        receipt_groups[receipt_bucket].append({
            'receipts': receipts,
            'contribution': receipt_contribution,
            'output': output,
            'base': base,
            'days': days,
            'miles': miles
        })
    
    # Analyze patterns in each group
    for bucket in sorted(receipt_groups.keys()):
        if len(receipt_groups[bucket]) >= 2:  # Only show buckets with multiple cases
            group = receipt_groups[bucket]
            contributions = [item['contribution'] for item in group]
            avg_contribution = sum(contributions) / len(contributions)
            
            print(f"\nReceipts ~${bucket}: {len(group)} cases")
            print(f"  Average contribution: ${avg_contribution:.2f}")
            
            # Show a few examples
            for i, item in enumerate(group[:3]):
                ratio = item['contribution'] / item['receipts'] if item['receipts'] > 0 else 0
                print(f"  Example {i+1}: ${item['receipts']:.2f} -> +${item['contribution']:.2f} (ratio: {ratio:.2f})")

def test_percentage_based_formulas(cases: list) -> None:
    """Test if receipts are reimbursed as a percentage"""
    print("\n=== TESTING PERCENTAGE-BASED RECEIPT REIMBURSEMENT ===")
    
    for daily_rate in [75, 100]:
        for mileage_rate in [0.5, 0.58]:
            for percentage in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                correct = 0
                errors = []
                
                for case in cases:
                    days = case['input']['trip_duration_days']
                    miles = case['input']['miles_traveled']
                    receipts = case['input']['total_receipts_amount']
                    expected = case['expected_output']
                    
                    predicted = days * daily_rate + miles * mileage_rate + receipts * percentage
                    error = abs(predicted - expected)
                    errors.append(error)
                    
                    if error < 0.01:
                        correct += 1
                
                avg_error = sum(errors) / len(errors)
                
                if correct > 0 or avg_error < 200:  # Only show promising results
                    print(f"{daily_rate}*days + {mileage_rate}*miles + {percentage}*receipts: {correct}/{len(cases)} exact, avg error: ${avg_error:.2f}")

def find_exact_matches(cases: list) -> None:
    """Try to find cases that match simple formulas exactly"""
    print("\n=== FINDING EXACT MATCHES ===")
    
    formulas_to_test = [
        (100, 0.58, 0.3),
        (100, 0.58, 0.4),
        (100, 0.58, 0.5),
        (75, 0.58, 0.5),
        (75, 0.58, 0.6),
        (100, 0.5, 0.4),
        (100, 0.5, 0.5),
    ]
    
    for daily, mileage, receipt_factor in formulas_to_test:
        exact_matches = []
        
        for i, case in enumerate(cases):
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            predicted = days * daily + miles * mileage + receipts * receipt_factor
            
            if abs(predicted - expected) < 0.01:
                exact_matches.append(i)
        
        if exact_matches:
            print(f"{daily}*days + {mileage}*miles + {receipt_factor}*receipts: {len(exact_matches)} exact matches")
            for match_idx in exact_matches[:3]:  # Show first 3 matches
                case = cases[match_idx]
                print(f"  Case {match_idx}: {case['input']} -> {case['expected_output']}")

def main():
    # Load cases
    cases = load_cases('public_cases.json')
    print(f"Total cases: {len(cases)}")
    
    # Use first 30 cases for faster analysis
    sample_cases = cases[:30]
    print(f"Analyzing first {len(sample_cases)} cases...")
    
    # Try different approaches
    test_simple_formula_with_receipts_cap(sample_cases)
    test_percentage_based_formulas(sample_cases)
    analyze_receipt_patterns_detailed(sample_cases)
    find_exact_matches(sample_cases)

if __name__ == "__main__":
    main()