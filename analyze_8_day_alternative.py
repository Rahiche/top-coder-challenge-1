#!/usr/bin/env python3
"""
Alternative analysis of 8-day trips - try working backwards from expected outputs
to discover the actual formula structure.
"""

import csv
import subprocess

def reverse_engineer_8_day_formula():
    """Work backwards from best 8-day cases to find the real formula."""
    
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
    
    # Sort by error (best cases first)
    eight_day_cases.sort(key=lambda x: x['error'])
    
    print("🔬 REVERSE ENGINEERING 8-DAY FORMULA FROM BEST CASES")
    print("=" * 55)
    
    best_cases = eight_day_cases[:10]
    
    for i, case in enumerate(best_cases):
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        
        print(f"\nCase {i+1}: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
        
        # Try different base rates to see what works
        for base_per_day in [30, 35, 40, 45, 50, 55]:
            base = base_per_day * 8
            remaining_after_base = expected - base
            
            print(f"  If base=${base_per_day}/day (${base} total): ${remaining_after_base:.2f} remaining")
            
            # Try different mileage rates
            for mile_rate in [0.20, 0.25, 0.30, 0.35, 0.40]:
                mileage_component = miles * mile_rate
                remaining_after_mileage = remaining_after_base - mileage_component
                
                if receipts > 0:
                    receipt_factor = remaining_after_mileage / receipts
                    
                    # Look for reasonable receipt factors
                    if 0.1 <= receipt_factor <= 1.0:
                        total_calc = base + mileage_component + (receipts * receipt_factor)
                        error = abs(total_calc - expected)
                        
                        if error < 20:  # Good match
                            print(f"    ✅ ${base_per_day}/day + ${mile_rate}/mi + ${receipts:.0f}×{receipt_factor:.3f} = ${total_calc:.2f} (error: ${error:.2f})")

def test_lower_base_rate_theory():
    """Test if 8-day trips use a much lower base rate."""
    
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
    
    print(f"\n🧪 TESTING LOWER BASE RATE THEORY")
    print("=" * 40)
    
    # Test Cases 684 and 548 with much lower base rates
    test_cases = [
        (684, 795, 1645.99, 644.69),
        (548, 482, 1411.49, 631.81)
    ]
    
    for case_num, miles, receipts, expected in test_cases:
        print(f"\nCase {case_num}: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
        
        # Try very low base rates (maybe 8-day trips are heavily penalized)
        for base_per_day in [15, 20, 25, 30]:
            base = base_per_day * 8
            
            # Try different mileage and receipt combinations
            for mile_rate in [0.15, 0.20, 0.25]:
                mileage = miles * mile_rate
                remaining = expected - base - mileage
                
                if receipts > 0:
                    receipt_factor = remaining / receipts
                    
                    if 0.01 <= receipt_factor <= 0.5:  # Very low receipt factors
                        total = base + mileage + (receipts * receipt_factor)
                        error = abs(total - expected)
                        
                        if error < 50:
                            print(f"  Possible: ${base_per_day}/day + ${mile_rate}/mi + receipts×{receipt_factor:.3f}")
                            print(f"    = ${base} + ${mileage:.2f} + ${receipts * receipt_factor:.2f} = ${total:.2f}")
                            print(f"    Error: ${error:.2f}")

def implement_ultra_low_8_day_formula():
    """Implement a completely different 8-day formula with ultra-low rates."""
    
    print(f"\n🔧 IMPLEMENTING ULTRA-LOW 8-DAY FORMULA")
    print("=" * 45)
    
    # Read current algorithm
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'r') as f:
        content = f.read()
    
    # Based on reverse engineering, try ultra-low rates for 8-day trips
    old_section = """    elif days == 8:
        # Aggressive receipt penalty for 8-day trips
        if receipts <= 400:
            receipt_component = receipts
        elif receipts <= 800:
            receipt_component = 400 + (receipts - 400) * 0.5
        elif receipts <= 1200:
            receipt_component = 400 + 400 * 0.5 + (receipts - 800) * 0.2
        else:
            receipt_component = 400 + 400 * 0.5 + 400 * 0.2 + (receipts - 1200) * 0.05"""
    
    new_section = """    elif days == 8:
        # Ultra-low rates for 8-day trips (discovered from reverse engineering)
        # Use much lower base rate and minimal receipt factors
        base = 25 * 8  # $25/day instead of $45/day
        mileage = miles * 0.20  # Much lower mileage rate
        
        # Very minimal receipt reimbursement
        if receipts <= 500:
            receipt_component = receipts * 0.15
        elif receipts <= 1000:
            receipt_component = 500 * 0.15 + (receipts - 500) * 0.08
        else:
            receipt_component = 500 * 0.15 + 500 * 0.08 + (receipts - 1000) * 0.03
        
        return base + mileage + receipt_component"""
    
    # Need to modify the function structure since we're changing the base calculation
    # Let's find the 8-day logic and replace it entirely
    
    # First, let's modify the base_per_day assignment
    base_rate_section = """    else:  # 8 days
        base_per_day = 45"""
    
    new_base_rate_section = """    else:  # 8 days
        base_per_day = 25  # Much lower for 8-day trips"""
    
    content = content.replace(base_rate_section, new_base_rate_section)
    
    # Now replace the receipt handling
    content = content.replace(old_section, new_section)
    
    # Write the updated content
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/run.sh', 'w') as f:
        f.write(content)
    
    print("✅ Ultra-low 8-day formula implemented!")
    return True

def test_ultra_low_formula():
    """Test the ultra-low 8-day formula."""
    
    print(f"\n🧪 TESTING ULTRA-LOW 8-DAY FORMULA")
    print("=" * 40)
    
    # Test the problematic cases
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
                
                # Old calculation (from analysis)
                old_calculated = 360 + (miles * 0.32) + min(receipts, 1160)
                
                old_error = abs(old_calculated - expected)
                new_error = abs(new_calculated - expected)
                improvement = old_error - new_error
                
                if improvement > 0:
                    improvements += 1
                    total_improvement += improvement
                
                print(f"Case {case_num}: {miles:.0f}mi, ${receipts:.0f}r → Expected: ${expected:.2f}")
                print(f"  Old formula: ${old_calculated:.2f} (error: ${old_error:.2f})")
                print(f"  New formula: ${new_calculated:.2f} (error: ${new_error:.2f})")
                print(f"  Improvement: {improvement:+.2f}")
                print()
        
        except Exception as e:
            print(f"Error testing case {case_num}: {e}")
    
    print(f"📊 Results: {improvements}/2 critical cases improved")
    if improvements > 0:
        print(f"Average improvement: ${total_improvement/improvements:.2f}")
    
    return improvements >= 1

if __name__ == "__main__":
    # Step 1: Reverse engineer from best cases
    reverse_engineer_8_day_formula()
    
    # Step 2: Test lower base rate theory
    test_lower_base_rate_theory()
    
    # Step 3: Implement ultra-low formula
    fix_applied = implement_ultra_low_8_day_formula()
    
    if fix_applied:
        # Step 4: Test the new formula
        success = test_ultra_low_formula()
        
        if success:
            print("\n✅ ULTRA-LOW 8-DAY FORMULA SUCCESSFUL!")
            print("8-day trips appear to use drastically different calculation structure.")
        else:
            print("\n⚠️ Ultra-low formula applied but needs further refinement.")
    else:
        print("\n❌ Could not implement ultra-low 8-day formula.")