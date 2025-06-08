#!/usr/bin/env python3
"""
Test for legacy system computational quirks that might explain calculation errors.
This explores COBOL, mainframe, and early computer system behaviors.
"""

import json
import csv
import math
import decimal
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

def cobol_decimal_rounding(value, places=2):
    """
    COBOL uses "round half away from zero" which is different from Python's default.
    COBOL: 2.5 -> 3, -2.5 -> -3
    Python: 2.5 -> 2, -2.5 -> -2 (banker's rounding)
    """
    d = Decimal(str(value))
    return float(d.quantize(Decimal('0.' + '0' * places), rounding=ROUND_HALF_UP))

def cobol_truncation(value, places=2):
    """
    Early COBOL systems sometimes truncated instead of rounding.
    """
    multiplier = 10 ** places
    return math.floor(value * multiplier) / multiplier

def fixed_point_arithmetic(value, decimal_places=2, total_digits=8):
    """
    Simulate fixed-point arithmetic with limited precision.
    Early systems used fixed-point instead of floating-point.
    """
    # Convert to fixed-point representation
    multiplier = 10 ** decimal_places
    fixed_value = round(value * multiplier)
    
    # Apply overflow/underflow limits
    max_value = 10 ** (total_digits - decimal_places) - 1
    if fixed_value > max_value:
        fixed_value = max_value
    elif fixed_value < -max_value:
        fixed_value = -max_value
    
    return fixed_value / multiplier

def binary_coded_decimal_errors(value):
    """
    BCD (Binary Coded Decimal) systems had specific rounding behaviors.
    Each decimal digit stored in 4 bits, leading to specific error patterns.
    """
    # Simulate BCD rounding to nearest representable value
    str_val = f"{value:.4f}"
    return float(str_val[:str_val.find('.') + 3])  # Keep only 2 decimal places

def mainframe_word_size_effects(value):
    """
    Early mainframes had specific word sizes (36-bit, 60-bit) that affected calculations.
    Simulate potential precision loss from word size limitations.
    """
    # Simulate 36-bit precision limitations
    # Convert to integer representation, apply limits, convert back
    scaled = value * 100  # 2 decimal places
    
    # 36-bit signed integer range: -2^35 to 2^35-1
    max_val = 2**35 - 1
    min_val = -(2**35)
    
    if scaled > max_val:
        scaled = max_val
    elif scaled < min_val:
        scaled = min_val
    
    return scaled / 100

def punch_card_column_limits(value):
    """
    Punch cards had 80 columns, which could limit number representation.
    This might cause truncation of large numbers.
    """
    # Simulate 8-character numeric field limitation
    str_val = f"{value:.2f}"
    if len(str_val) > 8:
        # Truncate to fit in 8 characters
        if '.' in str_val:
            before_decimal = str_val.split('.')[0]
            if len(before_decimal) > 5:  # Save 3 chars for ".XX"
                str_val = before_decimal[:5] + ".00"
            else:
                str_val = str_val[:8]
        else:
            str_val = str_val[:8]
    return float(str_val)

def test_legacy_calculations():
    """Test various legacy system calculation quirks."""
    
    # Load our comparison data
    comparison_data = []
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        comparison_data = list(reader)
    
    print("🕰️  Testing Legacy System Computational Quirks")
    print("=" * 60)
    
    # Focus on cases with specific error patterns
    test_cases = []
    
    # Get high-error cases
    high_error_cases = [row for row in comparison_data 
                       if float(row['absolute_error']) > 100]
    
    # Get cases with specific error patterns that might indicate legacy quirks
    for row in comparison_data[:50]:  # Test first 50 cases for detailed analysis
        expected = float(row['expected_output'])
        our_result = float(row['algorithm_result'])
        
        test_cases.append({
            'case': int(row['case_number']),
            'expected': expected,
            'our_result': our_result,
            'days': int(row['trip_duration_days']),
            'miles': float(row['miles_traveled']),
            'receipts': float(row['total_receipts_amount'])
        })
    
    quirk_tests = {
        'COBOL Rounding': cobol_decimal_rounding,
        'COBOL Truncation': cobol_truncation,
        'Fixed Point': fixed_point_arithmetic,
        'BCD Errors': binary_coded_decimal_errors,
        'Mainframe Word Size': mainframe_word_size_effects,
        'Punch Card Limits': punch_card_column_limits
    }
    
    best_improvements = {}
    
    for quirk_name, quirk_func in quirk_tests.items():
        print(f"\n🔍 Testing {quirk_name}:")
        
        total_improvement = 0
        significant_improvements = 0
        
        for case in test_cases:
            # Apply the quirk to our result
            quirked_result = quirk_func(case['our_result'])
            
            # Calculate errors
            original_error = abs(case['our_result'] - case['expected'])
            quirked_error = abs(quirked_result - case['expected'])
            improvement = original_error - quirked_error
            
            if improvement > 1:  # Significant improvement
                significant_improvements += 1
                total_improvement += improvement
                
                if significant_improvements <= 3:  # Show first 3 examples
                    print(f"   Case {case['case']}: ${original_error:.2f} -> ${quirked_error:.2f} "
                          f"(improvement: ${improvement:.2f})")
        
        avg_improvement = total_improvement / len(test_cases) if test_cases else 0
        improvement_rate = significant_improvements / len(test_cases) * 100
        
        print(f"   📊 Significant improvements: {significant_improvements}/{len(test_cases)} "
              f"({improvement_rate:.1f}%)")
        print(f"   📈 Average improvement: ${avg_improvement:.2f}")
        
        best_improvements[quirk_name] = {
            'improvements': significant_improvements,
            'avg_improvement': avg_improvement,
            'rate': improvement_rate
        }
    
    # Find the best quirk
    best_quirk = max(best_improvements.items(), 
                    key=lambda x: x[1]['improvements'])
    
    print(f"\n🏆 Best Legacy Quirk: {best_quirk[0]}")
    print(f"   Improved {best_quirk[1]['improvements']} cases")
    print(f"   Average improvement: ${best_quirk[1]['avg_improvement']:.2f}")
    
    return best_quirk

def test_specific_legacy_patterns():
    """Test specific patterns known in legacy systems."""
    
    print(f"\n🔬 Testing Specific Legacy Patterns:")
    print("=" * 40)
    
    # Load comparison data
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        comparison_data = list(reader)
    
    patterns_found = []
    
    # Pattern 1: Results ending in .00 (suggests truncation)
    truncated_results = [row for row in comparison_data 
                        if float(row['algorithm_result']) == int(float(row['algorithm_result']))]
    
    if len(truncated_results) > 10:
        patterns_found.append(f"🔸 Truncation Pattern: {len(truncated_results)} results end in .00")
    
    # Pattern 2: Specific rounding patterns
    half_rounded_up = 0
    half_rounded_down = 0
    
    for row in comparison_data:
        result_str = f"{float(row['algorithm_result']):.2f}"
        if result_str.endswith('.50'):
            expected = float(row['expected_output'])
            if expected > float(row['algorithm_result']):
                half_rounded_down += 1
            else:
                half_rounded_up += 1
    
    if half_rounded_up > 0 or half_rounded_down > 0:
        patterns_found.append(f"🔸 Half-value Rounding: {half_rounded_up} up, {half_rounded_down} down")
    
    # Pattern 3: Overflow/underflow patterns
    max_result = max(float(row['algorithm_result']) for row in comparison_data)
    min_result = min(float(row['algorithm_result']) for row in comparison_data)
    
    # Check for suspicious round numbers that might indicate limits
    suspicious_maxes = [9999.99, 999.99, 99999.99, 32767.99]  # Common system limits
    for limit in suspicious_maxes:
        if abs(max_result - limit) < 1:
            patterns_found.append(f"🔸 Possible Overflow Limit: Max result ${max_result:.2f} near ${limit}")
    
    # Pattern 4: BCD-style errors (digits ending in specific patterns)
    bcd_patterns = {}
    for row in comparison_data[:100]:  # Sample first 100
        last_digit = int(float(row['algorithm_result']) * 100) % 10
        bcd_patterns[last_digit] = bcd_patterns.get(last_digit, 0) + 1
    
    # Check if certain digits are over/under-represented (BCD errors)
    avg_count = sum(bcd_patterns.values()) / len(bcd_patterns)
    for digit, count in bcd_patterns.items():
        if count > avg_count * 1.5:
            patterns_found.append(f"🔸 BCD Pattern: Digit {digit} over-represented in cents")
    
    if patterns_found:
        print("Legacy patterns detected:")
        for pattern in patterns_found:
            print(f"   {pattern}")
    else:
        print("   No obvious legacy computational patterns detected")
    
    return patterns_found

def analyze_error_distribution():
    """Analyze the distribution of errors for legacy system signatures."""
    
    print(f"\n📊 Error Distribution Analysis:")
    print("=" * 35)
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        comparison_data = list(reader)
    
    errors = [float(row['absolute_error']) for row in comparison_data]
    
    # Check for clustered errors (common in legacy systems)
    error_buckets = {}
    for error in errors:
        bucket = round(error)  # Round to nearest dollar
        error_buckets[bucket] = error_buckets.get(bucket, 0) + 1
    
    # Find the most common error amounts
    common_errors = sorted(error_buckets.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("Most common error amounts:")
    for error_amount, count in common_errors:
        print(f"   ${error_amount:.0f}: {count} cases ({count/len(errors)*100:.1f}%)")
    
    # Check for systematic bias
    positive_errors = sum(1 for row in comparison_data 
                         if float(row['algorithm_result']) > float(row['expected_output']))
    negative_errors = len(comparison_data) - positive_errors
    
    print(f"\nError bias:")
    print(f"   Algorithm too high: {positive_errors} cases ({positive_errors/len(comparison_data)*100:.1f}%)")
    print(f"   Algorithm too low: {negative_errors} cases ({negative_errors/len(comparison_data)*100:.1f}%)")
    
    # This pattern can indicate specific legacy system behaviors
    if abs(positive_errors - negative_errors) > len(comparison_data) * 0.2:
        if positive_errors > negative_errors:
            print("   🚨 Strong bias toward over-calculation (possible legacy rounding up)")
        else:
            print("   🚨 Strong bias toward under-calculation (possible legacy truncation)")

if __name__ == "__main__":
    print("🕰️  LEGACY SYSTEM COMPUTATIONAL QUIRKS ANALYSIS")
    print("=" * 60)
    print("Testing hypothesis: Errors may be due to old COBOL/mainframe calculation quirks")
    print()
    
    # Test legacy calculation quirks
    best_quirk = test_legacy_calculations()
    
    # Test specific patterns
    legacy_patterns = test_specific_legacy_patterns()
    
    # Analyze error distribution
    analyze_error_distribution()
    
    print(f"\n" + "=" * 60)
    print("🎯 CONCLUSIONS:")
    
    if best_quirk[1]['improvements'] > 10:
        print(f"✅ Strong evidence for legacy quirks: {best_quirk[0]} improved {best_quirk[1]['improvements']} cases")
        print("🔧 Recommendation: Apply legacy computational corrections to algorithm")
    elif legacy_patterns:
        print("⚠️  Some legacy patterns detected, but improvements are limited")
        print("🔍 Recommendation: Investigate patterns further before applying corrections")
    else:
        print("❌ No strong evidence for simple legacy computational quirks")
        print("🤔 Recommendation: Errors likely due to complex business logic, not computational artifacts")