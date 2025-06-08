#!/usr/bin/env python3

import json
import math

def calculate_reimbursement(days, miles, receipts):
    """
    Calculate reimbursement based on interview insights about the legacy system
    """
    
    # Base per diem calculation
    base_per_diem = 100.0
    total_per_diem = base_per_diem * days
    
    # Mileage calculation with tiers
    mileage_reimbursement = calculate_mileage(miles, days)
    
    # Receipt processing with caps and penalties
    receipt_reimbursement = calculate_receipts(receipts, days, miles)
    
    # Base calculation
    base_amount = total_per_diem + mileage_reimbursement + receipt_reimbursement
    
    # Apply bonuses and penalties
    final_amount = apply_bonuses_and_penalties(base_amount, days, miles, receipts)
    
    # Apply rounding quirks
    final_amount = apply_rounding_quirks(final_amount, receipts)
    
    return round(final_amount, 2)

def calculate_mileage(miles, days):
    """Calculate mileage reimbursement with tiered system"""
    if miles == 0:
        return 0.0
    
    # Base rate for first 100 miles
    base_rate = 0.58
    mileage_amount = 0.0
    
    if miles <= 100:
        mileage_amount = miles * base_rate
    else:
        # First 100 miles at full rate
        mileage_amount = 100 * base_rate
        remaining_miles = miles - 100
        
        # Tiered reduction for remaining miles
        # Based on interviews: non-linear drop-off
        if remaining_miles <= 200:
            # Second tier: slight reduction
            mileage_amount += remaining_miles * (base_rate * 0.85)
        elif remaining_miles <= 500:
            # Third tier: more reduction
            mileage_amount += 200 * (base_rate * 0.85)
            mileage_amount += (remaining_miles - 200) * (base_rate * 0.70)
        else:
            # Fourth tier: significant reduction for very high mileage
            mileage_amount += 200 * (base_rate * 0.85)
            mileage_amount += 300 * (base_rate * 0.70)
            mileage_amount += (remaining_miles - 500) * (base_rate * 0.55)
    
    # Efficiency bonus (180-220 miles per day sweet spot)
    if days > 0:
        miles_per_day = miles / days
        if 180 <= miles_per_day <= 220:
            mileage_amount *= 1.15  # 15% efficiency bonus
        elif 150 <= miles_per_day < 180 or 220 < miles_per_day <= 250:
            mileage_amount *= 1.08  # 8% moderate bonus
        elif miles_per_day > 300:
            mileage_amount *= 0.90  # Penalty for excessive daily mileage
    
    return mileage_amount

def calculate_receipts(receipts, days, miles):
    """Calculate receipt reimbursement with caps and penalties"""
    if receipts == 0:
        return 0.0
    
    # Very low receipts penalty (worse than nothing)
    if receipts < 30:
        return -20.0  # Penalty for submitting very low receipts
    elif receipts < 50:
        return receipts * 0.5  # Reduced reimbursement for low receipts
    
    # Spending per day analysis
    spending_per_day = receipts / days if days > 0 else receipts
    
    # Optimal spending ranges based on trip length
    if days <= 3:  # Short trips
        if spending_per_day > 75:
            penalty_factor = max(0.6, 1.0 - (spending_per_day - 75) * 0.01)
        else:
            penalty_factor = 1.0
    elif 4 <= days <= 6:  # Medium trips
        if spending_per_day > 120:
            penalty_factor = max(0.5, 1.0 - (spending_per_day - 120) * 0.008)
        else:
            penalty_factor = min(1.1, 1.0 + (spending_per_day - 60) * 0.002)  # Slight bonus for medium spending
    else:  # Long trips
        if spending_per_day > 90:
            penalty_factor = max(0.4, 1.0 - (spending_per_day - 90) * 0.012)  # "Vacation penalty"
        else:
            penalty_factor = 1.0
    
    # Base receipt reimbursement with diminishing returns
    if receipts <= 600:
        receipt_amount = receipts * 0.85
    elif receipts <= 1000:
        receipt_amount = 600 * 0.85 + (receipts - 600) * 0.70
    elif receipts <= 1500:
        receipt_amount = 600 * 0.85 + 400 * 0.70 + (receipts - 1000) * 0.50
    else:
        # Heavy penalty for very high receipts
        receipt_amount = 600 * 0.85 + 400 * 0.70 + 500 * 0.50 + (receipts - 1500) * 0.25
    
    # Apply spending pattern penalty/bonus
    receipt_amount *= penalty_factor
    
    # High mileage + low spending bonus
    if miles > 200 and spending_per_day < 70:
        receipt_amount *= 1.12
    
    # Low mileage + high spending penalty  
    if miles < 100 and spending_per_day > 100:
        receipt_amount *= 0.85
    
    return receipt_amount

def apply_bonuses_and_penalties(base_amount, days, miles, receipts):
    """Apply various bonuses and penalties based on trip characteristics"""
    final_amount = base_amount
    
    # 5-day trip bonus (mentioned multiple times in interviews)
    if days == 5:
        final_amount *= 1.08
    
    # Sweet spot combo: 5 days, 180+ miles/day, <$100/day spending
    if days == 5 and miles >= 900 and (receipts / days) < 100:
        final_amount *= 1.12  # Additional bonus for hitting sweet spot
    
    # 8+ day vacation penalty with high spending
    if days >= 8 and (receipts / days) > 100:
        final_amount *= 0.88
    
    # Efficiency bonuses for optimal miles per day across all trip lengths
    if days > 0:
        miles_per_day = miles / days
        if miles_per_day >= 200:
            final_amount *= 1.05
    
    # Medium trip length bonus (4-6 days mentioned as sweet spot)
    if 4 <= days <= 6:
        final_amount *= 1.03
    
    # Very short trip penalty
    if days == 1 and miles < 50:
        final_amount *= 0.95
    
    # Very long trip with reasonable spending gets slight bonus
    if days >= 10 and (receipts / days) < 80:
        final_amount *= 1.02
    
    return final_amount

def apply_rounding_quirks(amount, receipts):
    """Apply rounding bugs mentioned in interviews"""
    
    # Rounding bug: receipts ending in .49 or .99 get extra money
    receipt_cents = int((receipts * 100) % 100)
    if receipt_cents == 49 or receipt_cents == 99:
        amount += 5.00  # Extra money from rounding bug
    
    # Additional small variations to simulate system noise
    # Based on interviews about 5-10% variation for similar trips
    import hashlib
    
    # Create deterministic "randomness" based on inputs
    hash_input = f"{receipts:.2f}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
    variation = (hash_value % 1000) / 10000.0  # 0-10% variation
    
    # Apply small variation (mentioned as 5-10% for similar trips)
    if variation < 0.5:
        amount *= (1.0 + variation * 0.1)  # Up to 5% increase
    else:
        amount *= (1.0 - (variation - 0.5) * 0.1)  # Up to 5% decrease
    
    return amount

def predict_reimbursement(days, miles, receipts):
    """Main prediction function"""
    return calculate_reimbursement(days, miles, receipts)

def test_public_cases():
    """Test the rule-based system on public cases"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    total_error = 0
    exact_matches = 0
    close_matches = 0
    
    print("Testing rule-based system on public cases...")
    
    for i, case in enumerate(cases):
        input_data = case['input']
        expected = case['expected_output']
        
        predicted = predict_reimbursement(
            input_data['trip_duration_days'],
            input_data['miles_traveled'], 
            input_data['total_receipts_amount']
        )
        
        error = abs(predicted - expected)
        total_error += error
        
        if error <= 0.01:
            exact_matches += 1
        elif error <= 1.00:
            close_matches += 1
            
        if i < 10:  # Show first 10 predictions
            print(f"Case {i+1}: Expected {expected}, Got {predicted}, Error {error:.2f}")
    
    avg_error = total_error / len(cases)
    print(f"\nResults:")
    print(f"Average error: ${avg_error:.2f}")
    print(f"Exact matches (±$0.01): {exact_matches} ({exact_matches/len(cases)*100:.1f}%)")
    print(f"Close matches (±$1.00): {close_matches} ({close_matches/len(cases)*100:.1f}%)")
    print(f"Total score: {total_error:.2f}")

def generate_private_predictions():
    """Generate predictions for private cases"""
    with open('private_cases.json', 'r') as f:
        private_cases = json.load(f)
    
    predictions = []
    for case in private_cases:
        pred = predict_reimbursement(
            case['trip_duration_days'],
            case['miles_traveled'],
            case['total_receipts_amount']
        )
        predictions.append(pred)
    
    with open('private_results.txt', 'w') as f:
        for pred in predictions:
            f.write(f"{pred}\n")
    
    print(f"Generated {len(predictions)} predictions for private cases")
    print("Saved to 'private_results.txt'")

if __name__ == "__main__":
    test_public_cases()
    print()
    generate_private_predictions()