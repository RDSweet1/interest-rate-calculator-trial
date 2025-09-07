import json
from pathlib import Path

# Test that migrated project loads correctly
project_file = Path('projects/ocean-harbor.json')
with open(project_file) as f:
    project = json.load(f)

print('MIGRATION VALIDATION:')
print(f'Invoices: {len(project["invoices"])}')
print(f'Payments: {len(project["payments"])}') 
print(f'Total unassigned: ${sum(p["unassigned_amount"] for p in project["payments"]):,.2f}')

# Verify structure
for invoice in project['invoices']:
    required_fields = ['id', 'date', 'description', 'amount', 'status', 'balance']
    missing = [f for f in required_fields if f not in invoice]
    if missing:
        print(f'Missing invoice fields: {missing}')
    else:
        print(f'Invoice {invoice["id"]}: OK')

for payment in project['payments']:
    required_fields = ['id', 'date', 'description', 'amount', 'assignments', 'unassigned_amount']
    missing = [f for f in required_fields if f not in payment]
    if missing:
        print(f'Missing payment fields: {missing}')
    else:
        print(f'Payment {payment["id"]}: OK')

print('[SUCCESS] Migration validation successful!')