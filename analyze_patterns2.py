#!/usr/bin/env python3
import json
import random
import statistics
from typing import List, Dict, Tuple

def load_cases(filename: str) -> List[Dict]:
    """Load test cases from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_case(case: Dict) -> Dict:
    """Analyze a single case and calculate various ratios"""
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    output = case['expected_output']
    
    # Calculate different base formulas
    base1 = days * 100 + miles * 0.58  # Standard mileage rate
    base2 = days * 100 + miles * 0.5   # Alternative mileage rate
    base3 = days * 90 + miles * 0.58   # Different daily rate
    base4 = days * 75 + miles * 0.58   # Lower daily rate
    
    # Calculate how output relates to these bases
    diff1 = output - base1
    diff2 = output - base2
    diff3 = output - base3
    diff4 = output - base4
    
    # Try to find if the difference is related to receipts
    if receipts > 0:
        receipts_factor1 = diff1 / receipts
        receipts_factor2 = diff2 / receipts
        receipts_factor3 = diff3 / receipts
        receipts_factor4 = diff4 / receipts
    else:
        receipts_factor1 = receipts_factor2 = receipts_factor3 = receipts_factor4 = 0
    
    # Check if output is a percentage of total inputs
    total_input = days + miles + receipts
    output_ratio = output / total_input if total_input > 0 else 0
    
    # Check if there's a maximum reimbursement pattern
    max_daily = output / days if days > 0 else 0
    
    return {
        'case': case,
        'base1': base1,
        'diff1': diff1,
        'receipts_factor1': receipts_factor1,
        'base2': base2,
        'diff2': diff2,
        'receipts_factor2': receipts_factor2,
        'base3': base3,
        'diff3': diff3,
        'receipts_factor3': receipts_factor3,
        'base4': base4,
        'diff4': diff4,
        'receipts_factor4': receipts_factor4,
        'output_ratio': output_ratio,
        'max_daily': max_daily
    }

def check_formula_with_caps(cases: List[Dict]) -> None:
    """Check if there's a daily cap pattern"""
    print("\n=== CHECKING DAILY CAP PATTERNS ===")
    
    daily_rates = []
    for case in cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        output = case['expected_output']
        
        daily_rate = output / days if days > 0 else 0
        daily_rates.append({
            'rate': daily_rate,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'output': output
        })
    
    # Sort by daily rate
    daily_rates.sort(key=lambda x: x['rate'])
    
    print("Top 5 lowest daily rates:")
    for i in range(min(5, len(daily_rates))):
        r = daily_rates[i]
        print(f"  ${r['rate']:.2f}/day: {r['days']} days, {r['miles']} miles, ${r['receipts']:.2f} receipts -> ${r['output']:.2f}")
    
    print("\nTop 5 highest daily rates:")
    for i in range(max(0, len(daily_rates)-5), len(daily_rates)):
        r = daily_rates[i]
        print(f"  ${r['rate']:.2f}/day: {r['days']} days, {r['miles']} miles, ${r['receipts']:.2f} receipts -> ${r['output']:.2f}")

def test_complex_formulas(cases: List[Dict]) -> None:
    """Test more complex formula patterns"""
    print("\n=== TESTING COMPLEX FORMULAS ===")
    
    # Test formula: min(base + receipts * factor, days * cap)
    for daily_cap in [150, 175, 200, 225, 250]:
        for receipts_factor in [0.3, 0.5, 0.7, 1.0]:
            errors = []
            for case in cases:
                days = case['input']['trip_duration_days']
                miles = case['input']['miles_traveled']
                receipts = case['input']['total_receipts_amount']
                output = case['expected_output']
                
                base = days * 75 + miles * 0.58
                predicted = min(base + receipts * receipts_factor, days * daily_cap)
                error = abs(predicted - output)
                errors.append(error)
            
            avg_error = statistics.mean(errors)
            if avg_error < 100:  # If average error is reasonable
                print(f"Cap=${daily_cap}, factor={receipts_factor}: avg_error=${avg_error:.2f}")

def analyze_receipts_ranges(cases: List[Dict]) -> None:
    """Analyze patterns based on receipt ranges"""
    print("\n=== RECEIPTS RANGE ANALYSIS ===")
    
    ranges = [
        (0, 50),
        (50, 100),
        (100, 200),
        (200, 500),
        (500, 1000),
        (1000, float('inf'))
    ]
    
    for low, high in ranges:
        range_cases = []
        for case in cases:
            receipts = case['input']['total_receipts_amount']
            if low <= receipts < high:
                days = case['input']['trip_duration_days']
                miles = case['input']['miles_traveled']
                output = case['expected_output']
                
                base = days * 100 + miles * 0.58
                diff = output - base
                factor = diff / receipts if receipts > 0 else 0
                
                range_cases.append({
                    'receipts': receipts,
                    'factor': factor,
                    'diff': diff,
                    'output': output,
                    'base': base
                })
        
        if range_cases:
            avg_factor = statistics.mean([c['factor'] for c in range_cases])
            print(f"\nReceipts ${low}-${high if high < float('inf') else '∞'}: {len(range_cases)} cases")
            print(f"  Average receipts factor: {avg_factor:.2f}")
            
            # Show a few examples
            for i in range(min(3, len(range_cases))):
                c = range_cases[i]
                print(f"  Example: ${c['receipts']:.2f} receipts, base=${c['base']:.2f}, output=${c['output']:.2f}, factor={c['factor']:.2f}")

def main():
    # Load all cases
    cases = load_cases('public_cases.json')
    print(f"Total cases: {len(cases)}")
    
    # Take a larger sample
    random.seed(42)
    sample_size = min(100, len(cases))
    sample_cases = random.sample(cases, sample_size)
    
    # Analyze patterns
    print(f"\nAnalyzing {sample_size} random cases...")
    
    # Analyze individual cases
    analyses = []
    for case in sample_cases:
        analyses.append(analyze_case(case))
    
    # Check for consistent factors
    print("\n=== CHECKING RECEIPTS FACTORS ===")
    for base_name, factor_name in [
        ('base1', 'receipts_factor1'),
        ('base2', 'receipts_factor2'),
        ('base3', 'receipts_factor3'),
        ('base4', 'receipts_factor4')
    ]:
        factors = [a[factor_name] for a in analyses if a[factor_name] != 0]
        if factors:
            # Check for values close to integers
            for target in [-3, -2, -1, -0.5, 0, 0.3, 0.5, 0.7, 1, 2, 3]:
                close_count = sum(1 for f in factors if abs(f - target) < 0.1)
                if close_count > len(factors) * 0.1:  # If more than 10% are close
                    print(f"  {base_name}: {close_count}/{len(factors)} cases have factor ≈ {target}")
    
    # Check other patterns
    check_formula_with_caps(sample_cases)
    test_complex_formulas(sample_cases[:20])  # Test on smaller subset
    analyze_receipts_ranges(sample_cases)

if __name__ == "__main__":
    main()