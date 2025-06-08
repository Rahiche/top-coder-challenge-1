#!/usr/bin/env python3
import json

def analyze_receipt_penalty_pattern():
    """Analyze the exact pattern for high-receipt cases"""
    
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
        data = json.load(f)
    
    print("="*80)
    print("RECEIPT PENALTY PATTERN ANALYSIS")
    print("="*80)
    
    # Focus on cases where receipts > expected (indicating a penalty/cap)
    penalty_cases = []
    for i, case in enumerate(data):
        inp = case['input']
        expected = case['expected_output']
        receipts = inp['total_receipts_amount']
        
        if receipts > expected:
            penalty_cases.append((i, case))
    
    print(f"Found {len(penalty_cases)} cases where receipts > reimbursement")
    print()
    
    # Test different penalty formulas on these cases
    print("Testing penalty formulas on high-receipt cases:")
    print()
    
    # Test the specific high-error cases first
    target_cases = [995, 683, 151, 710, 547]
    
    print("HIGH-ERROR CASES ANALYSIS:")
    for case_idx in target_cases:
        case = data[case_idx]
        inp = case['input']
        expected = case['expected_output']
        
        days = inp['trip_duration_days']
        miles = inp['miles_traveled'] 
        receipts = inp['total_receipts_amount']
        
        print(f"\nCase {case_idx}: {days} days, {miles} miles, ${receipts:.2f} receipts → ${expected:.2f}")
        
        # Test formula: base_reimbursement - penalty_factor * (receipts - threshold)
        # Where base = daily_rate * days + mileage_rate * miles
        
        for daily_rate in [100, 110, 120, 130]:
            for mileage_rate in [0.55, 0.56, 0.57, 0.58, 0.59, 0.60]:
                base_reimbursement = daily_rate * days + mileage_rate * miles
                
                # Test different thresholds and penalty factors
                for threshold in [500, 600, 700, 800, 900, 1000]:
                    if receipts > threshold:
                        excess = receipts - threshold
                        for penalty_factor in [0.3, 0.4, 0.5, 0.6, 0.7]:
                            penalty = excess * penalty_factor
                            final_reimbursement = base_reimbursement - penalty
                            error = abs(final_reimbursement - expected)
                            
                            if error < 1.0:  # Close match
                                print(f"  MATCH: ${daily_rate}*days + ${mileage_rate}*miles - {penalty_factor}*(receipts-{threshold}) = ${final_reimbursement:.2f} (error: ${error:.2f})")
        
        # Also test max cap formula: min(base_reimbursement, cap_amount)
        for daily_rate in [100, 110, 120, 130]:
            for mileage_rate in [0.55, 0.56, 0.57, 0.58, 0.59, 0.60]:
                base_reimbursement = daily_rate * days + mileage_rate * miles
                
                # Test if it's capped at a fraction of receipts
                for cap_factor in [0.2, 0.25, 0.3, 0.35, 0.4, 0.5]:
                    cap = receipts * cap_factor
                    capped_reimbursement = min(base_reimbursement, cap)
                    error = abs(capped_reimbursement - expected)
                    
                    if error < 1.0:
                        print(f"  CAP MATCH: min(${daily_rate}*days + ${mileage_rate}*miles, {cap_factor}*receipts) = ${capped_reimbursement:.2f} (error: ${error:.2f})")
    
    print("\n" + "="*80)
    print("COMPREHENSIVE PENALTY FORMULA TESTING")
    print("="*80)
    
    # Test on all penalty cases to find consistent pattern
    best_formulas = []
    
    for daily_rate in [100, 110, 120, 130]:
        for mileage_rate in [0.55, 0.56, 0.57, 0.58, 0.59, 0.60]:
            for penalty_factor in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
                for threshold in [500, 600, 700, 800, 900, 1000]:
                    
                    total_error = 0
                    exact_matches = 0
                    close_matches = 0
                    
                    for case_idx, case in penalty_cases[:50]:  # Test on first 50 penalty cases
                        inp = case['input']
                        expected = case['expected_output']
                        
                        days = inp['trip_duration_days']
                        miles = inp['miles_traveled'] 
                        receipts = inp['total_receipts_amount']
                        
                        base_reimbursement = daily_rate * days + mileage_rate * miles
                        
                        if receipts > threshold:
                            excess = receipts - threshold
                            penalty = excess * penalty_factor
                            final_reimbursement = base_reimbursement - penalty
                        else:
                            final_reimbursement = base_reimbursement
                        
                        error = abs(final_reimbursement - expected)
                        total_error += error
                        
                        if error < 0.01:
                            exact_matches += 1
                        elif error < 1.0:
                            close_matches += 1
                    
                    avg_error = total_error / len(penalty_cases[:50])
                    
                    if exact_matches > 0 or (close_matches > 10 and avg_error < 50):
                        best_formulas.append((
                            daily_rate, mileage_rate, penalty_factor, threshold,
                            exact_matches, close_matches, avg_error
                        ))
    
    # Sort by exact matches, then by close matches, then by average error
    best_formulas.sort(key=lambda x: (-x[4], -x[5], x[6]))
    
    print("Best penalty formulas found:")
    for i, (daily, mileage, penalty, threshold, exact, close, avg_err) in enumerate(best_formulas[:10]):
        print(f"{i+1}. ${daily}*days + ${mileage}*miles - {penalty}*(max(0, receipts-{threshold}))")
        print(f"   Exact matches: {exact}, Close matches: {close}, Avg error: ${avg_err:.2f}")
        print()
    
    # Test cap formulas too
    print("="*40)
    print("TESTING CAP FORMULAS")
    print("="*40)
    
    best_cap_formulas = []
    
    for daily_rate in [100, 110, 120, 130]:
        for mileage_rate in [0.55, 0.56, 0.57, 0.58, 0.59, 0.60]:
            for cap_factor in [0.2, 0.25, 0.3, 0.35, 0.4, 0.5]:
                
                total_error = 0
                exact_matches = 0
                close_matches = 0
                
                for case_idx, case in penalty_cases[:50]:
                    inp = case['input']
                    expected = case['expected_output']
                    
                    days = inp['trip_duration_days']
                    miles = inp['miles_traveled'] 
                    receipts = inp['total_receipts_amount']
                    
                    base_reimbursement = daily_rate * days + mileage_rate * miles
                    cap = receipts * cap_factor
                    final_reimbursement = min(base_reimbursement, cap)
                    
                    error = abs(final_reimbursement - expected)
                    total_error += error
                    
                    if error < 0.01:
                        exact_matches += 1
                    elif error < 1.0:
                        close_matches += 1
                
                avg_error = total_error / len(penalty_cases[:50])
                
                if exact_matches > 0 or (close_matches > 10 and avg_error < 50):
                    best_cap_formulas.append((
                        daily_rate, mileage_rate, cap_factor,
                        exact_matches, close_matches, avg_error
                    ))
    
    best_cap_formulas.sort(key=lambda x: (-x[3], -x[4], x[5]))
    
    print("Best cap formulas found:")
    for i, (daily, mileage, cap_factor, exact, close, avg_err) in enumerate(best_cap_formulas[:10]):
        print(f"{i+1}. min(${daily}*days + ${mileage}*miles, {cap_factor}*receipts)")
        print(f"   Exact matches: {exact}, Close matches: {close}, Avg error: ${avg_err:.2f}")
        print()

if __name__ == "__main__":
    analyze_receipt_penalty_pattern()