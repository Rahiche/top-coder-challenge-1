#!/usr/bin/env python3
import json

def load_cases(filename: str) -> list:
    """Load test cases from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_first_cases_in_detail(cases: list, num_cases: int = 20) -> None:
    """Analyze the first few cases in great detail to find patterns"""
    print(f"=== DETAILED ANALYSIS OF FIRST {num_cases} CASES ===\n")
    
    for i, case in enumerate(cases[:num_cases]):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        output = case['expected_output']
        
        print(f"Case {i+1}:")
        print(f"  Input: {days} days, {miles} miles, ${receipts:.2f} receipts")
        print(f"  Output: ${output:.2f}")
        
        # Calculate various ratios and patterns
        per_day = output / days if days > 0 else 0
        print(f"  Per day: ${per_day:.2f}")
        
        # Test if it's close to various simple formulas
        formulas = [
            ("100*days + 0.58*miles", days * 100 + miles * 0.58),
            ("75*days + 0.58*miles", days * 75 + miles * 0.58),
            ("days * 100 + receipts", days * 100 + receipts),
            ("miles * 0.58 + receipts", miles * 0.58 + receipts),
        ]
        
        for name, value in formulas:
            diff = output - value
            print(f"  {name} = ${value:.2f}, diff = ${diff:.2f}")
        
        # Check if output is related to some combination
        if receipts > 0:
            # What if it's base + function of receipts?
            base = days * 100 + miles * 0.58
            receipts_part = output - base
            receipts_factor = receipts_part / receipts
            print(f"  If base=100*days+0.58*miles: receipts factor = {receipts_factor:.2f}")
        
        # Check for caps or thresholds
        daily_cap = output / days if days > 0 else 0
        print(f"  Daily cap would be: ${daily_cap:.2f}")
        
        print()

def look_for_exact_formula_matches(cases: list) -> None:
    """Try to reverse engineer by looking for exact matches"""
    print("=== LOOKING FOR EXACT FORMULA MATCHES ===\n")
    
    # Try many different formulas systematically
    found_matches = {}
    
    for i, case in enumerate(cases[:50]):  # Test first 50 cases
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Try to find what coefficients would work exactly
        for daily_rate in range(50, 151, 5):  # 50 to 150 in steps of 5
            for mileage_rate_cents in range(40, 81, 2):  # 0.40 to 0.80 in steps of 0.02
                mileage_rate = mileage_rate_cents / 100.0
                
                # Calculate what the receipt factor would need to be
                base = days * daily_rate + miles * mileage_rate
                receipts_contribution = expected - base
                
                if receipts > 0:
                    needed_factor = receipts_contribution / receipts
                    
                    # Check if this factor is "nice" (close to common values)
                    nice_factors = [0, 0.25, 0.3, 0.33, 0.4, 0.5, 0.6, 0.67, 0.7, 0.75, 1.0]
                    for nice_factor in nice_factors:
                        if abs(needed_factor - nice_factor) < 0.01:
                            formula = f"{daily_rate}*days + {mileage_rate}*miles + {nice_factor}*receipts"
                            if formula not in found_matches:
                                found_matches[formula] = []
                            found_matches[formula].append(i)
    
    # Show formulas that work for multiple cases
    for formula, case_indices in found_matches.items():
        if len(case_indices) >= 2:
            print(f"{formula}: works for {len(case_indices)} cases: {case_indices}")

def check_for_conditional_logic(cases: list) -> None:
    """Check if there are conditional rules based on input values"""
    print("\n=== CHECKING FOR CONDITIONAL LOGIC ===\n")
    
    # Look for patterns based on ranges
    for i, case in enumerate(cases[:30]):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        output = case['expected_output']
        
        # Calculate what it would be with different rules
        base = days * 100 + miles * 0.58
        
        # Rule 1: Different receipt handling based on amount
        if receipts <= 20:
            predicted1 = base  # No receipts reimbursement
        elif receipts <= 100:
            predicted1 = base + receipts * 0.5
        else:
            predicted1 = base + receipts * 0.3
        
        # Rule 2: Daily cap
        predicted2 = min(base + receipts * 0.5, days * 200)
        
        # Rule 3: Total cap
        predicted3 = min(base + receipts * 0.6, 2000)
        
        error1 = abs(predicted1 - output)
        error2 = abs(predicted2 - output)
        error3 = abs(predicted3 - output)
        
        if error1 < 1 or error2 < 1 or error3 < 1:
            print(f"Case {i+1}: {days} days, {miles} miles, ${receipts:.2f} receipts -> ${output:.2f}")
            if error1 < 1:
                print(f"  Rule 1 works: ${predicted1:.2f} (error: ${error1:.2f})")
            if error2 < 1:
                print(f"  Rule 2 works: ${predicted2:.2f} (error: ${error2:.2f})")
            if error3 < 1:
                print(f"  Rule 3 works: ${predicted3:.2f} (error: ${error3:.2f})")

def main():
    # Load cases
    cases = load_cases('public_cases.json')
    print(f"Total cases: {len(cases)}")
    
    # Analyze first cases in detail
    analyze_first_cases_in_detail(cases, 10)
    
    # Look for exact matches
    look_for_exact_formula_matches(cases)
    
    # Check for conditional logic
    check_for_conditional_logic(cases)

if __name__ == "__main__":
    main()