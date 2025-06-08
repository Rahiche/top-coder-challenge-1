#!/usr/bin/env python3
"""
Deep analysis of 5-day trip cases - our 2nd best performing duration.
Focus on the $500 threshold system and high-receipt penalties.
"""

import csv
import subprocess

def get_5_day_cases():
    """Get all 5-day cases sorted by error."""
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    five_day_cases = []
    for row in data:
        if int(row['trip_duration_days']) == 5:
            five_day_cases.append({
                'case': int(row['case_number']),
                'miles': float(row['miles_traveled']),
                'receipts': float(row['total_receipts_amount']),
                'expected': float(row['expected_output']),
                'calculated': float(row['algorithm_result']),
                'error': float(row['absolute_error'])
            })
    
    return sorted(five_day_cases, key=lambda x: x['error'])

def analyze_5_day_threshold_system():
    """Analyze the $500 threshold system in 5-day trips."""
    
    cases = get_5_day_cases()
    print("🔍 ANALYZING 5-DAY THRESHOLD SYSTEM")
    print("=" * 45)
    
    # Separate cases by receipt amount around $500 threshold
    low_receipt_cases = [c for c in cases if c['receipts'] < 500]
    medium_receipt_cases = [c for c in cases if 500 <= c['receipts'] < 1500]
    high_receipt_cases = [c for c in cases if c['receipts'] >= 1500]
    
    print(f"Receipt distribution:")
    print(f"  < $500 (penalty zone): {len(low_receipt_cases)} cases")
    print(f"  $500-1500 (bonus zone): {len(medium_receipt_cases)} cases")
    print(f"  ≥ $1500 (high penalty): {len(high_receipt_cases)} cases")
    
    # Analyze each group
    for group_name, group_cases in [
        ("LOW RECEIPTS (<$500)", low_receipt_cases),
        ("MEDIUM RECEIPTS ($500-1500)", medium_receipt_cases),
        ("HIGH RECEIPTS (≥$1500)", high_receipt_cases)
    ]:
        if not group_cases:
            continue
            
        print(f"\n📊 {group_name}:")
        avg_error = sum(c['error'] for c in group_cases) / len(group_cases)
        over_calc = sum(1 for c in group_cases if c['calculated'] > c['expected'])
        
        print(f"   Cases: {len(group_cases)}")
        print(f"   Average error: ${avg_error:.2f}")
        print(f"   Over-calculated: {over_calc}/{len(group_cases)} ({over_calc/len(group_cases)*100:.1f}%)")
        
        # Show worst cases in each group
        worst_cases = sorted(group_cases, key=lambda x: x['error'], reverse=True)[:3]
        print(f"   Worst cases:")
        for i, case in enumerate(worst_cases):
            print(f"     {i+1}. {case['miles']:.0f}mi, ${case['receipts']:.0f}r → "
                  f"Expected: ${case['expected']:.2f}, Got: ${case['calculated']:.2f}, "
                  f"Error: ${case['error']:.2f}")

def analyze_best_5_day_cases():
    """Deep dive into best 5-day cases."""
    
    cases = get_5_day_cases()
    best_cases = cases[:10]
    
    print(f"\n🎯 BEST 5-DAY CASES ANALYSIS")
    print("=" * 35)
    
    for i, case in enumerate(best_cases):
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        calculated = case['calculated']
        error = case['error']
        
        print(f"\nCase {i+1}: {miles:.0f}mi, ${receipts:.0f}r")
        print(f"  Expected: ${expected:.2f}, Got: ${calculated:.2f}, Error: ${error:.2f}")
        
        # Current algorithm breakdown
        base = 450  # 5 * 90
        mileage = miles * 0.62
        
        if receipts < 500:
            receipt_component = min(receipts, 50)
            zone = "PENALTY"
        elif receipts < 1500:
            receipt_component = receipts * 0.70
            zone = "BONUS"
        else:
            receipt_component = 1500 * 0.70 - (receipts - 1500) * 0.2
            receipt_component = max(receipt_component, 50)
            zone = "HIGH PENALTY"
        
        current_total = base + mileage + receipt_component
        
        print(f"  Zone: {zone}")
        print(f"  Breakdown: ${base} + ${mileage:.2f} + ${receipt_component:.2f} = ${current_total:.2f}")
        
        # What would the receipt factor need to be for perfect accuracy?
        remaining_after_base_mileage = expected - base - mileage
        if receipts > 0:
            perfect_receipt_factor = remaining_after_base_mileage / receipts
            print(f"  Perfect receipt factor would be: {perfect_receipt_factor:.3f}")

def test_improved_5_day_penalties():
    """Test more aggressive penalties for high-receipt 5-day cases."""
    
    cases = get_5_day_cases()
    worst_cases = cases[-15:]  # Test on 15 worst cases
    
    print(f"\n🔧 TESTING IMPROVED 5-DAY PENALTIES")
    print("=" * 40)
    
    improvements = 0
    total_improvement = 0
    
    for case in worst_cases:
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        current_error = case['error']
        current_calculated = case['calculated']
        
        # Test more aggressive penalty system
        base = 450
        mileage = miles * 0.62
        
        if receipts < 500:
            # Keep current penalty system
            receipt_component = min(receipts, 50)
        elif receipts < 1200:  # Reduced upper bound
            # Slightly less generous bonus
            receipt_component = receipts * 0.65  # Reduced from 0.70
        elif receipts < 1800:  # New tier
            # Moderate penalty
            receipt_component = 1200 * 0.65 - (receipts - 1200) * 0.3
        else:
            # Very aggressive penalty for very high receipts
            receipt_component = 1200 * 0.65 - 600 * 0.3 - (receipts - 1800) * 0.6
            receipt_component = max(receipt_component, 25)  # Lower floor
        
        improved_total = base + mileage + receipt_component
        improved_error = abs(improved_total - expected)
        improvement = current_error - improved_error
        
        if improvement > 0:
            improvements += 1
            total_improvement += improvement
        
        print(f"Case: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
        print(f"  Current: ${current_calculated:.2f} (error: ${current_error:.2f})")
        print(f"  Improved: ${improved_total:.2f} (error: ${improved_error:.2f})")
        print(f"  Change: {improvement:+.2f}")
        print()
    
    print(f"📊 Results: {improvements}/{len(worst_cases)} cases improved")
    if improvements > 0:
        print(f"Average improvement: ${total_improvement/improvements:.2f}")
        print(f"Total improvement: ${total_improvement:.2f}")
    
    return improvements > len(worst_cases) * 0.4  # Return True if >40% improved

def implement_5_day_fix():
    """Implement improved 5-day penalties."""
    
    print(f"\n🔧 IMPLEMENTING 5-DAY ALGORITHM FIX")
    print("=" * 40)
    
    # Read current algorithm
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'r') as f:
        content = f.read()
    
    # Find and replace the 5-day calculation section
    old_5_day_section = """def calculate_5_day(miles, receipts):
    # CRITICAL: 5-day bonus/penalty system with $500 threshold
    base = 450  # 5 * 90
    mileage = miles * 0.62
    
    if receipts < 500:
        # Penalty case: receipts capped at $50
        receipt_component = min(receipts, 50)
    elif receipts < 1500:
        # Bonus case: 70% of receipts for moderate amounts
        receipt_component = receipts * 0.70
    else:
        # Very high receipts get penalized - may even go negative
        receipt_component = 1500 * 0.70 - (receipts - 1500) * 0.2
        receipt_component = max(receipt_component, 50)  # minimum floor
    
    return base + mileage + receipt_component"""
    
    new_5_day_section = """def calculate_5_day(miles, receipts):
    # CRITICAL: 5-day bonus/penalty system with improved thresholds
    base = 450  # 5 * 90
    mileage = miles * 0.62
    
    if receipts < 500:
        # Penalty case: receipts capped at $50
        receipt_component = min(receipts, 50)
    elif receipts < 1200:  # Reduced upper bound for bonus
        # Slightly less generous bonus
        receipt_component = receipts * 0.65  # Reduced from 0.70
    elif receipts < 1800:  # New intermediate tier
        # Moderate penalty for high receipts
        receipt_component = 1200 * 0.65 - (receipts - 1200) * 0.3
    else:
        # Very aggressive penalty for very high receipts
        receipt_component = 1200 * 0.65 - 600 * 0.3 - (receipts - 1800) * 0.6
        receipt_component = max(receipt_component, 25)  # Lower floor
    
    return base + mileage + receipt_component"""
    
    # Apply the fix
    updated_content = content.replace(old_5_day_section, new_5_day_section)
    
    if updated_content != content:
        with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'w') as f:
            f.write(updated_content)
        print("✅ 5-day algorithm updated successfully!")
        return True
    else:
        print("❌ Could not find 5-day section to update")
        return False

def test_updated_5_day_algorithm():
    """Test the updated 5-day algorithm."""
    
    print(f"\n🧪 TESTING UPDATED 5-DAY ALGORITHM")
    print("=" * 35)
    
    cases = get_5_day_cases()
    test_cases = cases[-10:]  # Test on 10 worst cases
    
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
                ['./run.sh', '5', str(miles), str(receipts)],
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
    
    print(f"📊 Results: {improvements}/{len(test_cases)} test cases improved")
    if improvements > 0:
        print(f"Average improvement: ${total_improvement/improvements:.2f}")
    
    return improvements >= len(test_cases) * 0.5  # Return True if ≥50% improved

if __name__ == "__main__":
    # Step 1: Analyze the threshold system
    analyze_5_day_threshold_system()
    
    # Step 2: Analyze best cases
    analyze_best_5_day_cases()
    
    # Step 3: Test improved penalties
    should_implement = test_improved_5_day_penalties()
    
    if should_implement:
        # Step 4: Implement the fix
        fix_applied = implement_5_day_fix()
        
        if fix_applied:
            # Step 5: Test the updated algorithm
            success = test_updated_5_day_algorithm()
            
            if success:
                print("\n✅ 5-DAY ALGORITHM SUCCESSFULLY IMPROVED!")
                print("Ready to move to next duration analysis.")
            else:
                print("\n⚠️ 5-day algorithm updated but improvements mixed.")
        else:
            print("\n❌ Could not apply 5-day algorithm fix.")
    else:
        print("\n❌ Proposed 5-day improvements not effective enough.")
        print("5-day algorithm requires different approach.")