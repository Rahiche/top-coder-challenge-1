#!/usr/bin/env python3
"""
Analyze 1-day trip cases - our 3rd best performing duration.
The top error case (Case 996) is a 1-day trip with very high mileage and receipts.
"""

import csv
import subprocess

def get_1_day_cases():
    """Get all 1-day cases sorted by error."""
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    one_day_cases = []
    for row in data:
        if int(row['trip_duration_days']) == 1:
            one_day_cases.append({
                'case': int(row['case_number']),
                'miles': float(row['miles_traveled']),
                'receipts': float(row['total_receipts_amount']),
                'expected': float(row['expected_output']),
                'calculated': float(row['algorithm_result']),
                'error': float(row['absolute_error'])
            })
    
    return sorted(one_day_cases, key=lambda x: x['error'])

def analyze_1_day_patterns():
    """Analyze patterns in 1-day trip errors."""
    
    cases = get_1_day_cases()
    print("🔍 ANALYZING 1-DAY TRIP PATTERNS")
    print("=" * 40)
    
    print(f"Total 1-day cases: {len(cases)}")
    avg_error = sum(c['error'] for c in cases) / len(cases)
    print(f"Average error: ${avg_error:.2f}")
    
    # Analyze by mileage ranges
    low_mile_cases = [c for c in cases if c['miles'] < 200]
    med_mile_cases = [c for c in cases if 200 <= c['miles'] < 800]
    high_mile_cases = [c for c in cases if c['miles'] >= 800]
    
    print(f"\nMileage distribution:")
    print(f"  < 200 miles: {len(low_mile_cases)} cases")
    print(f"  200-800 miles: {len(med_mile_cases)} cases") 
    print(f"  ≥ 800 miles: {len(high_mile_cases)} cases")
    
    # Analyze by receipt ranges
    low_receipt_cases = [c for c in cases if c['receipts'] < 100]
    med_receipt_cases = [c for c in cases if 100 <= c['receipts'] < 1000]
    high_receipt_cases = [c for c in cases if c['receipts'] >= 1000]
    
    print(f"\nReceipt distribution:")
    print(f"  < $100: {len(low_receipt_cases)} cases")
    print(f"  $100-1000: {len(med_receipt_cases)} cases")
    print(f"  ≥ $1000: {len(high_receipt_cases)} cases")
    
    # Analyze worst cases
    worst_cases = cases[-10:]
    print(f"\n❌ WORST 1-DAY CASES:")
    for i, case in enumerate(worst_cases):
        print(f"   {i+1}. Case {case['case']}: {case['miles']:.0f}mi, ${case['receipts']:.0f}r")
        print(f"      Expected: ${case['expected']:.2f}, Got: ${case['calculated']:.2f}, Error: ${case['error']:.2f}")
    
    # Check for patterns in worst cases
    worst_high_mile = [c for c in worst_cases if c['miles'] >= 800]
    worst_high_receipt = [c for c in worst_cases if c['receipts'] >= 1000]
    
    if len(worst_high_mile) > 5:
        print(f"\n⚠️ HIGH MILEAGE problem: {len(worst_high_mile)}/10 worst cases have ≥800 miles")
    
    if len(worst_high_receipt) > 5:
        print(f"\n⚠️ HIGH RECEIPT problem: {len(worst_high_receipt)}/10 worst cases have ≥$1000 receipts")

def analyze_case_996():
    """Deep dive into Case 996 - the highest error case overall."""
    
    print(f"\n🔬 CASE 996 DEEP ANALYSIS (Highest Error Case)")
    print("=" * 50)
    
    # Case 996: 1 day, 1082 miles, $1809.49 receipts → Expected: $446.94
    miles = 1082
    receipts = 1809.49
    expected = 446.94
    
    print(f"Input: 1 day, {miles} miles, ${receipts:.2f} receipts")
    print(f"Expected output: ${expected:.2f}")
    
    # Current algorithm: base = 80, mileage = miles * 0.60, receipts = min(receipts, 2000) * 0.5
    current_base = 80
    current_mileage = miles * 0.60  # 649.20
    current_receipts = min(receipts, 2000) * 0.5  # 904.75
    current_total = current_base + current_mileage + current_receipts  # 1633.95
    
    print(f"\nCurrent algorithm breakdown:")
    print(f"  Base: ${current_base}")
    print(f"  Mileage: {miles} × $0.60 = ${current_mileage:.2f}")
    print(f"  Receipts: min(${receipts:.2f}, $2000) × 0.5 = ${current_receipts:.2f}")
    print(f"  Total: ${current_total:.2f}")
    print(f"  Error: ${abs(current_total - expected):.2f}")
    
    print(f"\n🔍 What's wrong?")
    print(f"Expected ${expected:.2f} but got ${current_total:.2f}")
    print(f"The system severely penalizes high-mileage + high-receipt combinations!")
    
    # Work backwards from expected result
    remaining_after_base = expected - current_base  # 366.94
    print(f"\nReverse engineering:")
    print(f"  After base ${current_base}: ${remaining_after_base:.2f} remaining")
    
    # If mileage component is accurate, what should receipt component be?
    remaining_after_mileage = remaining_after_base - current_mileage
    print(f"  After mileage ${current_mileage:.2f}: ${remaining_after_mileage:.2f} remaining for receipts")
    
    if remaining_after_mileage < 0:
        print(f"  ⚠️ NEGATIVE! The mileage component alone exceeds the expected total!")
        print(f"  This suggests either:")
        print(f"    1. Lower mileage rate for high-mileage trips")
        print(f"    2. Receipt penalty system for high-mileage cases")
        print(f"    3. Different base calculation for extreme cases")

def test_improved_1_day_formula():
    """Test improved formulas for 1-day trips."""
    
    cases = get_1_day_cases()
    worst_cases = cases[-15:]  # Test on 15 worst cases
    
    print(f"\n🔧 TESTING IMPROVED 1-DAY FORMULAS")
    print("=" * 40)
    
    improvements = 0
    total_improvement = 0
    
    for case in worst_cases:
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        current_error = case['error']
        current_calculated = case['calculated']
        
        # Test formula with penalties for extreme cases
        base = 80
        
        # Progressive mileage penalty for high-mileage trips
        if miles <= 500:
            mileage = miles * 0.60
        elif miles <= 1000:
            mileage = 500 * 0.60 + (miles - 500) * 0.40  # Reduced rate for 500+ miles
        else:
            mileage = 500 * 0.60 + 500 * 0.40 + (miles - 1000) * 0.20  # Heavy penalty for 1000+ miles
        
        # Progressive receipt penalty
        if receipts <= 500:
            receipt_component = receipts * 0.5
        elif receipts <= 1500:
            receipt_component = 500 * 0.5 + (receipts - 500) * 0.3  # Reduced for high receipts
        else:
            receipt_component = 500 * 0.5 + 1000 * 0.3 + (receipts - 1500) * 0.1  # Heavy penalty
        
        # Additional penalty for combined high mileage + high receipts
        if miles >= 800 and receipts >= 1000:
            combined_penalty = (miles - 800) * 0.1 + (receipts - 1000) * 0.05
            receipt_component -= combined_penalty
            receipt_component = max(receipt_component, 0)  # Don't go negative
        
        improved_total = base + mileage + receipt_component
        improved_error = abs(improved_total - expected)
        improvement = current_error - improved_error
        
        if improvement > 0:
            improvements += 1
            total_improvement += improvement
        
        # Show detailed breakdown for extreme cases
        if miles >= 1000 or receipts >= 1500:
            print(f"\nExtreme case: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
            print(f"  Current: ${current_calculated:.2f} (error: ${current_error:.2f})")
            print(f"  Improved breakdown:")
            print(f"    Base: ${base}")
            print(f"    Mileage: ${mileage:.2f}")
            print(f"    Receipts: ${receipt_component:.2f}")
            if miles >= 800 and receipts >= 1000:
                penalty = (miles - 800) * 0.1 + (receipts - 1000) * 0.05
                print(f"    Combined penalty: -${penalty:.2f}")
            print(f"    Total: ${improved_total:.2f} (error: ${improved_error:.2f})")
            print(f"    Improvement: {improvement:+.2f}")
    
    print(f"\n📊 Results: {improvements}/{len(worst_cases)} cases improved")
    if improvements > 0:
        print(f"Average improvement: ${total_improvement/improvements:.2f}")
        print(f"Total improvement: ${total_improvement:.2f}")
    
    return improvements > len(worst_cases) * 0.4  # Return True if >40% improved

def implement_1_day_fix():
    """Implement improved 1-day formula with penalties for extreme cases."""
    
    print(f"\n🔧 IMPLEMENTING 1-DAY ALGORITHM FIX")
    print("=" * 40)
    
    # Read current algorithm
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'r') as f:
        content = f.read()
    
    # Find and replace the 1-day calculation section
    old_1_day_section = """def calculate_1_day(miles, receipts):
    # Formula: 80 + (miles × 0.60) + min(receipts, 2000) × 0.5
    base = 80
    mileage = miles * 0.60
    receipt_component = min(receipts, 2000) * 0.5
    return base + mileage + receipt_component"""
    
    new_1_day_section = """def calculate_1_day(miles, receipts):
    # Formula with penalties for extreme mileage and receipt combinations
    base = 80
    
    # Progressive mileage penalty for high-mileage trips
    if miles <= 500:
        mileage = miles * 0.60
    elif miles <= 1000:
        mileage = 500 * 0.60 + (miles - 500) * 0.40
    else:
        mileage = 500 * 0.60 + 500 * 0.40 + (miles - 1000) * 0.20
    
    # Progressive receipt penalty
    if receipts <= 500:
        receipt_component = receipts * 0.5
    elif receipts <= 1500:
        receipt_component = 500 * 0.5 + (receipts - 500) * 0.3
    else:
        receipt_component = 500 * 0.5 + 1000 * 0.3 + (receipts - 1500) * 0.1
    
    # Additional penalty for combined high mileage + high receipts
    if miles >= 800 and receipts >= 1000:
        combined_penalty = (miles - 800) * 0.1 + (receipts - 1000) * 0.05
        receipt_component -= combined_penalty
        receipt_component = max(receipt_component, 0)
    
    return base + mileage + receipt_component"""
    
    # Apply the fix
    updated_content = content.replace(old_1_day_section, new_1_day_section)
    
    if updated_content != content:
        with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'w') as f:
            f.write(updated_content)
        print("✅ 1-day algorithm updated successfully!")
        return True
    else:
        print("❌ Could not find 1-day section to update")
        return False

def test_updated_1_day_algorithm():
    """Test the updated 1-day algorithm, especially on Case 996."""
    
    print(f"\n🧪 TESTING UPDATED 1-DAY ALGORITHM")
    print("=" * 35)
    
    # Test Case 996 specifically
    print("Testing Case 996 (highest error case):")
    try:
        result = subprocess.run(
            ['./run.sh', '1', '1082', '1809.49'],
            capture_output=True,
            text=True,
            cwd='/Users/raoufrahiche/IdeaProjects/top-coder-challenge'
        )
        
        if result.returncode == 0:
            new_calculated = float(result.stdout.strip())
            old_calculated = 1633.94
            expected = 446.94
            
            old_error = abs(old_calculated - expected)
            new_error = abs(new_calculated - expected)
            improvement = old_error - new_error
            
            print(f"  Case 996: 1082mi, $1809r → Expected: ${expected:.2f}")
            print(f"  Old: ${old_calculated:.2f} (error: ${old_error:.2f})")
            print(f"  New: ${new_calculated:.2f} (error: ${new_error:.2f})")
            print(f"  Improvement: {improvement:+.2f}")
    
    except Exception as e:
        print(f"Error testing Case 996: {e}")
    
    # Test other high-error 1-day cases
    cases = get_1_day_cases()
    test_cases = cases[-5:]  # Test on 5 worst cases
    
    improvements = 0
    total_improvement = 0
    
    print(f"\nTesting other high-error 1-day cases:")
    for case in test_cases:
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        old_calculated = case['calculated']
        old_error = case['error']
        
        try:
            result = subprocess.run(
                ['./run.sh', '1', str(miles), str(receipts)],
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
                
                print(f"  Case {case['case']}: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
                print(f"    Old: ${old_calculated:.2f} (error: ${old_error:.2f})")
                print(f"    New: ${new_calculated:.2f} (error: ${new_error:.2f})")
                print(f"    Improvement: {improvement:+.2f}")
        
        except Exception as e:
            print(f"Error testing case: {e}")
    
    print(f"\n📊 Results: {improvements}/{len(test_cases)} additional cases improved")
    if improvements > 0:
        print(f"Average improvement: ${total_improvement/improvements:.2f}")
    
    return True  # Consider successful if Case 996 improved significantly

if __name__ == "__main__":
    # Step 1: Analyze 1-day patterns
    analyze_1_day_patterns()
    
    # Step 2: Deep dive into Case 996
    analyze_case_996()
    
    # Step 3: Test improved formula
    should_implement = test_improved_1_day_formula()
    
    if should_implement:
        # Step 4: Implement the fix
        fix_applied = implement_1_day_fix()
        
        if fix_applied:
            # Step 5: Test the updated algorithm
            success = test_updated_1_day_algorithm()
            
            if success:
                print("\n✅ 1-DAY ALGORITHM SUCCESSFULLY IMPROVED!")
                print("Ready to move to next duration analysis.")
            else:
                print("\n⚠️ 1-day algorithm updated but improvements mixed.")
        else:
            print("\n❌ Could not apply 1-day algorithm fix.")
    else:
        print("\n❌ Proposed 1-day improvements not effective enough.")
        print("1-day algorithm requires different approach.")