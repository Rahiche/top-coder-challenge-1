#!/usr/bin/env python3
"""
Systematic analysis of algorithm performance by trip duration.
Sort by lowest errors and identify patterns for improvement.
"""

import pandas as pd
import json

def analyze_by_duration():
    """Analyze performance by trip duration, starting with best cases."""
    
    # Load the comparison data
    df = pd.read_csv('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv')
    
    print("🔍 SYSTEMATIC DURATION ANALYSIS")
    print("=" * 50)
    
    # Get unique trip durations
    durations = sorted(df['trip_duration_days'].unique())
    
    for duration in durations:
        print(f"\n📊 ANALYZING {duration}-DAY TRIPS")
        print("=" * 30)
        
        # Filter by duration and sort by absolute error
        duration_data = df[df['trip_duration_days'] == duration].copy()
        duration_data = duration_data.sort_values('absolute_error')
        
        total_cases = len(duration_data)
        avg_error = duration_data['absolute_error'].mean()
        median_error = duration_data['absolute_error'].median()
        max_error = duration_data['absolute_error'].max()
        min_error = duration_data['absolute_error'].min()
        
        print(f"Total cases: {total_cases}")
        print(f"Average error: ${avg_error:.2f}")
        print(f"Median error: ${median_error:.2f}")
        print(f"Error range: ${min_error:.2f} - ${max_error:.2f}")
        
        # Show best cases (lowest errors)
        print(f"\n🎯 BEST CASES (lowest errors):")
        best_cases = duration_data.head(5)
        for _, row in best_cases.iterrows():
            print(f"   Case {int(row['case_number'])}: {row['miles_traveled']:.0f}mi, "
                  f"${row['total_receipts_amount']:.0f}r → "
                  f"Expected: ${row['expected_output']:.2f}, "
                  f"Got: ${row['algorithm_result']:.2f}, "
                  f"Error: ${row['absolute_error']:.2f}")
        
        # Show worst cases
        print(f"\n❌ WORST CASES (highest errors):")
        worst_cases = duration_data.tail(3)
        for _, row in worst_cases.iterrows():
            print(f"   Case {int(row['case_number'])}: {row['miles_traveled']:.0f}mi, "
                  f"${row['total_receipts_amount']:.0f}r → "
                  f"Expected: ${row['expected_output']:.2f}, "
                  f"Got: ${row['algorithm_result']:.2f}, "
                  f"Error: ${row['absolute_error']:.2f}")
        
        # Analyze patterns in best vs worst cases
        analyze_patterns(duration_data, duration)
        
        print(f"\n{'='*50}")
        input(f"Press Enter to continue to {duration+1 if duration < max(durations) else 'summary'}...")

def analyze_patterns(duration_data, duration):
    """Analyze patterns in the data to identify improvement opportunities."""
    
    print(f"\n🔍 PATTERN ANALYSIS:")
    
    # Divide into performance quartiles
    q1 = duration_data['absolute_error'].quantile(0.25)
    q3 = duration_data['absolute_error'].quantile(0.75)
    
    best_quartile = duration_data[duration_data['absolute_error'] <= q1]
    worst_quartile = duration_data[duration_data['absolute_error'] >= q3]
    
    # Compare characteristics
    print(f"   Best quartile (error ≤ ${q1:.2f}):")
    print(f"     Average miles: {best_quartile['miles_traveled'].mean():.0f}")
    print(f"     Average receipts: ${best_quartile['total_receipts_amount'].mean():.0f}")
    print(f"     Average expected: ${best_quartile['expected_output'].mean():.2f}")
    
    print(f"   Worst quartile (error ≥ ${q3:.2f}):")
    print(f"     Average miles: {worst_quartile['miles_traveled'].mean():.0f}")
    print(f"     Average receipts: ${worst_quartile['total_receipts_amount'].mean():.0f}")
    print(f"     Average expected: ${worst_quartile['expected_output'].mean():.2f}")
    
    # Check for over/under calculation patterns
    over_calc = duration_data[duration_data['algorithm_result'] > duration_data['expected_output']]
    under_calc = duration_data[duration_data['algorithm_result'] <= duration_data['expected_output']]
    
    print(f"   Over-calculation: {len(over_calc)}/{len(duration_data)} cases ({len(over_calc)/len(duration_data)*100:.1f}%)")
    print(f"   Under-calculation: {len(under_calc)}/{len(duration_data)} cases ({len(under_calc)/len(duration_data)*100:.1f}%)")
    
    # Look for specific patterns that might indicate formula issues
    if len(worst_quartile) > 0:
        high_receipt_errors = worst_quartile[worst_quartile['total_receipts_amount'] > 1000]
        high_mile_errors = worst_quartile[worst_quartile['miles_traveled'] > 500]
        
        if len(high_receipt_errors) > len(worst_quartile) * 0.5:
            print(f"   ⚠️  High receipt cases dominate worst errors")
        
        if len(high_mile_errors) > len(worst_quartile) * 0.5:
            print(f"   ⚠️  High mileage cases dominate worst errors")

def generate_duration_specific_analysis():
    """Generate detailed analysis for each duration to identify specific fixes."""
    
    df = pd.read_csv('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv')
    durations = sorted(df['trip_duration_days'].unique())
    
    analysis_report = []
    
    for duration in durations:
        duration_data = df[df['trip_duration_days'] == duration].copy()
        duration_data = duration_data.sort_values('absolute_error')
        
        # Get the best cases to understand what works
        best_5 = duration_data.head(5)
        worst_5 = duration_data.tail(5)
        
        analysis = {
            'duration': duration,
            'total_cases': len(duration_data),
            'avg_error': duration_data['absolute_error'].mean(),
            'median_error': duration_data['absolute_error'].median(),
            'best_cases': best_5.to_dict('records'),
            'worst_cases': worst_5.to_dict('records'),
            'over_calc_rate': len(duration_data[duration_data['algorithm_result'] > duration_data['expected_output']]) / len(duration_data)
        }
        
        analysis_report.append(analysis)
    
    # Save detailed analysis
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/duration_analysis_detailed.json', 'w') as f:
        json.dump(analysis_report, f, indent=2)
    
    print("📝 Detailed analysis saved to duration_analysis_detailed.json")
    return analysis_report

if __name__ == "__main__":
    print("Starting systematic duration analysis...")
    print("This will analyze each trip duration separately to identify specific improvements.")
    print()
    
    # Generate detailed analysis first
    detailed_analysis = generate_duration_specific_analysis()
    
    # Interactive analysis
    analyze_by_duration()