#!/usr/bin/env python3
import json

def analyze_high_error_cases():
    """Analyze the specific high-error cases mentioned"""
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
        data = json.load(f)
    
    # The specific cases mentioned
    target_cases = [995, 683, 151, 710, 547]  # Corrected case numbers
    
    print("="*80)
    print("HIGH-ERROR CASE ANALYSIS")
    print("="*80)
    print()
    
    print("These cases have very high receipt amounts that appear to be causing large errors:")
    print()
    
    for case_idx in target_cases:
        case = data[case_idx]
        inp = case['input']
        expected = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled'] 
        receipts = inp['total_receipts_amount']
        
        print(f"Case {case_idx}: {days} days, {miles} miles, ${receipts:.2f} receipts")
        print(f"  Expected: ${expected:.2f}")
        
        # Test different formula possibilities
        print("  Analysis of different formula approaches:")
        
        # 1. Current linear formula that was being tested
        linear_result = days * 120 + miles * 0.58 + receipts * 0.0
        print(f"    Linear (120*days + 0.58*miles + 0*receipts): ${linear_result:.2f} (error: ${abs(linear_result - expected):.2f})")
        
        # 2. What if receipts have negative coefficient (penalty)?
        penalty_result = days * 120 + miles * 0.58 - receipts * 0.3
        print(f"    With receipt penalty (120*days + 0.58*miles - 0.3*receipts): ${penalty_result:.2f} (error: ${abs(penalty_result - expected):.2f})")
        
        # 3. What if there's a cap on reimbursement based on receipts?
        # If receipts > some threshold, reimbursement is capped
        base_reimbursement = days * 120 + miles * 0.58
        if receipts > 1000:  # Example threshold
            capped_result = min(base_reimbursement, expected)
            print(f"    With receipt cap (if receipts > $1000, cap reimbursement): ${capped_result:.2f}")
        
        # 4. What if the formula changes based on receipt amount?
        if receipts > 1000:
            high_receipt_result = days * 80 + miles * 0.4  # Different rates for high receipts
            print(f"    High-receipt formula (80*days + 0.4*miles): ${high_receipt_result:.2f} (error: ${abs(high_receipt_result - expected):.2f})")
        
        # 5. Reverse engineer what the multipliers would need to be
        if days > 0 and miles > 0:
            # Assuming days * D + miles * M + receipts * R = expected
            # Try different receipt coefficients and solve for D, M
            for r_coeff in [0, -0.1, -0.2, -0.3, -0.4, -0.5]:
                remaining = expected - receipts * r_coeff
                # Now we need days * D + miles * M = remaining
                # Try typical daily rate
                for daily_rate in [100, 120, 140]:
                    mile_component = remaining - days * daily_rate
                    if miles > 0:
                        mile_rate = mile_component / miles
                        if 0.2 <= mile_rate <= 1.0:  # Reasonable mileage rate
                            predicted = days * daily_rate + miles * mile_rate + receipts * r_coeff
                            error = abs(predicted - expected)
                            if error < 1.0:
                                print(f"    POTENTIAL FORMULA: {daily_rate}*days + {mile_rate:.3f}*miles + {r_coeff}*receipts = ${predicted:.2f} (error: ${error:.2f})")
        
        print()
    
    print("\n" + "="*80)
    print("PATTERN ANALYSIS")
    print("="*80)
    
    # Look for patterns in receipt handling
    print("\n1. Receipt Amount vs Expected Output Analysis:")
    print("   Looking for evidence of caps, penalties, or different treatment...")
    
    # Group all cases by receipt amount ranges
    receipt_ranges = [
        (0, 100, "Low receipts ($0-100)"),
        (100, 500, "Medium receipts ($100-500)"), 
        (500, 1000, "High receipts ($500-1000)"),
        (1000, 1500, "Very high receipts ($1000-1500)"),
        (1500, 2500, "Extremely high receipts ($1500-2500)")
    ]
    
    for min_r, max_r, label in receipt_ranges:
        cases_in_range = [c for c in data if min_r <= c['input']['total_receipts_amount'] < max_r]
        if cases_in_range:
            print(f"\n   {label}: {len(cases_in_range)} cases")
            
            # Check if receipts affect reimbursement
            receipt_higher_count = 0
            receipt_lower_count = 0
            
            for case in cases_in_range[:10]:  # Sample first 10
                inp = case['input']
                expected = case['expected_output']
                receipts = inp['total_receipts_amount']
                
                if receipts > expected:
                    receipt_higher_count += 1
                else:
                    receipt_lower_count += 1
            
            print(f"     Sample of 10 cases:")
            print(f"     - Cases where receipts > reimbursement: {receipt_higher_count}")
            print(f"     - Cases where receipts < reimbursement: {receipt_lower_count}")
            
            if receipt_higher_count > 7:  # Most cases have receipts > reimbursement
                print(f"     → Suggests reimbursement CAP for this receipt range")
            elif receipt_lower_count > 7:  # Most cases have receipts < reimbursement  
                print(f"     → Suggests full reimbursement + allowances for this range")
    
    print("\n2. High-Receipt Cases Analysis:")
    high_receipt_cases = [c for c in data if c['input']['total_receipts_amount'] > 1000]
    print(f"   Found {len(high_receipt_cases)} cases with receipts > $1000")
    
    if high_receipt_cases:
        # Check if there's a consistent pattern
        penalties = []
        for case in high_receipt_cases:
            inp = case['input']
            expected = case['expected_output']
            receipts = inp['total_receipts_amount']
            days = inp['trip_duration_days']
            miles = inp['miles_traveled']
            
            # Estimate what base reimbursement might be (days + miles allowance)
            estimated_base = days * 120 + miles * 0.58  # Using common rates
            penalty = receipts - expected
            
            if penalty > 0:  # Receipts higher than reimbursement = penalty
                penalties.append(penalty)
                
        if penalties:
            avg_penalty = sum(penalties) / len(penalties)
            max_penalty = max(penalties)
            min_penalty = min(penalties)
            print(f"   Average 'penalty' (receipts - reimbursement): ${avg_penalty:.2f}")
            print(f"   Range: ${min_penalty:.2f} to ${max_penalty:.2f}")
            
            # Check if penalty is proportional to excess receipts
            proportional_penalties = []
            for case in high_receipt_cases:
                inp = case['input']
                expected = case['expected_output']
                receipts = inp['total_receipts_amount']
                
                if receipts > expected:
                    penalty_rate = (receipts - expected) / receipts
                    proportional_penalties.append(penalty_rate)
            
            if proportional_penalties:
                avg_penalty_rate = sum(proportional_penalties) / len(proportional_penalties)
                print(f"   Average penalty rate: {avg_penalty_rate:.1%} of receipts")
    
    print("\n3. Alternative Formula Hypothesis:")
    print("   Based on the analysis, the algorithm might be:")
    print("   • Base: daily_rate * days + mileage_rate * miles")
    print("   • For high receipts: Apply penalty or cap")
    print("   • Possible formulas:")
    print("     - max(base_reimbursement, receipts * cap_factor)")
    print("     - base_reimbursement - max(0, receipts - threshold) * penalty_rate")
    print("     - Different rates entirely for high-receipt cases")

if __name__ == "__main__":
    analyze_high_error_cases()