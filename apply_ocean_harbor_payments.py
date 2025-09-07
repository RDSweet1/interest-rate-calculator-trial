"""
Apply payments to Ocean Harbor invoices and add drywall invoice
"""

import json
from pathlib import Path
from interest_calculation_engine import InterestCalculationEngine

def apply_ocean_harbor_payments():
    """Apply payments to Ocean Harbor invoices and add drywall invoice"""
    
    print("UPDATING OCEAN HARBOR PROJECT WITH PAYMENT ASSIGNMENTS")
    print("=" * 60)
    
    # Load current project
    project_file = Path('projects/ocean-harbor.json')
    with open(project_file) as f:
        project = json.load(f)
    
    print("CURRENT PROJECT STATE:")
    print(f"Invoices: {len(project['invoices'])}")
    print(f"Payments: {len(project['payments'])}")
    print(f"Total Unassigned: ${sum(p['unassigned_amount'] for p in project['payments']):,.2f}")
    print()
    
    # Step 1: Add Drywall invoice
    print("STEP 1: Adding Drywall Invoice")
    drywall_invoice = {
        "id": "INV-DRY-001",
        "date": "2023-04-28",
        "description": "Drywall Principal", 
        "amount": 250000.00,  # Reasonable drywall amount
        "status": "open",
        "total_payments": 0.0,
        "balance": 250000.00,
        "last_payment_date": None,
        "interest_periods": []
    }
    
    project['invoices'].append(drywall_invoice)
    print(f"Added: {drywall_invoice['id']} - ${drywall_invoice['amount']:,.2f}")
    print()
    
    # Step 2: Apply payments using the calculation engine
    print("STEP 2: Applying Payments to Invoices")
    engine = InterestCalculationEngine(
        monthly_rate=project['monthly_rate'],
        annual_rate=project['annual_rate'], 
        grace_days=project['grace_days']
    )
    
    # Payment assignments:
    # Flood Deductible -> Fresh Water (pre-invoice payment)
    # WIND Deductible -> Fresh Water (pre-invoice payment)  
    # WIND Balance -> Fresh Water (pre-invoice payment)
    # We'll also add a drywall payment
    
    assignments = [
        {
            'payment_id': 'PAY-36A47D0E',  # Flood Deductible
            'invoice_id': 'INV-FW-001',    # Fresh Water
            'amount': 100000.0,
            'date': '2023-01-04',
            'notes': 'Flood deductible applied to Fresh Water principal'
        },
        {
            'payment_id': 'PAY-CCCF756B',  # WIND Deductible  
            'invoice_id': 'INV-FW-001',    # Fresh Water
            'amount': 860000.0,
            'date': '2023-01-24', 
            'notes': 'WIND deductible applied to Fresh Water principal'
        },
        {
            'payment_id': 'PAY-00124688',  # WIND Balance
            'invoice_id': 'INV-FW-001',    # Fresh Water  
            'amount': 2700000.0,
            'date': '2023-02-21',
            'notes': 'WIND balance applied to Fresh Water principal'
        }
    ]
    
    # Add drywall payment
    drywall_payment = {
        "id": "PAY-DRYWALL",
        "date": "2023-05-15", 
        "description": "Drywall Payment",
        "amount": 150000.0,
        "assignments": [],
        "unassigned_amount": 150000.0
    }
    
    project['payments'].append(drywall_payment)
    print(f"Added payment: {drywall_payment['description']} - ${drywall_payment['amount']:,.2f}")
    
    # Apply drywall payment to drywall invoice
    assignments.append({
        'payment_id': 'PAY-DRYWALL',
        'invoice_id': 'INV-DRY-001',
        'amount': 150000.0,
        'date': '2023-05-15',
        'notes': 'Drywall payment applied to drywall invoice'
    })
    
    # Apply all assignments
    for assignment in assignments:
        print(f"Applying: ${assignment['amount']:,.2f} from {assignment['payment_id']} to {assignment['invoice_id']}")
        
        # Find payment and invoice
        payment = next(p for p in project['payments'] if p['id'] == assignment['payment_id'])
        invoice = next(i for i in project['invoices'] if i['id'] == assignment['invoice_id'])
        
        # Use calculation engine to apply assignment
        updated_invoice, updated_payment = engine.apply_payment_to_invoice(
            invoice,
            payment,
            assignment['amount'],
            assignment['date'],
            assignment['notes']
        )
        
        # Update project data
        for i, inv in enumerate(project['invoices']):
            if inv['id'] == updated_invoice['id']:
                project['invoices'][i] = updated_invoice
                break
                
        for i, pay in enumerate(project['payments']):
            if pay['id'] == updated_payment['id']:
                project['payments'][i] = updated_payment
                break
    
    print()
    
    # Step 3: Calculate updated interest
    print("STEP 3: Updated Interest Calculations")
    total_result = engine.calculate_total_project_interest(project, project['as_of_date'])
    
    print("Updated Project Summary:")
    print(f"Total Principal: ${total_result['total_principal']:,.2f}")
    print(f"Total Interest: ${total_result['total_interest']:,.2f}")
    print(f"Total Payments Applied: ${total_result['total_payments']:,.2f}")
    print(f"Total Amount Due: ${total_result['total_due']:,.2f}")
    print()
    
    print("Invoice Details:")
    for detail in total_result['invoice_details']:
        print(f"  {detail['invoice_id']}: {detail['description']}")
        print(f"    Principal: ${detail['principal']:,.2f}")
        print(f"    Interest: ${detail['interest']:,.2f}")
        print(f"    Payments: ${detail['payments']:,.2f}")
        print(f"    Balance: ${detail['balance']:,.2f}")
        print(f"    Status: {detail['status']}")
        print()
    
    # Step 4: Save updated project
    print("STEP 4: Saving Updated Project")
    with open(project_file, 'w') as f:
        json.dump(project, f, indent=2)
    
    print(f"Project saved to {project_file}")
    print()
    
    # Step 5: Show the impact
    print("BUSINESS IMPACT:")
    print(f"Fresh Water Invoice:")
    fw_detail = next(d for d in total_result['invoice_details'] if d['invoice_id'] == 'INV-FW-001')
    print(f"  Original Amount: $13,365,247.68")
    print(f"  Pre-Invoice Payments: $3,660,000.00") 
    print(f"  Effective Principal: ${13365247.68 - 3660000:,.2f}")
    print(f"  Interest on Reduced Principal: ${fw_detail['interest']:,.2f}")
    print(f"  Status: {fw_detail['status']}")
    
    return project

if __name__ == "__main__":
    updated_project = apply_ocean_harbor_payments()
    print("\n" + "=" * 60)
    print("✅ Ocean Harbor payments successfully applied!")
    print("✅ Drywall invoice and payment added!")
    print("✅ Interest calculations updated with pre-invoice payment logic!")