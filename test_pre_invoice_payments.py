"""
Test the critical pre-invoice payment functionality
This tests the Ocean Harbor scenario where payments were made BEFORE invoice dates
"""

import json
from pathlib import Path
from interest_calculation_engine import InterestCalculationEngine
from datetime import datetime

def test_pre_invoice_payment_scenario():
    """Test the exact Ocean Harbor scenario with pre-invoice payments"""
    print("TESTING PRE-INVOICE PAYMENT SCENARIO")
    print("=" * 60)
    
    # Ocean Harbor scenario:
    # Payments: Jan 4, Jan 24, Feb 21, 2023 (total $3.66M)  
    # Invoices: April 28, 2023 ($14.48M)
    # Payments were made BEFORE invoice dates!
    
    project = {
        'monthly_rate': 0.015,
        'annual_rate': 0.18,
        'grace_days': 30,
        'as_of_date': '2025-09-05',
        'invoices': [
            {
                'id': 'INV-FW-001',
                'date': '2023-04-28',
                'description': 'Fresh Water Principal',
                'amount': 13365247.68
            },
            {
                'id': 'INV-DW-001', 
                'date': '2023-04-28',
                'description': 'Dirty Water Principal',
                'amount': 1113503.81
            }
        ],
        'payments': [
            {
                'id': 'PAY-001',
                'date': '2023-01-04',
                'description': 'Flood Deductible',
                'amount': 100000.0,
                'assignments': [{
                    'invoice_id': 'INV-FW-001',
                    'assigned_amount': 100000.0,
                    'assignment_date': '2023-01-04',  # BEFORE invoice date
                    'notes': 'Pre-invoice payment'
                }],
                'unassigned_amount': 0.0
            },
            {
                'id': 'PAY-002',
                'date': '2023-01-24',
                'description': 'WIND Deductible',
                'amount': 860000.0,
                'assignments': [{
                    'invoice_id': 'INV-FW-001',
                    'assigned_amount': 860000.0,
                    'assignment_date': '2023-01-24',  # BEFORE invoice date
                    'notes': 'Pre-invoice payment'
                }],
                'unassigned_amount': 0.0
            },
            {
                'id': 'PAY-003',
                'date': '2023-02-21',
                'description': 'WIND Balance',
                'amount': 2700000.0,
                'assignments': [{
                    'invoice_id': 'INV-FW-001',
                    'assigned_amount': 2700000.0,
                    'assignment_date': '2023-02-21',  # BEFORE invoice date
                    'notes': 'Pre-invoice payment'
                }],
                'unassigned_amount': 0.0
            }
        ]
    }
    
    # Initialize calculation engine
    engine = InterestCalculationEngine(
        monthly_rate=project['monthly_rate'],
        annual_rate=project['annual_rate'],
        grace_days=project['grace_days']
    )
    
    print("SCENARIO DETAILS:")
    print(f"Invoice Date: {project['invoices'][0]['date']}")
    print(f"Grace Period: {project['grace_days']} days")
    
    # Calculate interest start date
    invoice_date = datetime.strptime(project['invoices'][0]['date'], '%Y-%m-%d')
    from datetime import timedelta
    interest_start_date = invoice_date + timedelta(days=project['grace_days'])
    print(f"Interest Starts: {interest_start_date.strftime('%Y-%m-%d')}")
    print()
    
    # Test Fresh Water invoice (the one with pre-payments)
    fw_invoice = project['invoices'][0]
    fw_result = engine.calculate_invoice_interest(
        fw_invoice, project['as_of_date'], project['payments']
    )
    
    print("FRESH WATER INVOICE ANALYSIS:")
    print(f"Original Invoice Amount: ${fw_invoice['amount']:,.2f}")
    
    # Calculate pre-invoice payments
    total_pre_payments = sum(p['amount'] for p in project['payments'])
    print(f"Pre-Invoice Payments: ${total_pre_payments:,.2f}")
    print(f"Effective Principal: ${fw_invoice['amount'] - total_pre_payments:,.2f}")
    print()
    
    print("INTEREST CALCULATION RESULTS:")
    print(f"Total Interest (with pre-payments): ${fw_result['total_interest']:,.2f}")
    print(f"Current Balance: ${fw_result['current_balance']:,.2f}")
    print(f"Status: {fw_result['status']}")
    print()
    
    # Compare with wrong calculation (without pre-invoice logic)
    # Simulate old calculation on full principal
    old_principal = fw_invoice['amount']
    days_total = (datetime.strptime(project['as_of_date'], '%Y-%m-%d') - interest_start_date).days
    months_total = days_total / 30.4375
    
    # Old compound interest calculation
    from decimal import Decimal
    old_interest = old_principal * ((1 + project['monthly_rate']) ** months_total) - old_principal
    
    print("COMPARISON WITH INCORRECT CALCULATION:")
    print(f"Wrong Interest (full principal): ${old_interest:,.2f}")
    print(f"Correct Interest (reduced principal): ${fw_result['total_interest']:,.2f}")
    
    savings = old_interest - float(fw_result['total_interest'])
    print(f"Interest Savings from Pre-Payments: ${savings:,.2f}")
    print()
    
    # Test Dirty Water invoice (no pre-payments assigned)
    dw_invoice = project['invoices'][1]
    dw_result = engine.calculate_invoice_interest(
        dw_invoice, project['as_of_date'], project['payments']
    )
    
    print("DIRTY WATER INVOICE ANALYSIS:")
    print(f"Invoice Amount: ${dw_invoice['amount']:,.2f}")
    print(f"Interest: ${dw_result['total_interest']:,.2f}")
    print(f"Status: {dw_result['status']}")
    print()
    
    # Total project analysis
    total_result = engine.calculate_total_project_interest(project, project['as_of_date'])
    
    print("TOTAL PROJECT SUMMARY:")
    print(f"Total Principal: ${total_result['total_principal']:,.2f}")
    print(f"Total Interest: ${total_result['total_interest']:,.2f}")
    print(f"Total Payments Applied: ${total_result['total_payments']:,.2f}")
    print(f"Total Amount Due: ${total_result['total_due']:,.2f}")
    print()
    
    # Validate the critical business logic
    expected_effective_principal = fw_invoice['amount'] - total_pre_payments
    print("VALIDATION:")
    print(f"Expected Effective Principal: ${expected_effective_principal:,.2f}")
    
    # The total payments should equal the pre-payments
    actual_payments_applied = total_result['total_payments']
    print(f"Actual Payments Applied: ${actual_payments_applied:,.2f}")
    
    if abs(actual_payments_applied - total_pre_payments) < 1.0:
        print("[PASS] Payment application logic correct")
    else:
        print("[FAIL] Payment application logic incorrect")
    
    # Interest should be calculated on reduced principal
    if float(fw_result['total_interest']) < old_interest:
        print("[PASS] Pre-invoice payment logic reduces interest correctly")
        print(f"Interest reduction: ${savings:,.2f}")
    else:
        print("[FAIL] Pre-invoice payment logic not working")
    
    return {
        'original_interest': old_interest,
        'corrected_interest': float(fw_result['total_interest']),
        'savings': savings,
        'effective_principal': expected_effective_principal
    }

if __name__ == "__main__":
    result = test_pre_invoice_payment_scenario()
    
    print("\n" + "=" * 60)
    print("BUSINESS IMPACT SUMMARY:")
    print(f"Without pre-invoice logic: ${result['original_interest']:,.2f} interest")
    print(f"With pre-invoice logic: ${result['corrected_interest']:,.2f} interest")  
    print(f"Total correction: ${result['savings']:,.2f}")
    print(f"This is a {result['savings']/result['original_interest']*100:.1f}% reduction in interest!")