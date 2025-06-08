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
    
    # Calculate ratios
    per_day_rate = output / days if days > 0 else 0
    reimbursement_rate = output / receipts if receipts > 0 else 0
    
    # Try common formula patterns
    # Pattern 1: Days * X + Miles * Y + Receipts * Z
    # Using 100 for days, 0.58 for miles (standard IRS rate)
    formula1 = days * 100 + miles * 0.58
    formula1_diff = output - formula1
    formula1_ratio = output / formula1 if formula1 > 0 else 0
    
    # Pattern 2: Days * X + Miles * Y + Receipts * Z (with receipts)
    formula2 = days * 100 + miles * 0.58 + receipts
    formula2_diff = output - formula2
    formula2_ratio = output / formula2 if formula2 > 0 else 0
    
    # Pattern 3: Days * X + Miles * Y + Receipts * multiplier
    # Try to find receipts multiplier
    base_expense = days * 100 + miles * 0.58
    receipts_contribution = output - base_expense
    receipts_multiplier = receipts_contribution / receipts if receipts > 0 else 0
    
    return {
        'case': case,
        'per_day_rate': per_day_rate,
        'reimbursement_rate': reimbursement_rate,
        'formula1_ratio': formula1_ratio,
        'formula1_diff': formula1_diff,
        'formula2_ratio': formula2_ratio,
        'formula2_diff': formula2_diff,
        'receipts_multiplier': receipts_multiplier,
        'base_expense': base_expense,
        'receipts_contribution': receipts_contribution
    }

def find_patterns(analyses: List[Dict]) -> None:
    """Find patterns across multiple analyses"""
    print("\n=== PATTERN ANALYSIS ===\n")
    
    # Check if receipts multiplier is consistent
    receipts_multipliers = [a['receipts_multiplier'] for a in analyses if a['receipts_multiplier'] > 0]
    if receipts_multipliers:
        avg_multiplier = statistics.mean(receipts_multipliers)
        std_multiplier = statistics.stdev(receipts_multipliers) if len(receipts_multipliers) > 1 else 0
        print(f"Receipts multiplier: mean={avg_multiplier:.2f}, std={std_multiplier:.2f}")
        
        # Check for common multipliers
        for mult in [1, 2, 3, 4, 5, 10]:
            close_to_mult = sum(1 for m in receipts_multipliers if abs(m - mult) < 0.1)
            if close_to_mult > len(receipts_multipliers) * 0.1:
                print(f"  {close_to_mult} cases have multiplier close to {mult}")
    
    # Check if there's a threshold pattern
    print("\n=== CHECKING THRESHOLD PATTERNS ===")
    for threshold in [10, 15, 20, 25, 30]:
        above_threshold = []
        below_threshold = []
        
        for a in analyses:
            receipts = a['case']['input']['total_receipts_amount']
            if receipts > threshold:
                above_threshold.append(a['receipts_multiplier'])
            else:
                below_threshold.append(a['receipts_multiplier'])
        
        if above_threshold and below_threshold:
            avg_above = statistics.mean(above_threshold)
            avg_below = statistics.mean(below_threshold)
            if abs(avg_above - avg_below) > 0.5:
                print(f"Threshold at {threshold}: below={avg_below:.2f}, above={avg_above:.2f}")

def main():
    # Load cases
    cases = load_cases('public_cases.json')
    print(f"Total cases: {len(cases)}")
    
    # Select 20 random cases
    random.seed(42)  # For reproducibility
    sample_cases = random.sample(cases, min(20, len(cases)))
    
    # Analyze each case
    analyses = []
    print("\n=== INDIVIDUAL CASE ANALYSIS ===\n")
    
    for i, case in enumerate(sample_cases, 1):
        analysis = analyze_case(case)
        analyses.append(analysis)
        
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        output = case['expected_output']
        
        print(f"Case {i}:")
        print(f"  Input: {days} days, {miles} miles, ${receipts:.2f} receipts")
        print(f"  Output: ${output:.2f}")
        print(f"  Per day rate: ${analysis['per_day_rate']:.2f}")
        print(f"  Reimbursement rate: {analysis['reimbursement_rate']:.2f}x")
        print(f"  Base (100*days + 0.58*miles): ${analysis['base_expense']:.2f}")
        print(f"  Receipts contribution: ${analysis['receipts_contribution']:.2f}")
        print(f"  Receipts multiplier: {analysis['receipts_multiplier']:.2f}")
        print()
    
    # Find patterns
    find_patterns(analyses)
    
    # Try to fit a more complex formula
    print("\n=== TESTING SPECIFIC FORMULAS ===\n")
    
    # Test formula: base + (receipts <= 20 ? receipts * 3 : receipts * 1)
    correct_predictions = 0
    for a in analyses:
        days = a['case']['input']['trip_duration_days']
        miles = a['case']['input']['miles_traveled']
        receipts = a['case']['input']['total_receipts_amount']
        expected = a['case']['expected_output']
        
        base = days * 100 + miles * 0.58
        if receipts <= 20:
            predicted = base + receipts * 3
        else:
            predicted = base + receipts * 1
        
        error = abs(predicted - expected)
        if error < 0.01:
            correct_predictions += 1
        elif error > 1:
            print(f"Large error: expected=${expected:.2f}, predicted=${predicted:.2f}, error=${error:.2f}")
            print(f"  Input: {days} days, {miles} miles, ${receipts:.2f} receipts")
    
    print(f"\nFormula with threshold at $20: {correct_predictions}/{len(analyses)} correct")

if __name__ == "__main__":
    main()