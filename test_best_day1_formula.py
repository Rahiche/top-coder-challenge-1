#!/usr/bin/env python3
"""
Test the best formulas found and implement the most promising one
"""

import json

# Read public cases
with open('public_cases.json', 'r') as f:
    public_cases = json.load(f)

# Get day 1 cases
day1_cases = []
for i, case in enumerate(public_cases):
    if case['input']['trip_duration_days'] == 1:
        day1_cases.append({
            'case': i + 1,
            'miles': case['input']['miles_traveled'],
            'receipts': case['input']['total_receipts_amount'],
            'expected': case['expected_output']
        })

def test_formula(base, m_coeff, r_coeff, name):
    """Test a specific formula"""
    errors = []
    perfect_matches = 0
    close_matches = 0
    very_close_matches = 0  # within $5
    
    worst_cases = []
    
    for case in day1_cases:
        calculated = base + case['miles'] * m_coeff + case['receipts'] * r_coeff
        error = abs(calculated - case['expected'])
        errors.append(error)
        
        if error <= 0.01:
            perfect_matches += 1
        elif error <= 1.0:
            close_matches += 1
        elif error <= 5.0:
            very_close_matches += 1
        
        worst_cases.append({
            'case': case['case'],
            'miles': case['miles'],
            'receipts': case['receipts'],
            'expected': case['expected'],
            'calculated': calculated,
            'error': error
        })
    
    # Sort by error to see worst cases
    worst_cases.sort(key=lambda x: x['error'], reverse=True)
    
    avg_error = sum(errors) / len(errors)
    max_error = max(errors)
    
    print(f"\n{name}: ${base} + {m_coeff:.3f}*miles + {r_coeff:.3f}*receipts")
    print(f"  Average error: ${avg_error:.2f}")
    print(f"  Max error: ${max_error:.2f}")
    print(f"  Perfect matches (≤$0.01): {perfect_matches} ({perfect_matches/len(day1_cases)*100:.1f}%)")
    print(f"  Close matches (≤$1.00): {close_matches} ({close_matches/len(day1_cases)*100:.1f}%)")
    print(f"  Very close (≤$5.00): {very_close_matches} ({very_close_matches/len(day1_cases)*100:.1f}%)")
    
    # Show worst 5 cases
    print(f"  Worst 5 cases:")
    for i, case in enumerate(worst_cases[:5]):
        print(f"    {i+1}. Case {case['case']}: {case['miles']:.0f}mi, ${case['receipts']:.0f}r → Expected: ${case['expected']:.2f}, Got: ${case['calculated']:.2f}, Error: ${case['error']:.2f}")
    
    return avg_error, perfect_matches, close_matches, very_close_matches

# Test the top formulas found
print("Testing top formulas from brute force search:")
print("=" * 70)

top_formulas = [
    (95, 0.400, 0.550, "Formula 1 (Best from search)"),
    (130, 0.450, 0.550, "Formula 2"),
    (135, 0.300, 0.500, "Formula 3"),
    (10, 0.700, 0.450, "Formula 4"),
    (45, 0.500, 0.600, "Formula 5"),
]

best_formula = None
best_score = -1

for base, m_coeff, r_coeff, name in top_formulas:
    avg_error, perfect, close, very_close = test_formula(base, m_coeff, r_coeff, name)
    
    # Score formula: prioritize perfect matches, then close matches, then low average error
    score = perfect * 1000 + close * 100 + very_close * 10 - avg_error
    
    if score > best_score:
        best_score = score
        best_formula = (base, m_coeff, r_coeff, name)

print(f"\n" + "=" * 70)
print(f"BEST FORMULA: {best_formula[3]}")
print(f"${best_formula[0]} + {best_formula[1]:.3f}*miles + {best_formula[2]:.3f}*receipts")

# Let's try to improve this further with small adjustments
print(f"\n" + "=" * 70)
print("FINE-TUNING THE BEST FORMULA")

base_best, m_best, r_best, _ = best_formula

# Try small variations around the best formula
variations = []
for base_adj in [-5, 0, 5]:
    for m_adj in [-0.01, 0, 0.01, 0.02]:
        for r_adj in [-0.02, -0.01, 0, 0.01, 0.02]:
            new_base = base_best + base_adj
            new_m = m_best + m_adj  
            new_r = r_best + r_adj
            
            if new_base >= 0 and new_m >= 0 and new_r >= 0:  # Keep coefficients non-negative
                variations.append((new_base, new_m, new_r))

print(f"Testing {len(variations)} variations...")

best_variation = None
best_variation_score = -1

for base, m_coeff, r_coeff in variations[:50]:  # Test first 50 to avoid too much output
    errors = []
    perfect_matches = 0
    close_matches = 0
    very_close_matches = 0
    
    for case in day1_cases:
        calculated = base + case['miles'] * m_coeff + case['receipts'] * r_coeff
        error = abs(calculated - case['expected'])
        errors.append(error)
        
        if error <= 0.01:
            perfect_matches += 1
        elif error <= 1.0:
            close_matches += 1
        elif error <= 5.0:
            very_close_matches += 1
    
    avg_error = sum(errors) / len(errors)
    score = perfect_matches * 1000 + close_matches * 100 + very_close_matches * 10 - avg_error
    
    if score > best_variation_score:
        best_variation_score = score
        best_variation = (base, m_coeff, r_coeff, perfect_matches, close_matches, avg_error)

if best_variation:
    base, m_coeff, r_coeff, perfect, close, avg_err = best_variation
    print(f"\nIMPROVED FORMULA: ${base} + {m_coeff:.3f}*miles + {r_coeff:.3f}*receipts")
    print(f"Perfect matches: {perfect}, Close matches: {close}, Avg error: ${avg_err:.2f}")
    
    # This is our final formula to implement
    final_formula = (base, m_coeff, r_coeff)
else:
    final_formula = (base_best, m_best, r_best)

print(f"\nFINAL FORMULA TO IMPLEMENT:")
print(f"${final_formula[0]} + {final_formula[1]:.3f} * miles + {final_formula[2]:.3f} * receipts")

# Save this formula
with open('best_day1_formula.txt', 'w') as f:
    f.write(f"{final_formula[0]} {final_formula[1]:.3f} {final_formula[2]:.3f}")
print("Formula saved to best_day1_formula.txt")