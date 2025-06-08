#!/usr/bin/env python3
"""
Analyze 8-day trip cases - now showing up as top error cases.
Cases 684 and 548 are 8-day trips with high errors.
"""

import csv
import subprocess

def get_8_day_cases():
    """Get all 8-day cases sorted by error."""
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    eight_day_cases = []
    for row in data:
        if int(row['trip_duration_days']) == 8:
            eight_day_cases.append({
                'case': int(row['case_number']),
                'miles': float(row['miles_traveled']),
                'receipts': float(row['total_receipts_amount']),
                'expected': float(row['expected_output']),
                'calculated': float(row['algorithm_result']),
                'error': float(row['absolute_error'])
            })
    
    return sorted(eight_day_cases, key=lambda x: x['error'])

def analyze_8_day_patterns():
    """Analyze 8-day trip patterns and current algorithm performance."""
    
    cases = get_8_day_cases()
    print("🔍 ANALYZING 8-DAY TRIP PATTERNS")
    print("=" * 40)
    
    print(f"Total 8-day cases: {len(cases)}")
    avg_error = sum(c['error'] for c in cases) / len(cases)
    print(f"Average error: ${avg_error:.2f}")
    
    # Analyze over/under calculation bias
    over_calc = sum(1 for c in cases if c['calculated'] > c['expected'])
    print(f"Over-calculated: {over_calc}/{len(cases)} ({over_calc/len(cases)*100:.1f}%)")
    
    # Current algorithm for 8-day trips: base = 45 * 8 = 360, mileage = 0.32 (or 0.35 for 7-day only), receipt_cap = 145 * 8 = 1160
    print(f"\nCurrent 8-day algorithm:")
    print(f"  Base: $45/day × 8 = $360")
    print(f"  Mileage rate: $0.32/mile") 
    print(f"  Receipt cap: $145/day × 8 = $1160")
    
    # Show top error cases
    worst_cases = cases[-10:]
    print(f"\n❌ WORST 8-DAY CASES:")
    for i, case in enumerate(worst_cases):
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        calculated = case['calculated']
        error = case['error']
        
        # Current algorithm breakdown
        base = 45 * 8  # 360
        mileage = miles * 0.32
        receipt_component = min(receipts, 1160)
        current_calc = base + mileage + receipt_component
        
        print(f"   {i+1}. Case {case['case']}: {miles:.0f}mi, ${receipts:.0f}r")
        print(f"      Expected: ${expected:.2f}, Got: ${calculated:.2f}, Error: ${error:.2f}")
        print(f"      Breakdown: ${base} + ${mileage:.2f} + ${receipt_component:.2f} = ${current_calc:.2f}")
        
        # Check if receipts exceed cap
        if receipts > 1160:
            print(f"      ⚠️ Receipts exceed cap by ${receipts - 1160:.2f}")

def analyze_specific_error_cases():
    """Deep dive into Cases 684 and 548."""
    
    print(f"\n🔬 DEEP ANALYSIS OF TOP ERROR CASES")
    print("=" * 45)
    
    # Case 684: 8 days, 795 miles, $1645.99 receipts → Expected: $644.69
    print(f"Case 684: 8 days, 795 miles, $1645.99 receipts")
    print(f"Expected: $644.69")
    
    miles_684 = 795
    receipts_684 = 1645.99
    expected_684 = 644.69
    
    # Current calculation
    base = 360
    mileage = miles_684 * 0.32  # 254.40
    receipt_component = min(receipts_684, 1160)  # 1160 (capped)
    current_total = base + mileage + receipt_component  # 1774.40
    
    print(f"Current: ${base} + ${mileage:.2f} + ${receipt_component:.2f} = ${current_total:.2f}")
    print(f"Error: ${current_total - expected_684:.2f}")
    print(f"🚨 SEVERE over-calculation! System heavily penalizes high receipts")
    
    # What would make this work?
    remaining_after_base_mileage = expected_684 - base - mileage  # 644.69 - 360 - 254.40 = 30.29
    print(f"For accuracy, receipt component should be only ${remaining_after_base_mileage:.2f}")
    receipt_factor = remaining_after_base_mileage / receipts_684  # 0.018
    print(f"That's a {receipt_factor:.3f} factor on receipts (vs current cap system)")
    
    print(f"\n" + "-"*40)
    
    # Case 548: 8 days, 482 miles, $1411.49 receipts → Expected: $631.81
    print(f"Case 548: 8 days, 482 miles, $1411.49 receipts")
    print(f"Expected: $631.81")
    
    miles_548 = 482
    receipts_548 = 1411.49
    expected_548 = 631.81
    
    # Current calculation
    mileage_548 = miles_548 * 0.32  # 154.24
    receipt_component_548 = min(receipts_548, 1160)  # 1160 (capped)
    current_total_548 = base + mileage_548 + receipt_component_548  # 1674.24
    
    print(f"Current: ${base} + ${mileage_548:.2f} + ${receipt_component_548:.2f} = ${current_total_548:.2f}")
    print(f"Error: ${current_total_548 - expected_548:.2f}")
    
    remaining_548 = expected_548 - base - mileage_548  # 117.57
    receipt_factor_548 = remaining_548 / receipts_548  # 0.083
    print(f"For accuracy, receipt component should be ${remaining_548:.2f}")
    print(f"That's a {receipt_factor_548:.3f} factor on receipts")

def test_improved_8_day_formula():
    """Test improved 8-day formula with aggressive receipt penalties."""
    
    cases = get_8_day_cases()
    worst_cases = cases[-15:]  # Test on 15 worst cases
    
    print(f"\n🔧 TESTING IMPROVED 8-DAY FORMULA")
    print("=" * 40)
    
    improvements = 0
    total_improvement = 0
    
    for case in worst_cases:
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        current_error = case['error']
        current_calculated = case['calculated']
        
        # New formula with much more aggressive receipt penalties
        base = 45 * 8  # Keep base the same: 360
        
        # Slightly higher mileage rate (like we did for 7-day)
        mileage = miles * 0.35  # Increased from 0.32
        
        # Much more aggressive receipt penalty system
        if receipts <= 400:
            receipt_component = receipts  # Full value for low receipts
        elif receipts <= 800:
            receipt_component = 400 + (receipts - 400) * 0.5  # 50% for medium
        elif receipts <= 1200:
            receipt_component = 400 + 400 * 0.5 + (receipts - 800) * 0.2  # 20% for high
        else:
            # Very high receipts get almost nothing
            receipt_component = 400 + 400 * 0.5 + 400 * 0.2 + (receipts - 1200) * 0.05
        
        improved_total = base + mileage + receipt_component
        improved_error = abs(improved_total - expected)
        improvement = current_error - improved_error
        
        if improvement > 0:
            improvements += 1
            total_improvement += improvement
        
        # Show breakdown for high-receipt cases
        if receipts >= 1200:
            print(f"\nHigh-receipt case: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
            print(f"  Current: ${current_calculated:.2f} (error: ${current_error:.2f})")
            print(f"  Improved breakdown:")
            print(f"    Base: ${base}")
            print(f"    Mileage: ${mileage:.2f}")
            print(f"    Receipts: ${receipt_component:.2f}")
            print(f"    Total: ${improved_total:.2f} (error: ${improved_error:.2f})")
            print(f"    Improvement: {improvement:+.2f}")
    
    print(f"\n📊 Results: {improvements}/{len(worst_cases)} cases improved")
    if improvements > 0:
        print(f"Average improvement: ${total_improvement/improvements:.2f}")
        print(f"Total improvement: ${total_improvement:.2f}")
    
    return improvements > len(worst_cases) * 0.4

def implement_8_day_fix():
    """Implement improved 8-day formula."""
    
    print(f"\n🔧 IMPLEMENTING 8-DAY ALGORITHM FIX")
    print("=" * 40)
    
    # Read current algorithm
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'r') as f:
        content = f.read()
    
    # The 8-day logic is in the calculate_6_8_day function
    # We need to modify it to handle 8-day trips differently
    
    old_section = """    # Improved mileage rate for 7-day trips
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
        receipt_component = min(receipts, receipt_cap)"""
    
    new_section = """    # Improved mileage rates for 7 and 8-day trips
    if days == 7:
        mileage = miles * 0.35  # Increased from 0.32
    elif days == 8:
        mileage = miles * 0.35  # Increased from 0.32
    else:
        mileage = miles * 0.32
    
    # Improved receipt handling for 7 and 8-day trips
    if days == 7:
        if receipts <= 800:
            receipt_component = receipts
        elif receipts <= 1500:
            receipt_component = 800 + (receipts - 800) * 0.6
        else:
            receipt_component = 800 + 700 * 0.6 + (receipts - 1500) * 0.2
    elif days == 8:
        # Aggressive receipt penalty for 8-day trips
        if receipts <= 400:
            receipt_component = receipts
        elif receipts <= 800:
            receipt_component = 400 + (receipts - 400) * 0.5
        elif receipts <= 1200:
            receipt_component = 400 + 400 * 0.5 + (receipts - 800) * 0.2
        else:
            receipt_component = 400 + 400 * 0.5 + 400 * 0.2 + (receipts - 1200) * 0.05
    else:
        # Original logic for 6-day trips
        receipt_cap = 145 * days
        receipt_component = min(receipts, receipt_cap)"""
    
    # Apply the fix
    updated_content = content.replace(old_section, new_section)
    
    if updated_content != content:
        with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'w') as f:
            f.write(updated_content)
        print("✅ 8-day algorithm updated successfully!")
        return True
    else:
        print("❌ Could not find 8-day section to update")
        return False

def test_updated_8_day_algorithm():
    """Test the updated 8-day algorithm on Cases 684 and 548."""
    
    print(f"\n🧪 TESTING UPDATED 8-DAY ALGORITHM")
    print("=" * 35)
    
    # Test the specific high-error cases
    test_cases = [
        (684, 795, 1645.99, 644.69),
        (548, 482, 1411.49, 631.81)
    ]
    
    improvements = 0
    total_improvement = 0
    
    for case_num, miles, receipts, expected in test_cases:
        try:
            result = subprocess.run(
                ['./run.sh', '8', str(miles), str(receipts)],
                capture_output=True,
                text=True,
                cwd='/Users/raoufrahiche/IdeaProjects/top-coder-challenge'
            )
            
            if result.returncode == 0:
                new_calculated = float(result.stdout.strip())
                
                # Calculate old values
                base = 360
                old_mileage = miles * 0.32
                old_receipt = min(receipts, 1160)
                old_calculated = base + old_mileage + old_receipt
                
                old_error = abs(old_calculated - expected)
                new_error = abs(new_calculated - expected)
                improvement = old_error - new_error
                
                if improvement > 0:
                    improvements += 1
                    total_improvement += improvement
                
                print(f"Case {case_num}: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
                print(f"  Old: ${old_calculated:.2f} (error: ${old_error:.2f})")
                print(f"  New: ${new_calculated:.2f} (error: ${new_error:.2f})")
                print(f"  Improvement: {improvement:+.2f}")
                print()
        
        except Exception as e:
            print(f"Error testing case {case_num}: {e}")
    
    # Test other high-error 8-day cases
    cases = get_8_day_cases()
    other_worst = cases[-5:]  # 5 worst cases
    
    print("Testing other high-error 8-day cases:")
    for case in other_worst:
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        old_calculated = case['calculated']
        old_error = case['error']
        
        try:
            result = subprocess.run(
                ['./run.sh', '8', str(miles), str(receipts)],
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
                
                print(f"  Case {case['case']}: {miles:.0f}mi, ${receipts:.0f}r")
                print(f"    Old: ${old_calculated:.2f} (error: ${old_error:.2f})")
                print(f"    New: ${new_calculated:.2f} (error: ${new_error:.2f})")
                print(f"    Improvement: {improvement:+.2f}")
        
        except Exception as e:
            print(f"Error testing case: {e}")
    
    print(f"\n📊 Results: {improvements} total cases improved")
    if improvements > 0:
        print(f"Average improvement: ${total_improvement/improvements:.2f}")
    
    return improvements >= 2  # Success if both main cases improved

if __name__ == "__main__":
    # Step 1: Analyze 8-day patterns
    analyze_8_day_patterns()
    
    # Step 2: Deep dive into specific error cases
    analyze_specific_error_cases()
    
    # Step 3: Test improved formula
    should_implement = test_improved_8_day_formula()
    
    if should_implement:
        # Step 4: Implement the fix
        fix_applied = implement_8_day_fix()
        
        if fix_applied:
            # Step 5: Test the updated algorithm
            success = test_updated_8_day_algorithm()
            
            if success:
                print("\n✅ 8-DAY ALGORITHM SUCCESSFULLY IMPROVED!")
                print("Ready to move to next duration analysis.")
            else:
                print("\n⚠️ 8-day algorithm updated but results need verification.")
        else:
            print("\n❌ Could not apply 8-day algorithm fix.")
    else:
        print("\n❌ Proposed 8-day improvements not effective enough.")
        print("8-day algorithm requires different approach.")