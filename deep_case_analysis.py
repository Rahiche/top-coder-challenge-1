#!/usr/bin/env python3
import json

def load_cases(filename: str) -> list:
    """Load test cases from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_case_in_extreme_detail(case_idx: int, case: dict) -> None:
    """Analyze a single case in extreme detail"""
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    
    print(f"=== CASE {case_idx + 1} DEEP ANALYSIS ===")
    print(f"Input: {days} days, {miles} miles, ${receipts:.2f} receipts")
    print(f"Output: ${output:.2f}")
    print()
    
    # Try to work backwards to find the exact formula
    print("Working backwards:")
    
    # If it's days * X + miles * Y + receipts * Z, what would X, Y, Z need to be?
    # We need to solve: days * X + miles * Y + receipts * Z = output
    
    # Try different combinations
    for daily_rate in range(50, 201, 5):  # Try daily rates from 50 to 200
        remaining_after_daily = output - (days * daily_rate)
        print(f"  If daily rate = ${daily_rate}: remaining = ${remaining_after_daily:.2f}")
        
        if remaining_after_daily > 0:
            # What mileage + receipt rates would work?
            for mileage_rate_cents in range(30, 100, 5):  # 0.30 to 0.95
                mileage_rate = mileage_rate_cents / 100.0
                remaining_after_mileage = remaining_after_daily - (miles * mileage_rate)
                
                if receipts > 0:
                    needed_receipt_factor = remaining_after_mileage / receipts
                    if 0 <= needed_receipt_factor <= 2:  # Only show reasonable factors
                        print(f"    ${daily_rate} + {mileage_rate}*{miles} + {needed_receipt_factor:.3f}*${receipts:.2f} = ${output:.2f}")
    
    print()

def find_common_exact_formulas(cases: list, num_cases: int = 10) -> None:
    """Find formulas that work exactly for multiple cases"""
    print(f"=== FINDING FORMULAS THAT WORK EXACTLY FOR MULTIPLE CASES ===\n")
    
    # Dictionary to store formula -> list of case indices where it works
    formula_matches = {}
    
    for case_idx in range(num_cases):
        case = cases[case_idx]
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        output = case['expected_output']
        
        # Try systematic combinations
        for daily_rate in range(50, 201, 5):
            for mileage_rate_cents in range(30, 100, 2):
                mileage_rate = mileage_rate_cents / 100.0
                
                remaining = output - (days * daily_rate + miles * mileage_rate)
                
                if receipts > 0:
                    receipt_factor = remaining / receipts
                    
                    # Check if this is a "nice" factor
                    nice_factors = [0, 0.1, 0.2, 0.25, 0.3, 0.33, 0.4, 0.5, 0.6, 0.67, 0.7, 0.75, 0.8, 0.9, 1.0]
                    for nice_factor in nice_factors:
                        if abs(receipt_factor - nice_factor) < 0.001:
                            formula = f"{daily_rate}*days + {mileage_rate}*miles + {nice_factor}*receipts"
                            if formula not in formula_matches:
                                formula_matches[formula] = []
                            formula_matches[formula].append(case_idx + 1)
                            break
                else:
                    # No receipts case
                    if abs(remaining) < 0.01:
                        formula = f"{daily_rate}*days + {mileage_rate}*miles"
                        if formula not in formula_matches:
                            formula_matches[formula] = []
                        formula_matches[formula].append(case_idx + 1)
    
    # Show formulas that work for multiple cases
    for formula, case_list in formula_matches.items():
        if len(case_list) >= 2:
            print(f"{formula}: works exactly for cases {case_list}")

def check_if_receipt_handling_is_conditional(cases: list, num_cases: int = 20) -> None:
    """Check if receipt handling has conditional logic"""
    print(f"\n=== CHECKING FOR CONDITIONAL RECEIPT LOGIC ===\n")
    
    for case_idx in range(num_cases):
        case = cases[case_idx]
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        output = case['expected_output']
        
        # Test if it matches: base + min(receipts, cap) or base + receipts * factor_based_on_amount
        base = days * 100 + miles * 0.58  # Standard base
        receipt_contribution = output - base
        
        # Test various conditional rules
        rules_tested = []
        
        # Rule 1: Receipt cap
        for cap in [20, 25, 30, 50]:
            predicted = base + min(receipts, cap)
            if abs(predicted - output) < 0.01:
                rules_tested.append(f"base + min(receipts, {cap})")
        
        # Rule 2: Receipt factor based on amount
        if receipts <= 20:
            predicted = base + receipts * 0
        elif receipts <= 100:
            predicted = base + receipts * 0.5
        else:
            predicted = base + receipts * 0.3
        
        if abs(predicted - output) < 0.01:
            rules_tested.append("conditional receipt factor (0/0.5/0.3)")
        
        # Rule 3: Different bases
        for base_daily in [75, 90, 100, 110]:
            for base_mileage in [0.5, 0.58, 0.65]:
                alt_base = days * base_daily + miles * base_mileage
                if receipts > 0:
                    needed_factor = (output - alt_base) / receipts
                    if abs(needed_factor - 0.5) < 0.01:
                        rules_tested.append(f"{base_daily}*days + {base_mileage}*miles + 0.5*receipts")
                    elif abs(needed_factor - 0.6) < 0.01:
                        rules_tested.append(f"{base_daily}*days + {base_mileage}*miles + 0.6*receipts")
        
        if rules_tested:
            print(f"Case {case_idx + 1}: {days} days, {miles} miles, ${receipts:.2f} receipts -> ${output:.2f}")
            for rule in rules_tested:
                print(f"  Matches: {rule}")
            print()

def main():
    # Load cases
    cases = load_cases('public_cases.json')
    
    # Analyze first few cases in extreme detail
    for i in range(3):
        analyze_case_in_extreme_detail(i, cases[i])
    
    # Find common exact formulas
    find_common_exact_formulas(cases, 50)
    
    # Check for conditional logic
    check_if_receipt_handling_is_conditional(cases, 20)

if __name__ == "__main__":
    main()