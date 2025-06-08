#!/usr/bin/env python3
"""
Test legacy system corrections based on the deep analysis findings.
Focus on component-wise rounding and stricter 5-day penalties.
"""

import subprocess
import json

def run_original_algorithm(days, miles, receipts):
    """Run our current algorithm."""
    try:
        result = subprocess.run(
            ['./run.sh', str(days), str(miles), str(receipts)],
            capture_output=True,
            text=True,
            cwd='/Users/raoufrahiche/IdeaProjects/top-coder-challenge'
        )
        return float(result.stdout.strip()) if result.returncode == 0 else None
    except:
        return None

def legacy_cobol_style_calculation(days, miles, receipts):
    """
    Apply COBOL-style component-wise rounding to each calculation step.
    This addresses the 61.1% over-calculation bias.
    """
    
    def cobol_round(value):
        """COBOL rounds 0.5 up always (not banker's rounding)."""
        return round(value + 0.0000001, 2)  # Slight bias to round up
    
    if days == 1:
        base = cobol_round(80.0)
        mileage = cobol_round(miles * 0.60)
        receipt_component = cobol_round(min(receipts, 2000) * 0.5)
        return cobol_round(base + mileage + receipt_component)
    
    elif days == 2:
        base = cobol_round(170.0)
        mileage = cobol_round(miles * 0.69)
        if receipts <= 300:
            receipt_component = cobol_round(receipts)
        elif receipts <= 800:
            receipt_component = cobol_round(receipts * 0.8)
        else:
            receipt_component = cobol_round(receipts * 0.4)
        return cobol_round(base + mileage + receipt_component)
    
    elif days == 3:
        base = cobol_round(300.0)
        mileage = cobol_round(miles * 0.70)
        if receipts <= 200:
            receipt_component = cobol_round(receipts * 0.5)
        elif receipts <= 500:
            receipt_component = cobol_round(receipts * 0.4)
        elif receipts <= 1000:
            receipt_component = cobol_round(receipts * 0.3)
        elif receipts <= 1500:
            receipt_component = cobol_round(receipts * 0.25)
        else:
            receipt_component = cobol_round(receipts * 0.15)
        return cobol_round(base + mileage + receipt_component)
    
    elif days == 4:
        base = cobol_round(280.0)
        mileage = cobol_round(miles * 0.67)
        if receipts < 100:
            receipt_component = cobol_round(receipts * 0.9)
        elif receipts <= 800:
            receipt_component = cobol_round(receipts * 0.6)
        else:
            receipt_component = cobol_round(receipts * 0.4 + 160)
        return cobol_round(base + mileage + receipt_component)
    
    elif days == 5:
        # CRITICAL: More aggressive penalty for 5-day trips (81.2% over-calculation)
        base = cobol_round(450.0)
        mileage = cobol_round(miles * 0.62)
        
        if receipts < 500:
            receipt_component = cobol_round(min(receipts, 50))
        elif receipts < 1500:
            receipt_component = cobol_round(receipts * 0.70)
        else:
            # Much more aggressive penalty for high receipts
            penalty = cobol_round((receipts - 1500) * 0.4)  # Increased from 0.2
            receipt_component = cobol_round(1500 * 0.70 - penalty)
            receipt_component = max(receipt_component, 25)  # Lower floor
        
        return cobol_round(base + mileage + receipt_component)
    
    elif days in [6, 7, 8]:
        base_rates = {6: 86, 7: 73, 8: 45}
        base = cobol_round(base_rates[days] * days)
        mileage = cobol_round(miles * 0.32)
        receipt_cap = 145 * days
        receipt_component = cobol_round(min(receipts, receipt_cap))
        return cobol_round(base + mileage + receipt_component)
    
    else:  # 9+ days
        base = cobol_round(55 * days)
        mileage = cobol_round(miles * 0.67)
        
        if receipts < 200:
            receipt_component = cobol_round(receipts)
        elif receipts <= 1500:
            receipt_component = cobol_round(receipts * 0.7)
        elif receipts <= 2000:
            receipt_component = cobol_round(receipts * 0.5)
        else:
            receipt_component = cobol_round(receipts * 0.25)
        
        if days >= 10 and receipts < 100:
            penalty = cobol_round((days - 9) * 15)
            total = cobol_round(base + mileage + receipt_component - penalty)
            return max(total, days * 50)
        
        return cobol_round(base + mileage + receipt_component)

def test_legacy_corrections():
    """Test the legacy corrections on a sample of cases."""
    
    print("🔧 Testing Legacy System Corrections")
    print("=" * 40)
    
    # Load test cases
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    # Focus on cases where we over-calculate significantly
    test_cases = []
    
    # Test 5-day cases (81.2% over-calculation rate)
    five_day_cases = [case for case in public_cases if case['input']['trip_duration_days'] == 5][:10]
    test_cases.extend(five_day_cases)
    
    # Test some high-error cases from other durations
    other_cases = [case for case in public_cases if case['input']['trip_duration_days'] != 5][:10]
    test_cases.extend(other_cases)
    
    improvements = 0
    total_improvement = 0
    
    print("Testing COBOL-style component rounding and stricter 5-day penalties:\n")
    
    for i, case in enumerate(test_cases):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Get current algorithm result
        current_result = run_original_algorithm(days, miles, receipts)
        if current_result is None:
            continue
            
        # Get legacy-corrected result
        legacy_result = legacy_cobol_style_calculation(days, miles, receipts)
        
        # Calculate errors
        current_error = abs(current_result - expected)
        legacy_error = abs(legacy_result - expected)
        improvement = current_error - legacy_error
        
        if improvement > 1:
            improvements += 1
            total_improvement += improvement
            
            print(f"Case {i+1} ({days}d, {miles}mi, ${receipts:.0f}r):")
            print(f"  Expected: ${expected:.2f}")
            print(f"  Current:  ${current_result:.2f} (error: ${current_error:.2f})")
            print(f"  Legacy:   ${legacy_result:.2f} (error: ${legacy_error:.2f})")
            print(f"  Improvement: ${improvement:.2f}")
            print()
    
    print(f"📊 Results:")
    print(f"   Significant improvements: {improvements}/{len(test_cases)}")
    if improvements > 0:
        print(f"   Average improvement: ${total_improvement/improvements:.2f}")
        print(f"   Total improvement: ${total_improvement:.2f}")
    
    if improvements > len(test_cases) * 0.3:
        print("\n✅ Strong evidence for legacy system corrections!")
        print("🔧 Recommend implementing COBOL-style rounding and stricter penalties")
    elif improvements > 0:
        print("\n⚠️  Some evidence for legacy corrections")
        print("🔍 May be worth testing on full dataset")
    else:
        print("\n❌ No evidence for these specific legacy corrections")

if __name__ == "__main__":
    test_legacy_corrections()