"""
Playwright-based UI tests for Invoice-Payment Assignment System
Tests user workflows and visual validation for payment assignment functionality
"""

import pytest
import asyncio
import os
import sys
from datetime import datetime, timedelta
from playwright.async_api import Page, expect
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.mark.playwright
@pytest.mark.asyncio
class TestInvoicePaymentUI:
    """Playwright tests for Invoice-Payment assignment UI functionality"""
    
    @pytest.fixture(autouse=True)
    async def setup_app(self, page: Page):
        """Setup application for testing"""
        # Launch the Interest Rate Calculator
        # Note: This assumes the app can be launched for Playwright testing
        # May need modification based on how GUI testing is implemented
        await page.goto("file://localhost/path/to/app")  # Placeholder
        await page.wait_for_load_state("networkidle")
    
    async def test_create_invoice_workflow(self, page: Page):
        """Test creating a new invoice through the UI"""
        # Navigate to invoice section
        await page.click("text=Invoices")
        
        # Click Add Invoice button
        await page.click("button:has-text('Add Invoice')")
        
        # Fill in invoice dialog
        await page.fill("input[placeholder*='Invoice ID']", "INV-TEST-001")
        await page.fill("input[type='date']", "2023-01-15")
        await page.fill("input[placeholder*='Description']", "Test Invoice for Payment Assignment")
        await page.fill("input[placeholder*='Amount']", "10000.00")
        
        # Save invoice
        await page.click("button:has-text('Save')")
        
        # Verify invoice appears in table
        await expect(page.locator("text=INV-TEST-001")).to_be_visible()
        await expect(page.locator("text=Test Invoice for Payment Assignment")).to_be_visible()
        await expect(page.locator("text=$10,000.00")).to_be_visible()
    
    async def test_create_payment_workflow(self, page: Page):
        """Test creating a payment through the UI"""
        # Navigate to payments section
        await page.click("text=Payments")
        
        # Click Add Payment button
        await page.click("button:has-text('Add Payment')")
        
        # Fill in payment dialog
        await page.fill("input[type='date']", "2023-04-15")
        await page.fill("input[placeholder*='Description']", "Payment Check #1001")
        await page.fill("input[placeholder*='Amount']", "12000.00")
        
        # Save payment
        await page.click("button:has-text('Save')")
        
        # Verify payment appears in table
        await expect(page.locator("text=Payment Check #1001")).to_be_visible()
        await expect(page.locator("text=$12,000.00")).to_be_visible()
    
    async def test_assign_payment_to_invoice(self, page: Page):
        """Test assigning payment to invoice through enhanced UI"""
        # Prerequisites: Create invoice and payment first
        await self.test_create_invoice_workflow(page)
        await self.test_create_payment_workflow(page)
        
        # Navigate to payments section
        await page.click("text=Payments")
        
        # Select the payment row
        await page.click("tr:has-text('Payment Check #1001')")
        
        # Click "Assign to Invoice" button (new functionality)
        await page.click("button:has-text('Assign to Invoice')")
        
        # Assignment dialog should open
        await expect(page.locator("dialog:has-text('Assign Payment')")).to_be_visible()
        
        # Select invoice from dropdown
        await page.select_option("select[name='invoice_id']", "INV-TEST-001")
        
        # Enter assignment amount
        await page.fill("input[name='assigned_amount']", "10000.00")
        
        # Set assignment date
        await page.fill("input[name='assignment_date']", "2023-04-15")
        
        # Add notes
        await page.fill("textarea[name='notes']", "Full payment of test invoice")
        
        # Save assignment
        await page.click("button:has-text('Save Assignment')")
        
        # Verify assignment was created
        await expect(page.locator("text=Assignment saved successfully")).to_be_visible()
        
        # Check that invoice status changed
        await page.click("text=Invoices")
        await expect(page.locator("tr:has-text('INV-TEST-001') >> text=Paid")).to_be_visible()
        
        # Check that unassigned amount shows correctly
        await page.click("text=Payments")
        await expect(page.locator("tr:has-text('Payment Check #1001') >> text=$2,000.00")).to_be_visible()
    
    async def test_partial_payment_assignment(self, page: Page):
        """Test partial payment assignment updates balances correctly"""
        # Create invoice worth $5,000
        await page.click("text=Invoices")
        await page.click("button:has-text('Add Invoice')")
        await page.fill("input[placeholder*='Invoice ID']", "INV-PARTIAL-001")
        await page.fill("input[type='date']", "2023-03-01")
        await page.fill("input[placeholder*='Description']", "Partial Payment Test Invoice")
        await page.fill("input[placeholder*='Amount']", "5000.00")
        await page.click("button:has-text('Save')")
        
        # Create payment worth $3,000
        await page.click("text=Payments")
        await page.click("button:has-text('Add Payment')")
        await page.fill("input[type='date']", "2023-05-01")
        await page.fill("input[placeholder*='Description']", "Partial Payment")
        await page.fill("input[placeholder*='Amount']", "3000.00")
        await page.click("button:has-text('Save')")
        
        # Assign partial payment
        await page.click("tr:has-text('Partial Payment')")
        await page.click("button:has-text('Assign to Invoice')")
        await page.select_option("select[name='invoice_id']", "INV-PARTIAL-001")
        await page.fill("input[name='assigned_amount']", "3000.00")
        await page.fill("input[name='assignment_date']", "2023-05-01")
        await page.click("button:has-text('Save Assignment')")
        
        # Verify partial status and remaining balance
        await page.click("text=Invoices")
        await expect(page.locator("tr:has-text('INV-PARTIAL-001') >> text=Partial")).to_be_visible()
        await expect(page.locator("tr:has-text('INV-PARTIAL-001') >> text=$2,000.00")).to_be_visible()  # Remaining balance
        
        # Verify payment is fully assigned
        await page.click("text=Payments")
        await expect(page.locator("tr:has-text('Partial Payment') >> text=$0.00")).to_be_visible()  # Unassigned amount
    
    async def test_payment_reassignment(self, page: Page):
        """Test reassigning payment from one invoice to another"""
        # Create two invoices
        invoices = [
            ("INV-REASSIGN-001", "First Invoice", "3000.00"),
            ("INV-REASSIGN-002", "Second Invoice", "4000.00")
        ]
        
        await page.click("text=Invoices")
        for invoice_id, desc, amount in invoices:
            await page.click("button:has-text('Add Invoice')")
            await page.fill("input[placeholder*='Invoice ID']", invoice_id)
            await page.fill("input[type='date']", "2023-02-01")
            await page.fill("input[placeholder*='Description']", desc)
            await page.fill("input[placeholder*='Amount']", amount)
            await page.click("button:has-text('Save')")
        
        # Create payment
        await page.click("text=Payments")
        await page.click("button:has-text('Add Payment')")
        await page.fill("input[type='date']", "2023-04-01")
        await page.fill("input[placeholder*='Description']", "Reassignment Test Payment")
        await page.fill("input[placeholder*='Amount']", "3000.00")
        await page.click("button:has-text('Save')")
        
        # Initially assign to first invoice
        await page.click("tr:has-text('Reassignment Test Payment')")
        await page.click("button:has-text('Assign to Invoice')")
        await page.select_option("select[name='invoice_id']", "INV-REASSIGN-001")
        await page.fill("input[name='assigned_amount']", "3000.00")
        await page.fill("input[name='assignment_date']", "2023-04-01")
        await page.click("button:has-text('Save Assignment')")
        
        # Verify first assignment
        await page.click("text=Invoices")
        await expect(page.locator("tr:has-text('INV-REASSIGN-001') >> text=Paid")).to_be_visible()
        
        # Now reassign to second invoice
        await page.click("text=Payments")
        await page.click("tr:has-text('Reassignment Test Payment')")
        await page.click("button:has-text('Manage Assignments')")  # New button for reassignment
        
        # Reassignment dialog should show current assignments
        await expect(page.locator("text=Current Assignments")).to_be_visible()
        await expect(page.locator("text=INV-REASSIGN-001: $3,000.00")).to_be_visible()
        
        # Move assignment to second invoice
        await page.click("button[data-assignment-id='INV-REASSIGN-001']:has-text('Move')")
        await page.select_option("select[name='new_invoice_id']", "INV-REASSIGN-002")
        await page.click("button:has-text('Confirm Move')")
        
        # Verify reassignment
        await expect(page.locator("text=Assignment moved successfully")).to_be_visible()
        
        # Check invoice statuses changed
        await page.click("text=Invoices")
        await expect(page.locator("tr:has-text('INV-REASSIGN-001') >> text=Open")).to_be_visible()
        await expect(page.locator("tr:has-text('INV-REASSIGN-002') >> text=Partial")).to_be_visible()  # $3k of $4k paid
    
    async def test_amortization_table_display(self, page: Page):
        """Test amortization table shows correct calculations"""
        # Create invoice and assign payment with interest period
        await page.click("text=Invoices")
        await page.click("button:has-text('Add Invoice')")
        await page.fill("input[placeholder*='Invoice ID']", "INV-AMORT-001")
        await page.fill("input[type='date']", "2023-01-01")  # Start of year
        await page.fill("input[placeholder*='Description']", "Amortization Test Invoice")
        await page.fill("input[placeholder*='Amount']", "10000.00")
        await page.click("button:has-text('Save')")
        
        # Create payment 6 months later
        await page.click("text=Payments")
        await page.click("button:has-text('Add Payment')")
        await page.fill("input[type='date']", "2023-07-01")  # 6 months later
        await page.fill("input[placeholder*='Description']", "6-Month Payment")
        await page.fill("input[placeholder*='Amount']", "12000.00")
        await page.click("button:has-text('Save')")
        
        # Assign payment
        await page.click("tr:has-text('6-Month Payment')")
        await page.click("button:has-text('Assign to Invoice')")
        await page.select_option("select[name='invoice_id']", "INV-AMORT-001")
        await page.fill("input[name='assigned_amount']", "11500.00")  # Principal + interest
        await page.fill("input[name='assignment_date']", "2023-07-01")
        await page.click("button:has-text('Save Assignment')")
        
        # View amortization table
        await page.click("text=Invoices")
        await page.click("tr:has-text('INV-AMORT-001')")
        await page.click("button:has-text('View Amortization')")  # New feature
        
        # Amortization dialog should show detailed breakdown
        await expect(page.locator("dialog:has-text('Amortization Schedule')")).to_be_visible()
        
        # Check for expected amortization table elements
        await expect(page.locator("th:has-text('Period')")).to_be_visible()
        await expect(page.locator("th:has-text('Principal')")).to_be_visible()
        await expect(page.locator("th:has-text('Interest')")).to_be_visible()
        await expect(page.locator("th:has-text('Payment')")).to_be_visible()
        await expect(page.locator("th:has-text('Balance')")).to_be_visible()
        
        # Check calculation rows exist
        await expect(page.locator("td:has-text('2023-01-01')")).to_be_visible()  # Start date
        await expect(page.locator("td:has-text('2023-07-01')")).to_be_visible()  # Payment date
        await expect(page.locator("td:has-text('$10,000.00')")).to_be_visible()  # Original principal
        await expect(page.locator("td:has-text('$1,500.00')")).to_be_visible()  # Interest (approx)
        await expect(page.locator("td:has-text('$0.00')")).to_be_visible()  # Final balance
    
    async def test_unassigned_payments_view(self, page: Page):
        """Test view of unassigned payment amounts"""
        # Create payments with different assignment statuses
        payments = [
            ("Fully Assigned Payment", "10000.00", "10000.00"),  # Fully assigned
            ("Partially Assigned Payment", "5000.00", "3000.00"),  # Partially assigned  
            ("Unassigned Payment", "2000.00", "0.00")  # Completely unassigned
        ]
        
        await page.click("text=Payments")
        for desc, amount, assigned in payments:
            await page.click("button:has-text('Add Payment')")
            await page.fill("input[type='date']", "2023-06-01")
            await page.fill("input[placeholder*='Description']", desc)
            await page.fill("input[placeholder*='Amount']", amount)
            await page.click("button:has-text('Save')")
            
            # Simulate assignment logic here if needed
        
        # Filter to show only unassigned amounts
        await page.click("button:has-text('Show Unassigned Only')")  # New filter
        
        # Verify filtering works
        await expect(page.locator("tr:has-text('Partially Assigned Payment')")).to_be_visible()
        await expect(page.locator("tr:has-text('Unassigned Payment')")).to_be_visible()
        await expect(page.locator("tr:has-text('Fully Assigned Payment')")).not_to_be_visible()
        
        # Check unassigned amounts are highlighted
        await expect(page.locator("tr:has-text('Partially Assigned Payment') >> .unassigned-amount:has-text('$2,000.00')")).to_be_visible()
        await expect(page.locator("tr:has-text('Unassigned Payment') >> .unassigned-amount:has-text('$2,000.00')")).to_be_visible()
    
    async def test_invoice_status_color_coding(self, page: Page):
        """Test invoice status color coding in table"""
        # Create invoices with different statuses
        statuses = [
            ("INV-OPEN-001", "Open Invoice", "open", "red"),
            ("INV-PARTIAL-001", "Partial Invoice", "partial", "yellow"), 
            ("INV-PAID-001", "Paid Invoice", "paid", "green"),
            ("INV-OVERDUE-001", "Overdue Invoice", "overdue", "dark-red")
        ]
        
        await page.click("text=Invoices")
        
        for invoice_id, desc, status, expected_color in statuses:
            await page.click("button:has-text('Add Invoice')")
            await page.fill("input[placeholder*='Invoice ID']", invoice_id)
            await page.fill("input[type='date']", "2023-01-01")
            await page.fill("input[placeholder*='Description']", desc)
            await page.fill("input[placeholder*='Amount']", "1000.00")
            await page.click("button:has-text('Save')")
            
            # Simulate setting status through business logic
            # In real implementation, status would be calculated based on payments and dates
        
        # Check color coding is applied
        for invoice_id, desc, status, expected_color in statuses:
            invoice_row = page.locator(f"tr:has-text('{invoice_id}')")
            await expect(invoice_row).to_have_class(f"status-{status}")
    
    async def test_payment_validation_errors(self, page: Page):
        """Test payment assignment validation and error messages"""
        # Create invoice worth $1,000
        await page.click("text=Invoices")
        await page.click("button:has-text('Add Invoice')")
        await page.fill("input[placeholder*='Invoice ID']", "INV-VALIDATE-001")
        await page.fill("input[type='date']", "2023-01-01")
        await page.fill("input[placeholder*='Description']", "Validation Test Invoice")
        await page.fill("input[placeholder*='Amount']", "1000.00")
        await page.click("button:has-text('Save')")
        
        # Create payment worth $500
        await page.click("text=Payments")
        await page.click("button:has-text('Add Payment')")
        await page.fill("input[type='date']", "2023-02-01")
        await page.fill("input[placeholder*='Description']", "Small Payment")
        await page.fill("input[placeholder*='Amount']", "500.00")
        await page.click("button:has-text('Save')")
        
        # Try to assign more than payment amount
        await page.click("tr:has-text('Small Payment')")
        await page.click("button:has-text('Assign to Invoice')")
        await page.select_option("select[name='invoice_id']", "INV-VALIDATE-001")
        await page.fill("input[name='assigned_amount']", "600.00")  # More than $500 payment
        await page.fill("input[name='assignment_date']", "2023-02-01")
        await page.click("button:has-text('Save Assignment')")
        
        # Should show validation error
        await expect(page.locator("text=Assignment amount cannot exceed payment amount")).to_be_visible()
        await expect(page.locator("input[name='assigned_amount']")).to_have_class("error")
        
        # Try to assign to same invoice twice (creating over-assignment)
        await page.fill("input[name='assigned_amount']", "300.00")
        await page.click("button:has-text('Save Assignment')")
        
        # Now try to assign remaining $200 + more to same invoice
        await page.click("button:has-text('Add Assignment')")  # Add another assignment to same payment
        await page.select_option("select[name='invoice_id_2']", "INV-VALIDATE-001")
        await page.fill("input[name='assigned_amount_2']", "300.00")  # Total would be $600 > $500
        await page.click("button:has-text('Save Assignment')")
        
        # Should show total assignment error
        await expect(page.locator("text=Total assignments ($600.00) exceed payment amount ($500.00)")).to_be_visible()
    
    async def test_export_amortization_report(self, page: Page):
        """Test exporting amortization schedule to Excel/PDF"""
        # Set up invoice with payment history
        await self.test_amortization_table_display(page)
        
        # Open amortization view
        await page.click("text=Invoices")
        await page.click("tr:has-text('INV-AMORT-001')")
        await page.click("button:has-text('View Amortization')")
        
        # Export to Excel
        await page.click("button:has-text('Export to Excel')")
        
        # Should trigger download
        async with page.expect_download() as download_info:
            await page.click("button:has-text('Export to Excel')")
        download = await download_info.value
        assert download.suggested_filename.endswith('.xlsx')
        
        # Export to PDF
        async with page.expect_download() as download_info:
            await page.click("button:has-text('Export to PDF')")
        download = await download_info.value
        assert download.suggested_filename.endswith('.pdf')

@pytest.mark.playwright
@pytest.mark.asyncio  
class TestInvoicePaymentPerformance:
    """Performance tests for large datasets"""
    
    async def test_large_invoice_list_performance(self, page: Page):
        """Test UI performance with many invoices"""
        # Create 100+ invoices programmatically
        await page.click("text=Invoices")
        
        # Use page.evaluate to create many invoices quickly
        await page.evaluate("""
            // Simulate creating 100 invoices through JavaScript
            for(let i = 1; i <= 100; i++) {
                // This would call the actual invoice creation API
                console.log(`Creating invoice ${i}`);
            }
        """)
        
        # Measure table rendering time
        start_time = asyncio.get_event_loop().time()
        await page.wait_for_selector("tr:nth-child(100)")  # Wait for 100th row
        end_time = asyncio.get_event_loop().time()
        
        render_time = end_time - start_time
        assert render_time < 2.0  # Should render in less than 2 seconds
    
    async def test_complex_payment_assignment_performance(self, page: Page):
        """Test performance with complex payment assignments"""
        # This would test scenarios with many payments assigned to many invoices
        pytest.skip("Performance test - implement after core functionality")

if __name__ == "__main__":
    # Run with: python -m pytest tests/test_playwright_invoice_payment.py -v --browser=chromium
    pytest.main([__file__, "-v", "--browser=chromium"])