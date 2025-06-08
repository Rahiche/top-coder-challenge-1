import json

# Read the first 50 cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

cases = data[:50]

print("FORMULA DISCOVERY ANALYSIS")
print("=" * 80)

# Key observations from previous analysis:
# 1. Output seems to depend on days, miles, and receipts
# 2. Receipt contribution might be negative (see some cases where more receipts = less output)
# 3. There might be different formulas for different day ranges

# Let's test a hypothesis: The output might be inversely related to receipts
print("\n1. TESTING INVERSE RECEIPT RELATIONSHIP:")
print("-" * 60)

# Look at 5-day trips sorted by receipts
five_day = [c for c in cases if c['input']['trip_duration_days'] == 5]
five_day_sorted = sorted(five_day, key=lambda x: x['input']['total_receipts_amount'])

print("5-day trips sorted by receipts:")
for c in five_day_sorted[:10]:
    inp = c['input']
    out = c['expected_output']
    # Calculate a "base" excluding receipts
    base_plus_miles = out + inp['total_receipts_amount']
    per_mile = base_plus_miles / inp['miles_traveled'] if inp['miles_traveled'] > 0 else 0
    
    print(f"  {inp['miles_traveled']} mi, ${inp['total_receipts_amount']:.2f} receipts -> ${out:.2f}")
    print(f"    Output + Receipts = ${base_plus_miles:.2f} (${per_mile:.2f}/mile)")

# Test formula: output = base_per_day * days + mile_rate * miles - receipt_penalty * receipts
print("\n2. TESTING FORMULA WITH RECEIPT PENALTY:")
print("-" * 60)

# Try different coefficients
best_formula = None
best_error = float('inf')

for base_per_day in range(50, 150, 10):
    for mile_rate in [0.5, 0.75, 1.0, 1.25, 1.5]:
        for receipt_penalty in [0, 0.25, 0.5, 0.75, 1.0]:
            errors = []
            
            for case in cases[:20]:  # Test on first 20 cases
                inp = case['input']
                predicted = (base_per_day * inp['trip_duration_days'] + 
                           mile_rate * inp['miles_traveled'] - 
                           receipt_penalty * inp['total_receipts_amount'])
                actual = case['expected_output']
                error = abs(predicted - actual)
                errors.append(error)
            
            avg_error = sum(errors) / len(errors)
            
            if avg_error < best_error:
                best_error = avg_error
                best_formula = (base_per_day, mile_rate, receipt_penalty)
                
                if avg_error < 30:  # Good fit
                    print(f"\nPotential formula: ${base_per_day}/day + ${mile_rate}/mile - ${receipt_penalty}x receipts")
                    print(f"Average error: ${avg_error:.2f}")
                    
                    # Show examples
                    for i in range(5):
                        case = cases[i]
                        inp = case['input']
                        predicted = (base_per_day * inp['trip_duration_days'] + 
                                   mile_rate * inp['miles_traveled'] - 
                                   receipt_penalty * inp['total_receipts_amount'])
                        actual = case['expected_output']
                        print(f"  Case {i+1}: {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f} -> ")
                        print(f"    Predicted: ${predicted:.2f}, Actual: ${actual:.2f}, Error: ${abs(predicted-actual):.2f}")

print(f"\nBest formula found: ${best_formula[0]}/day + ${best_formula[1]}/mile - ${best_formula[2]}x receipts")
print(f"Average error: ${best_error:.2f}")

# Look for patterns by trip duration
print("\n3. CHECKING IF FORMULA VARIES BY TRIP DURATION:")
print("-" * 60)

for days in [1, 2, 3, 5]:
    day_cases = [c for c in cases if c['input']['trip_duration_days'] == days]
    if len(day_cases) < 3:
        continue
        
    print(f"\n{days}-day trips:")
    
    # For each trip duration, try to find the best formula
    best_day_formula = None
    best_day_error = float('inf')
    
    for base_per_day in range(50, 150, 10):
        for mile_rate in [0.5, 0.75, 1.0, 1.25, 1.5]:
            for receipt_penalty in [0, 0.25, 0.5, 0.75, 1.0]:
                errors = []
                
                for case in day_cases:
                    inp = case['input']
                    predicted = (base_per_day * inp['trip_duration_days'] + 
                               mile_rate * inp['miles_traveled'] - 
                               receipt_penalty * inp['total_receipts_amount'])
                    actual = case['expected_output']
                    error = abs(predicted - actual)
                    errors.append(error)
                
                avg_error = sum(errors) / len(errors)
                
                if avg_error < best_day_error:
                    best_day_error = avg_error
                    best_day_formula = (base_per_day, mile_rate, receipt_penalty)
    
    print(f"  Best formula: ${best_day_formula[0]}/day + ${best_day_formula[1]}/mile - ${best_day_formula[2]}x receipts")
    print(f"  Average error: ${best_day_error:.2f}")
    
    # Show examples with this formula
    for i in range(min(3, len(day_cases))):
        case = day_cases[i]
        inp = case['input']
        predicted = (best_day_formula[0] * inp['trip_duration_days'] + 
                   best_day_formula[1] * inp['miles_traveled'] - 
                   best_day_formula[2] * inp['total_receipts_amount'])
        actual = case['expected_output']
        print(f"    {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f} -> Predicted: ${predicted:.2f}, Actual: ${actual:.2f}")

# Check if there's a minimum threshold
print("\n4. CHECKING FOR MINIMUM THRESHOLDS:")
print("-" * 60)

# Look at cases with very low predicted values
for case in cases[:30]:
    inp = case['input']
    basic_calc = 100 * inp['trip_duration_days'] + 1.0 * inp['miles_traveled'] - 0.5 * inp['total_receipts_amount']
    actual = case['expected_output']
    
    if basic_calc < actual - 50:  # If basic calc is much lower than actual
        print(f"{inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f}:")
        print(f"  Basic calc: ${basic_calc:.2f}, Actual: ${actual:.2f}")
        print(f"  Difference: ${actual - basic_calc:.2f}")
        
        # Check if there's a minimum per day
        min_per_day = actual / inp['trip_duration_days']
        print(f"  Actual per day: ${min_per_day:.2f}")