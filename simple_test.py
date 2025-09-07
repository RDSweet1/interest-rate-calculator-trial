#!/usr/bin/env python3
"""
Simple test to verify the Ocean Harbor project data loads correctly
"""

import json
from pathlib import Path

def test_ocean_harbor_load():
    project_file = Path('projects/ocean-harbor.json')
    
    print("Testing Ocean Harbor project load...")
    
    try:
        with open(project_file) as f:
            project = json.load(f)
        
        print("[OK] File loaded successfully")
        print(f"  Title: {project.get('title', 'N/A')}")
        print(f"  Invoices: {len(project.get('invoices', []))}")
        print(f"  Payments: {len(project.get('payments', []))}")
        
        # Check payment structure
        for i, payment in enumerate(project.get('payments', [])):
            print(f"  Payment {i}: {payment.get('description', payment.get('desc', 'N/A'))}")
            print(f"    Amount: {payment.get('amount', 0)}")
            print(f"    Assignments: {len(payment.get('assignments', []))}")
            print(f"    Unassigned: {payment.get('unassigned_amount', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error loading project: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ocean_harbor_load()
    if success:
        print("\n[OK] Test completed successfully")
    else:
        print("\n[ERROR] Test failed")