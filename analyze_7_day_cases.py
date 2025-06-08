#!/usr/bin/env python3
"""
Deep analysis of 7-day trip cases to identify the exact issues.
"""

import csv
import subprocess

def get_7_day_cases():
    """Get all 7-day cases sorted by error."""
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    seven_day_cases = []
    for row in data:
        if int(row['trip_duration_days']) == 7:
            seven_day_cases.append({
                'case': int(row['case_number']),
                'miles': float(row['miles_traveled']),
                'receipts': float(row['total_receipts_amount']),
                'expected': float(row['expected_output']),
                'calculated': float(row['algorithm_result']),
                'error': float(row['absolute_error'])
            })
    
    return sorted(seven_day_cases, key=lambda x: x['error'])

def analyze_best_7_day_cases():
    """Analyze the best 7-day cases to understand the working formula."""
    
    cases = get_7_day_cases()
    print("🔍 ANALYZING BEST 7-DAY CASES")
    print("=" * 40)
    
    # Look at the 10 best cases
    best_cases = cases[:10]
    
    for i, case in enumerate(best_cases):
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        calculated = case['calculated']
        error = case['error']
        
        print(f"\nCase {i+1}: {miles:.0f}mi, ${receipts:.0f}r")
        print(f"  Expected: ${expected:.2f}, Got: ${calculated:.2f}, Error: ${error:.2f}")
        
        # Current algorithm: base_per_day = 73, mileage = 0.32, receipt_cap = 145 * 7 = 1015
        current_base = 73 * 7  # 511
        current_mileage = miles * 0.32
        current_receipts = min(receipts, 1015)
        current_total = current_base + current_mileage + current_receipts
        
        print(f"  Current breakdown: ${current_base} + ${current_mileage:.2f} + ${current_receipts:.2f} = ${current_total:.2f}")
        
        # Try to work backwards to find what the actual formula should be
        # If we assume mileage rate is correct, what would the other components need to be?
        remaining_after_mileage = expected - current_mileage
        
        # If receipts are handled correctly, what base would we need?
        if receipts <= 1015:  # Within current cap
            implied_base = remaining_after_mileage - receipts
            print(f"  If receipts full value: base would need to be ${implied_base:.2f} (${implied_base/7:.2f}/day)")
        
        # If base is correct, what receipt handling would we need?
        implied_receipt_value = remaining_after_mileage - current_base
        if receipts > 0:
            implied_receipt_factor = implied_receipt_value / receipts
            print(f"  If base ${current_base}: receipt factor would be {implied_receipt_factor:.3f}")

def test_improved_7_day_formula():
    """Test an improved formula for 7-day trips based on analysis."""
    
    cases = get_7_day_cases()
    worst_cases = cases[-10:]  # 10 worst cases
    
    print(f"\n🔧 TESTING IMPROVED 7-DAY FORMULA")
    print("=" * 40)
    
    improvements = 0
    total_improvement = 0
    
    for case in worst_cases:
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        current_error = case['error']
        
        # Current formula issues based on analysis:
        # 1. High receipts (>$1000) cause high errors
        # 2. High mileage cases have issues
        
        # Test improved formula:
        # - Keep base rate at 73/day
        # - Adjust mileage rate slightly
        # - Add penalty for very high receipts
        
        base = 73 * 7  # 511
        
        # Slightly higher mileage rate for better accuracy
        mileage_component = miles * 0.35  # Increased from 0.32
        
        # More sophisticated receipt handling
        if receipts <= 800:
            receipt_component = receipts  # Full value for reasonable receipts
        elif receipts <= 1500:
            receipt_component = 800 + (receipts - 800) * 0.6  # Reduced rate for high receipts
        else:
            receipt_component = 800 + 700 * 0.6 + (receipts - 1500) * 0.2  # Heavy penalty for very high receipts
        
        improved_total = base + mileage_component + receipt_component
        improved_error = abs(improved_total - expected)
        improvement = current_error - improved_error
        
        if improvement > 0:
            improvements += 1
            total_improvement += improvement
        
        print(f"Case: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
        print(f"  Current: ${case['calculated']:.2f} (error: ${current_error:.2f})")
        print(f"  Improved: ${improved_total:.2f} (error: ${improved_error:.2f})")
        print(f"  Change: {improvement:+.2f}")
        print()
    
    print(f"📊 Results: {improvements}/10 cases improved")
    if improvements > 0:
        print(f"Average improvement: ${total_improvement/improvements:.2f}")
        print(f"Total improvement: ${total_improvement:.2f}")
    
    return improvements > 5  # Return True if majority improved

def implement_7_day_fix():
    """Implement the improved 7-day formula in the algorithm."""
    
    print(f"\n🔧 IMPLEMENTING 7-DAY ALGORITHM FIX")
    print("=" * 40)
    
    # Read the current run.sh file
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'r') as f:
        content = f.read()
    
    # Find and replace the 7-day calculation
    old_7_day_section = """    elif days == 7:
        base_per_day = 73"""
    
    new_7_day_section = """    elif days == 7:
        base_per_day = 73"""
    
    # The actual fix will be in the receipt handling section
    # Look for the section that handles 6-8 day trips
    
    old_receipt_section = """    base = base_per_day * days
    mileage = miles * 0.32
    # Receipt cap at $145/day
    receipt_cap = 145 * days
    receipt_component = min(receipts, receipt_cap)
    
    return base + mileage + receipt_component"""
    
    new_receipt_section = """    base = base_per_day * days
    
    # Improved mileage rate for 7-day trips
    if days == 7:
        mileage = miles * 0.35  # Increased from 0.32
    else:
        mileage = miles * 0.32
    
    # Improved receipt handling for 7-day trips
    if days == 7:
        if receipts <= 800:
            receipt_component = receipts
        elif receipts <= 1500:
            receipt_component = 800 + (receipts - 800) * 0.6
        else:
            receipt_component = 800 + 700 * 0.6 + (receipts - 1500) * 0.2
    else:
        # Original logic for 6 and 8 day trips
        receipt_cap = 145 * days
        receipt_component = min(receipts, receipt_cap)
    
    return base + mileage + receipt_component"""
    
    # Apply the fix
    updated_content = content.replace(old_receipt_section, new_receipt_section)
    
    if updated_content != content:
        with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'w') as f:
            f.write(updated_content)
        print("✅ 7-day algorithm updated successfully!")
        return True
    else:
        print("❌ Could not find section to update")
        return False

def test_updated_algorithm():
    """Test the updated algorithm on 7-day cases."""
    
    print(f"\n🧪 TESTING UPDATED ALGORITHM")
    print("=" * 30)
    
    cases = get_7_day_cases()
    test_cases = cases[-5:]  # Test on 5 worst cases
    
    improvements = 0
    total_improvement = 0
    
    for case in test_cases:
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        old_calculated = case['calculated']
        old_error = case['error']
        
        # Run updated algorithm
        try:
            result = subprocess.run(
                ['./run.sh', '7', str(miles), str(receipts)],
                capture_output=True,
                text=True,
                cwd='/Users/raoufrahiche/IdeaProjects/top-coder-challenge'
            )
            
            if result.returncode == 0:
                new_calculated = float(result.stdout.strip())
                new_error = abs(new_calculated - expected)
                improvement = old_error - new_error
                
                if improvement > 0:
                    improvements += 1
                    total_improvement += improvement
                
                print(f"Case: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
                print(f"  Old: ${old_calculated:.2f} (error: ${old_error:.2f})")
                print(f"  New: ${new_calculated:.2f} (error: ${new_error:.2f})")
                print(f"  Improvement: {improvement:+.2f}")
                print()
            
        except Exception as e:
            print(f"Error testing case: {e}")
    
    print(f"📊 Results: {improvements}/5 test cases improved")
    if improvements > 0:
        print(f"Average improvement: ${total_improvement/improvements:.2f}")
    
    return improvements >= 3  # Return True if majority improved

if __name__ == "__main__":
    # Step 1: Analyze best cases to understand working formula
    analyze_best_7_day_cases()
    
    # Step 2: Test improved formula on worst cases
    should_implement = test_improved_7_day_formula()
    
    if should_implement:
        # Step 3: Implement the fix
        fix_applied = implement_7_day_fix()
        
        if fix_applied:
            # Step 4: Test the updated algorithm
            success = test_updated_algorithm()
            
            if success:
                print("\n✅ 7-DAY ALGORITHM SUCCESSFULLY IMPROVED!")
                print("Ready to move to next duration analysis.")
            else:
                print("\n⚠️ Algorithm updated but improvements not significant.")
        else:
            print("\n❌ Could not apply algorithm fix.")
    else:
        print("\n❌ Proposed improvements not effective enough.")
        print("7-day algorithm requires different approach.")