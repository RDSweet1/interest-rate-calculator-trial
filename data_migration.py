"""
Critical Data Migration Utility
Converts existing project files to new invoice-payment assignment model
MUST BE RUN BEFORE implementing new functionality
"""

import json
import os
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict, Any, List
import uuid


class DataMigrationManager:
    """Handles migration from old data model to invoice-payment assignment model"""
    
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.backup_dir = Path("projects_backup")
        
    def backup_projects(self):
        """Create backup of all existing projects before migration"""
        print("Creating backup of existing projects...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        shutil.copytree(self.projects_dir, self.backup_dir)
        print(f"[OK] Backup created in {self.backup_dir}")
        
    def migrate_all_projects(self):
        """Migrate all projects in the projects directory"""
        if not self.projects_dir.exists():
            print("No projects directory found - creating new one")
            self.projects_dir.mkdir(exist_ok=True)
            return
            
        self.backup_projects()
        
        project_files = list(self.projects_dir.glob("*.json"))
        print(f"Found {len(project_files)} projects to migrate")
        
        for project_file in project_files:
            try:
                self.migrate_single_project(project_file)
                print(f"[OK] Migrated: {project_file.name}")
            except Exception as e:
                print(f"[ERROR] Failed to migrate {project_file.name}: {e}")
                
    def migrate_single_project(self, project_file: Path):
        """Migrate a single project file to new data model"""
        
        # Load existing project
        with open(project_file, 'r') as f:
            old_project = json.load(f)
            
        # Create new project structure
        new_project = self.convert_to_new_model(old_project)
        
        # Save migrated project
        with open(project_file, 'w') as f:
            json.dump(new_project, f, indent=2)
            
    def convert_to_new_model(self, old_project: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old project model to new invoice-payment assignment model"""
        
        new_project = {
            # Keep all existing basic fields
            'title': old_project.get('title', 'Untitled Project'),
            'billing_date': old_project.get('billing_date', '2023-01-01'),
            'as_of_date': old_project.get('as_of_date', '2023-12-31'),
            'grace_days': old_project.get('grace_days', 30),
            'annual_rate': old_project.get('annual_rate', 0.18),
            'monthly_rate': old_project.get('monthly_rate', 0.015),
            
            # NEW: Convert principal amounts to invoices
            'invoices': self.convert_principals_to_invoices(old_project),
            
            # NEW: Convert payments to new structure  
            'payments': self.convert_payments_to_new_structure(old_project),
            
            # Keep other fields
            'sharepoint': old_project.get('sharepoint', {
                'folder_id': None,
                'folder_path': None
            })
        }
        
        return new_project
        
    def convert_principals_to_invoices(self, old_project: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert principal_fw/principal_dw to invoice records"""
        invoices = []
        
        # Convert principal_fw to invoice
        principal_fw = old_project.get('principal_fw', 0)
        if principal_fw > 0:
            invoices.append({
                'id': 'INV-FW-001',
                'date': old_project.get('billing_date', '2023-01-01'),
                'description': 'Fresh Water Principal',
                'amount': float(principal_fw),
                'status': 'open',  # Will be recalculated based on payments
                'total_payments': 0.0,
                'balance': float(principal_fw),
                'last_payment_date': None,
                'interest_periods': []
            })
            
        # Convert principal_dw to invoice
        principal_dw = old_project.get('principal_dw', 0)  
        if principal_dw > 0:
            invoices.append({
                'id': 'INV-DW-001',
                'date': old_project.get('billing_date', '2023-01-01'),
                'description': 'Dirty Water Principal',
                'amount': float(principal_dw),
                'status': 'open',
                'total_payments': 0.0,
                'balance': float(principal_dw),
                'last_payment_date': None,
                'interest_periods': []
            })
            
        # Add existing invoices if they exist (for projects already partially migrated)
        existing_invoices = old_project.get('invoices', [])
        for invoice in existing_invoices:
            # Ensure new fields exist
            migrated_invoice = {
                'id': invoice.get('id', f"INV-{str(uuid.uuid4())[:8].upper()}"),
                'date': invoice.get('date', old_project.get('billing_date', '2023-01-01')),
                'description': invoice.get('description', 'Migrated Invoice'),
                'amount': float(invoice.get('amount', 0)),
                'status': invoice.get('status', 'open'),
                'total_payments': float(invoice.get('total_payments', 0)),
                'balance': float(invoice.get('balance', invoice.get('amount', 0))),
                'last_payment_date': invoice.get('last_payment_date'),
                'interest_periods': invoice.get('interest_periods', [])
            }
            invoices.append(migrated_invoice)
            
        return invoices
        
    def convert_payments_to_new_structure(self, old_project: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert old payment structure to new assignment-based structure"""
        new_payments = []
        
        old_payments = old_project.get('payments', [])
        
        for i, old_payment in enumerate(old_payments):
            # Generate unique ID if not present
            payment_id = old_payment.get('id', f"PAY-{str(uuid.uuid4())[:8].upper()}")
            
            new_payment = {
                'id': payment_id,
                'date': old_payment.get('date', '2023-01-01'),
                'description': old_payment.get('desc', old_payment.get('description', f'Payment {i+1}')),
                'amount': float(old_payment.get('amount', 0)),
                
                # NEW FIELDS: Start with empty assignments - user will assign manually
                'assignments': old_payment.get('assignments', []),
                'unassigned_amount': float(old_payment.get('unassigned_amount', old_payment.get('amount', 0)))
            }
            
            new_payments.append(new_payment)
            
        return new_payments
        
    def validate_migration(self, project_file: Path):
        """Validate that migration was successful"""
        with open(project_file, 'r') as f:
            project = json.load(f)
            
        errors = []
        
        # Check required fields exist
        required_fields = ['title', 'invoices', 'payments']
        for field in required_fields:
            if field not in project:
                errors.append(f"Missing required field: {field}")
                
        # Check invoice structure
        for i, invoice in enumerate(project.get('invoices', [])):
            required_invoice_fields = ['id', 'date', 'description', 'amount', 'status', 'balance']
            for field in required_invoice_fields:
                if field not in invoice:
                    errors.append(f"Invoice {i}: Missing field {field}")
                    
        # Check payment structure  
        for i, payment in enumerate(project.get('payments', [])):
            required_payment_fields = ['id', 'date', 'description', 'amount', 'assignments', 'unassigned_amount']
            for field in required_payment_fields:
                if field not in payment:
                    errors.append(f"Payment {i}: Missing field {field}")
                    
        if errors:
            raise ValueError(f"Migration validation failed: {errors}")
            
        return True
        
    def create_migration_report(self) -> str:
        """Generate report of migration results"""
        report = []
        report.append("DATA MIGRATION REPORT")
        report.append("=" * 50)
        
        if not self.projects_dir.exists():
            report.append("No projects found to migrate")
            return "\n".join(report)
            
        project_files = list(self.projects_dir.glob("*.json"))
        report.append(f"Projects processed: {len(project_files)}")
        report.append("")
        
        for project_file in project_files:
            try:
                with open(project_file, 'r') as f:
                    project = json.load(f)
                    
                invoice_count = len(project.get('invoices', []))
                payment_count = len(project.get('payments', []))
                total_invoice_amount = sum(inv.get('amount', 0) for inv in project.get('invoices', []))
                total_payment_amount = sum(pay.get('amount', 0) for pay in project.get('payments', []))
                unassigned_amount = sum(pay.get('unassigned_amount', 0) for pay in project.get('payments', []))
                
                report.append(f"PROJECT: {project_file.name}")
                report.append(f"   Title: {project.get('title', 'Unknown')}")
                report.append(f"   Invoices: {invoice_count} (${total_invoice_amount:,.2f})")
                report.append(f"   Payments: {payment_count} (${total_payment_amount:,.2f})")
                report.append(f"   Unassigned: ${unassigned_amount:,.2f}")
                report.append("")
                
            except Exception as e:
                report.append(f"[ERROR] {project_file.name}: Error reading - {e}")
                report.append("")
                
        return "\n".join(report)


def main():
    """Run data migration"""
    print("[MIGRATION] Starting Data Migration for Invoice-Payment Assignment System")
    print("=" * 60)
    
    migrator = DataMigrationManager()
    
    try:
        migrator.migrate_all_projects()
        print("\n[SUCCESS] Migration completed successfully!")
        
        # Generate and display report
        report = migrator.create_migration_report()
        print(f"\n{report}")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("1. [DONE] Data migration complete")  
        print("2. [TODO] Run tests to validate migration")
        print("3. [TODO] Implement payment assignment UI")
        print("4. [TODO] Test with migrated data")
        print("\nBackup created in 'projects_backup' directory")
        
    except Exception as e:
        print(f"\n[FAILED] Migration failed: {e}")
        print("Check 'projects_backup' directory to restore if needed")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())