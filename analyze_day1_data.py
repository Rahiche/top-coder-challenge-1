#!/usr/bin/env python3
"""
Deep analysis of day 1 data to find the exact pattern
"""

import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

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

print(f"Analyzing {len(day1_cases)} day 1 cases...")

# Extract features and targets
X = np.array([[case['miles'], case['receipts']] for case in day1_cases])
y = np.array([case['expected'] for case in day1_cases])

# Try different regression models
print("\n1. Simple Linear Regression:")
lr = LinearRegression()
lr.fit(X, y)
coef = lr.coef_
intercept = lr.intercept_
print(f"Formula: {intercept:.2f} + {coef[0]:.4f} * miles + {coef[1]:.4f} * receipts")

# Test this formula
predictions_lr = lr.predict(X)
errors_lr = np.abs(predictions_lr - y)
print(f"Average error: ${np.mean(errors_lr):.2f}")
print(f"Perfect matches: {np.sum(errors_lr <= 0.01)}")

# Try polynomial features
print("\n2. Polynomial Features (degree 2):")
poly_model = make_pipeline(PolynomialFeatures(2), LinearRegression())
poly_model.fit(X, y)
predictions_poly = poly_model.predict(X)
errors_poly = np.abs(predictions_poly - y)
print(f"Average error: ${np.mean(errors_poly):.2f}")
print(f"Perfect matches: {np.sum(errors_poly <= 0.01)}")

# Analyze the data patterns more deeply
print("\n3. Data Pattern Analysis:")

# Look at the relationships
miles = X[:, 0]
receipts = X[:, 1]

# Correlation analysis
print(f"Correlation between miles and expected: {np.corrcoef(miles, y)[0,1]:.3f}")
print(f"Correlation between receipts and expected: {np.corrcoef(receipts, y)[0,1]:.3f}")

# Check for different patterns in different ranges
low_mile_mask = miles < 200
med_mile_mask = (miles >= 200) & (miles < 800)
high_mile_mask = miles >= 800

print(f"\nLow miles (<200): {np.sum(low_mile_mask)} cases")
if np.sum(low_mile_mask) > 0:
    lr_low = LinearRegression()
    lr_low.fit(X[low_mile_mask], y[low_mile_mask])
    print(f"  Formula: {lr_low.intercept_:.2f} + {lr_low.coef_[0]:.4f} * miles + {lr_low.coef_[1]:.4f} * receipts")

print(f"\nMedium miles (200-800): {np.sum(med_mile_mask)} cases")
if np.sum(med_mile_mask) > 0:
    lr_med = LinearRegression()
    lr_med.fit(X[med_mile_mask], y[med_mile_mask])
    print(f"  Formula: {lr_med.intercept_:.2f} + {lr_med.coef_[0]:.4f} * miles + {lr_med.coef_[1]:.4f} * receipts")

print(f"\nHigh miles (>=800): {np.sum(high_mile_mask)} cases")
if np.sum(high_mile_mask) > 0:
    lr_high = LinearRegression()
    lr_high.fit(X[high_mile_mask], y[high_mile_mask])
    print(f"  Formula: {lr_high.intercept_:.2f} + {lr_high.coef_[0]:.4f} * miles + {lr_high.coef_[1]:.4f} * receipts")

# Show worst performing cases for analysis
print("\n4. Worst Cases Analysis:")
worst_indices = np.argsort(errors_lr)[-10:]

for idx in worst_indices:
    case = day1_cases[idx]
    predicted = predictions_lr[idx]
    error = errors_lr[idx]
    print(f"Case {case['case']}: {case['miles']:.0f}mi, ${case['receipts']:.0f}r → Expected: ${case['expected']:.2f}, Predicted: ${predicted:.2f}, Error: ${error:.2f}")

# Try to find exact formula by looking at individual cases
print("\n5. Exact Formula Discovery:")
print("Checking if there's a simpler underlying pattern...")

# Check for patterns in the ratio of expected to (miles + receipts)
total_input = miles + receipts
ratios = y / total_input
print(f"Average ratio of expected/(miles+receipts): {np.mean(ratios):.3f}")
print(f"Std dev of ratio: {np.std(ratios):.3f}")

# Check for base amount patterns
# If formula is base + miles*rate1 + receipts*rate2, solve for base
estimated_base = y - miles * coef[0] - receipts * coef[1]
print(f"Estimated base amounts range: ${np.min(estimated_base):.2f} to ${np.max(estimated_base):.2f}")
print(f"Most common base: ${np.median(estimated_base):.2f}")

# Try different base amounts
for base in [50, 75, 100, 125, 150]:
    remaining = y - base
    # Solve for miles and receipts coefficients
    A = np.column_stack([miles, receipts])
    try:
        coeffs = np.linalg.lstsq(A, remaining, rcond=None)[0]
        test_predictions = base + miles * coeffs[0] + receipts * coeffs[1]
        test_errors = np.abs(test_predictions - y)
        perfect_matches = np.sum(test_errors <= 0.01)
        print(f"Base {base}: ${base} + miles*{coeffs[0]:.4f} + receipts*{coeffs[1]:.4f} → Avg error: ${np.mean(test_errors):.2f}, Perfect: {perfect_matches}")
    except:
        pass