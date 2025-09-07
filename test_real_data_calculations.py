"""
Test the interest calculation engine with real migrated project data
"""

import json
from pathlib import Path
from interest_calculation_engine import InterestCalculationEngine

def test_with_ocean_harbor_data():
    """Test calculations with the migrated Ocean Harbor project"""
    print("TESTING WITH REAL OCEAN HARBOR PROJECT DATA")
    print("=" * 60)
    
    # Load the migrated project
    project_file = Path('projects/ocean-harbor.json')
    with open(project_file) as f:
        project = json.load(f)
    
    print(f"Project: {project['title']}")
    print(f"As of Date: {project['as_of_date']}")
    print(f"Grace Days: {project['grace_days']}")
    print(f"Monthly Rate: {project['monthly_rate']} ({project['monthly_rate']*100}%)")
    print()
    
    # Initialize calculation engine with project parameters
    engine = InterestCalculationEngine(
        monthly_rate=project['monthly_rate'],
        annual_rate=project['annual_rate'],
        grace_days=project['grace_days']
    )
    
    # Calculate total project interest
    total_result = engine.calculate_total_project_interest(project, project['as_of_date'])
    
    print("TOTAL PROJECT CALCULATIONS:")
    print(f"Total Principal: ${total_result['total_principal']:,.2f}")
    print(f"Total Interest: ${total_result['total_interest']:,.2f}")
    print(f"Total Payments: ${total_result['total_payments']:,.2f}")
    print(f"Total Due: ${total_result['total_due']:,.2f}")
    print()
    
    print("INVOICE BREAKDOWN:")
    for detail in total_result['invoice_details']:
        print(f"  {detail['invoice_id']}: {detail['description']}")
        print(f"    Principal: ${detail['principal']:,.2f}")
        print(f"    Interest: ${detail['interest']:,.2f}")
        print(f"    Payments: ${detail['payments']:,.2f}")
        print(f"    Balance: ${detail['balance']:,.2f}")
        print(f"    Status: {detail['status']}")
        print()
    
    # Test individual invoice calculations
    print("DETAILED INVOICE ANALYSIS:")
    for invoice in project['invoices']:
        print(f"\nInvoice: {invoice['id']} - {invoice['description']}")
        print(f"Invoice Date: {invoice['date']}")
        print(f"Amount: ${invoice['amount']:,.2f}")
        
        result = engine.calculate_invoice_interest(
            invoice, project['as_of_date'], project['payments']
        )
        
        print(f"Interest Calculation:")
        print(f"  Total Interest: ${result['total_interest']:,.2f}")
        print(f"  Current Balance: ${result['current_balance']:,.2f}")
        print(f"  Payments Applied: ${result['total_payments_applied']:,.2f}")
        print(f"  Status: {result['status']}")
        
        if result['interest_periods']:
            print(f"  Interest Periods:")
            for i, period in enumerate(result['interest_periods']):
                print(f"    Period {i+1}: {period['start_date']} to {period['end_date']}")
                print(f"      Days: {period['days']}")
                print(f"      Principal: ${period['principal']:,.2f}")
                print(f"      Interest: ${period['interest_amount']:,.2f}")
    
    # Calculate the time period
    from datetime import datetime
    start_date = datetime.strptime(project['invoices'][0]['date'], '%Y-%m-%d')
    end_date = datetime.strptime(project['as_of_date'], '%Y-%m-%d')
    total_days = (end_date - start_date).days
    total_months = total_days / 30.4375
    
    print(f"\nTIME PERIOD ANALYSIS:")
    print(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
    print(f"End Date: {end_date.strftime('%Y-%m-%d')}")
    print(f"Total Days: {total_days}")
    print(f"Total Months: {total_months:.2f}")
    
    # Show available unassigned payments
    print(f"\nUNASSIGNED PAYMENTS AVAILABLE:")
    total_unassigned = 0
    for payment in project['payments']:
        unassigned = payment['unassigned_amount']
        total_unassigned += unassigned
        print(f"  {payment['id']}: ${unassigned:,.2f} ({payment['description']})")
    
    print(f"\nTotal Unassigned Payment Amount: ${total_unassigned:,.2f}")
    print(f"Total Amount Due: ${total_result['total_due']:,.2f}")
    
    if total_unassigned >= total_result['total_due']:
        print("[OK] Sufficient unassigned payments to cover all interest!")
    else:
        shortfall = total_result['total_due'] - total_unassigned
        print(f"[WARNING] Shortfall: ${shortfall:,.2f} additional payment needed")

if __name__ == "__main__":
    test_with_ocean_harbor_data()