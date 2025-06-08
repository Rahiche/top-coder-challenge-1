#!/usr/bin/env python3
"""
Deep analysis of legacy system patterns focusing on the over-calculation bias
and specific error clustering patterns.
"""

import json
import csv
import math
from collections import defaultdict

def analyze_over_calculation_bias():
    """
    61.1% over-calculation bias suggests systematic rounding up or
    different calculation order that accumulates errors upward.
    """
    
    print("🔍 DEEP ANALYSIS: Over-Calculation Bias (61.1%)")
    print("=" * 50)
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        comparison_data = list(reader)
    
    over_calc_cases = []
    under_calc_cases = []
    
    for row in comparison_data:
        expected = float(row['expected_output'])
        our_result = float(row['algorithm_result'])
        days = int(row['trip_duration_days'])
        miles = float(row['miles_traveled'])
        receipts = float(row['total_receipts_amount'])
        
        if our_result > expected:
            over_calc_cases.append({
                'case': row['case_number'],
                'days': days,
                'miles': miles,
                'receipts': receipts,
                'expected': expected,
                'calculated': our_result,
                'excess': our_result - expected
            })
        else:
            under_calc_cases.append({
                'case': row['case_number'],
                'days': days,
                'miles': miles,
                'receipts': receipts,
                'expected': expected,
                'calculated': our_result,
                'deficit': expected - our_result
            })
    
    print(f"Over-calculations: {len(over_calc_cases)} cases")
    print(f"Under-calculations: {len(under_calc_cases)} cases")
    
    # Analyze by trip duration
    over_by_duration = defaultdict(int)
    under_by_duration = defaultdict(int)
    
    for case in over_calc_cases:
        over_by_duration[case['days']] += 1
    
    for case in under_calc_cases:
        under_by_duration[case['days']] += 1
    
    print(f"\nBias by trip duration:")
    for days in sorted(set(list(over_by_duration.keys()) + list(under_by_duration.keys()))):
        over = over_by_duration[days]
        under = under_by_duration[days]
        total = over + under
        if total > 0:
            over_pct = over / total * 100
            print(f"   {days} days: {over_pct:.1f}% over-calculated ({over}/{total})")
    
    # Look for systematic patterns in excess amounts
    excess_amounts = [case['excess'] for case in over_calc_cases]
    if excess_amounts:
        avg_excess = sum(excess_amounts) / len(excess_amounts)
        print(f"\nAverage over-calculation: ${avg_excess:.2f}")
        
        # Check for common excess amounts (might indicate rounding rules)
        excess_buckets = defaultdict(int)
        for excess in excess_amounts:
            bucket = round(excess, 1)  # Round to nearest 10 cents
            excess_buckets[bucket] += 1
        
        common_excess = sorted(excess_buckets.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"Most common excess amounts:")
        for amount, count in common_excess:
            print(f"   ${amount:.1f}: {count} cases")

def test_cobol_packed_decimal():
    """
    COBOL packed decimal format might explain some errors.
    Packed decimal stores 2 digits per byte, which can cause specific rounding.
    """
    
    print(f"\n🔍 COBOL Packed Decimal Analysis:")
    print("=" * 35)
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        comparison_data = list(reader)
    
    def cobol_packed_decimal_round(value):
        """
        Simulate COBOL packed decimal rounding.
        Numbers are stored as BCD with specific precision.
        """
        # Convert to string, then back to simulate storage precision loss
        str_val = f"{value:.4f}"  # 4 decimal places max in many COBOL systems
        
        # Simulate packed decimal storage (2 digits per byte)
        # This can introduce subtle rounding errors
        rounded_val = round(float(str_val), 2)
        
        # Some COBOL systems round .5 up always (not banker's rounding)
        if abs(rounded_val - round(rounded_val)) == 0.5:
            if rounded_val > 0:
                rounded_val = math.ceil(rounded_val)
            else:
                rounded_val = math.floor(rounded_val)
        
        return rounded_val
    
    improvements = 0
    total_improvement = 0
    
    for row in comparison_data[:100]:  # Test first 100
        expected = float(row['expected_output'])
        our_result = float(row['algorithm_result'])
        
        packed_result = cobol_packed_decimal_round(our_result)
        
        original_error = abs(our_result - expected)
        packed_error = abs(packed_result - expected)
        
        if packed_error < original_error:
            improvement = original_error - packed_error
            improvements += 1
            total_improvement += improvement
            
            if improvements <= 3:
                print(f"   Case {row['case_number']}: ${original_error:.2f} -> ${packed_error:.2f}")
    
    print(f"   Improvements: {improvements}/100 cases")
    if improvements > 0:
        print(f"   Average improvement: ${total_improvement/improvements:.2f}")

def test_calculation_order_effects():
    """
    Test if different calculation orders explain the bias.
    Early systems might have calculated components in different orders.
    """
    
    print(f"\n🔍 Calculation Order Effects:")
    print("=" * 30)
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    # Test different calculation orders for a few cases
    test_cases = public_cases[:5]
    
    for i, case in enumerate(test_cases):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        print(f"\nCase {i+1}: {days} days, {miles} miles, ${receipts:.2f} receipts")
        print(f"Expected: ${expected:.2f}")
        
        # Test various calculation approaches that might be used in legacy systems
        
        # Approach 1: Round each component separately (common in COBOL)
        if days == 1:
            base = round(80.0, 2)
            mileage = round(miles * 0.60, 2)
            receipt_comp = round(min(receipts, 2000) * 0.5, 2)
            total_1 = base + mileage + receipt_comp
        else:
            total_1 = 0  # Simplified for demo
        
        # Approach 2: Calculate total, then round (modern approach)
        if days == 1:
            total_2 = round(80 + miles * 0.60 + min(receipts, 2000) * 0.5, 2)
        else:
            total_2 = 0
        
        # Approach 3: Use integer arithmetic (common in early systems)
        if days == 1:
            base_cents = 8000  # 80.00 in cents
            mileage_cents = round(miles * 60)  # 0.60 per mile in cents
            receipt_cents = round(min(receipts, 2000) * 50)  # 0.5 factor in cents
            total_3 = (base_cents + mileage_cents + receipt_cents) / 100
        else:
            total_3 = 0
        
        if days == 1:  # Only test 1-day cases for this demo
            print(f"   Round components: ${total_1:.2f} (error: ${abs(total_1-expected):.2f})")
            print(f"   Round final: ${total_2:.2f} (error: ${abs(total_2-expected):.2f})")
            print(f"   Integer arithmetic: ${total_3:.2f} (error: ${abs(total_3-expected):.2f})")
            
            if abs(total_1 - expected) < abs(total_2 - expected):
                print("   → Component rounding seems better!")
            if abs(total_3 - expected) < min(abs(total_1-expected), abs(total_2-expected)):
                print("   → Integer arithmetic seems best!")

def test_ebcdic_character_encoding():
    """
    Test if EBCDIC character encoding differences might affect number parsing.
    This is a long shot, but early IBM systems used EBCDIC instead of ASCII.
    """
    
    print(f"\n🔍 EBCDIC Character Encoding Effects:")
    print("=" * 40)
    
    # EBCDIC had different numeric representations
    # This is mostly relevant for data input/output, not calculations
    # But could affect how numbers were parsed from punch cards
    
    ascii_to_ebcdic_digits = {
        '0': 0xF0, '1': 0xF1, '2': 0xF2, '3': 0xF3, '4': 0xF4,
        '5': 0xF5, '6': 0xF6, '7': 0xF7, '8': 0xF8, '9': 0xF9
    }
    
    print("   EBCDIC digit encoding differences detected in:")
    print("   - Packed decimal representation")
    print("   - Zone decimal format")
    print("   - Unsigned numeric fields")
    print("   → Unlikely to cause systematic calculation errors")
    print("   → More likely to cause data corruption or parsing errors")

def analyze_systematic_rounding():
    """
    Analyze if there's a systematic rounding pattern that explains the bias.
    """
    
    print(f"\n🔍 Systematic Rounding Pattern Analysis:")
    print("=" * 45)
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        comparison_data = list(reader)
    
    # Look for patterns in the decimal places
    cent_patterns = defaultdict(int)
    
    for row in comparison_data[:200]:  # Sample 200 cases
        our_result = float(row['algorithm_result'])
        expected = float(row['expected_output'])
        
        # Extract cents from both values
        our_cents = round((our_result % 1) * 100)
        expected_cents = round((expected % 1) * 100)
        
        cent_patterns[our_cents] += 1
    
    print("Distribution of cents in our calculations:")
    sorted_cents = sorted(cent_patterns.items())
    for cents, count in sorted_cents[:10]:  # Show first 10
        print(f"   .{cents:02d}: {count} cases")
    
    # Check if certain cent values are over-represented
    avg_count = sum(cent_patterns.values()) / len(cent_patterns)
    overrepresented = [(cents, count) for cents, count in cent_patterns.items() 
                      if count > avg_count * 1.5]
    
    if overrepresented:
        print(f"\nOver-represented cent values (possible rounding artifacts):")
        for cents, count in overrepresented:
            print(f"   .{cents:02d}: {count} cases ({count/200*100:.1f}%)")

if __name__ == "__main__":
    print("🕰️  DEEP LEGACY SYSTEM ANALYSIS")
    print("=" * 40)
    print("Focus: 61.1% over-calculation bias and error clustering")
    print()
    
    # Analyze the over-calculation bias
    analyze_over_calculation_bias()
    
    # Test COBOL packed decimal
    test_cobol_packed_decimal()
    
    # Test calculation order effects
    test_calculation_order_effects()
    
    # Test EBCDIC effects
    test_ebcdic_character_encoding()
    
    # Analyze systematic rounding
    analyze_systematic_rounding()
    
    print(f"\n" + "=" * 60)
    print("🎯 LEGACY SYSTEM CONCLUSIONS:")
    print("The 61.1% over-calculation bias suggests:")
    print("1. 🔧 Component-wise rounding (COBOL style) vs final rounding")
    print("2. 📊 Different calculation order accumulating upward errors") 
    print("3. 🎯 Systematic 'round half up' instead of banker's rounding")
    print("4. 💾 Fixed-point arithmetic with specific precision handling")
    print("\n🔍 Next steps: Test component-wise rounding in the algorithm")