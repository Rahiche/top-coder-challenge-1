#!/usr/bin/env python3
"""
Generate a CSV comparison file with public test cases, expected outputs, and algorithm results.
"""

import json
import csv
import subprocess
import os

def run_algorithm(days, miles, receipts):
    """Run the algorithm and get the result."""
    try:
        # Run the bash script with the inputs
        result = subprocess.run(
            ['./run.sh', str(days), str(miles), str(receipts)],
            capture_output=True,
            text=True,
            cwd='/Users/raoufrahiche/IdeaProjects/top-coder-challenge'
        )
        
        if result.returncode == 0:
            return float(result.stdout.strip())
        else:
            print(f"Error running algorithm: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception running algorithm: {e}")
        return None

def generate_comparison_csv():
    """Generate a CSV file with test cases and comparison results."""
    
    # Read the public test cases
    with open('/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    # Prepare the CSV data
    csv_data = []
    
    print("Processing public test cases...")
    
    for i, case in enumerate(public_cases):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Get our algorithm's result
        our_result = run_algorithm(days, miles, receipts)
        
        # Calculate error if we got a result
        error = abs(our_result - expected) if our_result is not None else None
        error_percentage = (error / expected * 100) if error is not None and expected != 0 else None
        
        # Add to CSV data
        csv_data.append({
            'case_number': i + 1,
            'trip_duration_days': days,
            'miles_traveled': miles,
            'total_receipts_amount': receipts,
            'expected_output': expected,
            'algorithm_result': our_result,
            'absolute_error': error,
            'error_percentage': error_percentage
        })
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{len(public_cases)} cases...")
    
    # Write to CSV
    csv_filename = '/Users/raoufrahiche/IdeaProjects/top-coder-challenge/public_cases_comparison.csv'
    
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = [
            'case_number',
            'trip_duration_days', 
            'miles_traveled',
            'total_receipts_amount',
            'expected_output',
            'algorithm_result',
            'absolute_error',
            'error_percentage'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"✅ CSV file generated: {csv_filename}")
    
    # Calculate some summary statistics
    valid_results = [row for row in csv_data if row['algorithm_result'] is not None]
    total_cases = len(csv_data)
    successful_cases = len(valid_results)
    
    if valid_results:
        errors = [row['absolute_error'] for row in valid_results]
        avg_error = sum(errors) / len(errors)
        max_error = max(errors)
        min_error = min(errors)
        
        # Count cases by error ranges
        exact_matches = len([e for e in errors if e <= 0.01])
        close_matches = len([e for e in errors if e <= 1.00])
        good_matches = len([e for e in errors if e <= 10.00])
        
        print(f"\n📊 Summary Statistics:")
        print(f"   Total cases: {total_cases}")
        print(f"   Successful runs: {successful_cases}")
        print(f"   Failed runs: {total_cases - successful_cases}")
        print(f"   Average error: ${avg_error:.2f}")
        print(f"   Maximum error: ${max_error:.2f}")
        print(f"   Minimum error: ${min_error:.2f}")
        print(f"   Exact matches (±$0.01): {exact_matches} ({exact_matches/successful_cases*100:.1f}%)")
        print(f"   Close matches (±$1.00): {close_matches} ({close_matches/successful_cases*100:.1f}%)")
        print(f"   Good matches (±$10.00): {good_matches} ({good_matches/successful_cases*100:.1f}%)")
    
    return csv_filename

if __name__ == "__main__":
    # Change to the project directory
    os.chdir('/Users/raoufrahiche/IdeaProjects/top-coder-challenge')
    
    # Generate the comparison CSV
    csv_file = generate_comparison_csv()
    
    print(f"\n🎯 Results saved to: {csv_file}")
    print("📈 You can now open this CSV file in Excel, Google Sheets, or any data analysis tool")
    print("🔍 Use it to identify patterns in errors and improve your algorithm")