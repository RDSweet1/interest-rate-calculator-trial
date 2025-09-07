# Enhanced Phase 3: Invoice-Payment Assignment System

**Project:** Interest Rate Calculator - Critical Business Logic Enhancement  
**Date:** 2025-09-07  
**Phase:** 3 Enhanced  
**Duration:** 8-10 hours (expanded from original 4-5 hours)  
**Dependencies:** Phase 1 & 2 Complete  

## Executive Summary

This enhanced Phase 3 addresses the critical missing functionality: **per-invoice amortization with payment assignment**. The core business requirement is that each invoice must accrue interest from its invoice date until a payment is applied to it, creating individual amortization schedules that accurately reflect payment applications.

## Core Business Requirements

### 1. Invoice-Centric Interest Calculation
- Each invoice begins accruing interest from its **invoice date**
- Interest compounds according to project settings (monthly/annual rate)
- Interest calculation **stops** when payment is fully applied to invoice
- Partial payments reduce principal but interest continues on remaining balance

### 2. Payment-to-Invoice Assignment
- Payments can be assigned to specific invoices with assignment dates
- Assignment date determines when interest calculation stops for that invoice
- Support for:
  - **Full payment**: Complete invoice payoff
  - **Partial payment**: Reduces principal, interest continues on balance  
  - **Overpayment**: Excess can be applied to other invoices or held as credit
  - **Multiple payments**: Several payments can be applied to one invoice

### 3. Amortization Table Generation
- Generate per-invoice amortization schedules
- Show interest accrual from invoice date to payment date(s)
- Display payment applications and remaining balances
- Calculate total interest owed per invoice

## Technical Implementation Plan

### Phase 3A: Data Model Enhancement (2-3 hours)

#### Enhanced Payment Model
```python
Payment = {
    'id': str,                    # Unique payment ID
    'date': datetime,             # Payment received date  
    'description': str,           # Payment description
    'amount': float,              # Payment amount
    'assignments': [              # NEW: Payment assignments to invoices
        {
            'invoice_id': str,    # Target invoice ID
            'assigned_amount': float,  # Amount applied to this invoice
            'assignment_date': datetime,  # When payment was assigned
            'notes': str          # Optional assignment notes
        }
    ],
    'unassigned_amount': float    # NEW: Remaining unassigned payment amount
}
```

#### Enhanced Invoice Model  
```python
Invoice = {
    'id': str,                    # Unique invoice ID
    'date': datetime,             # Invoice date (interest starts here)
    'description': str,           # Invoice description  
    'amount': float,              # Original invoice amount
    'status': str,                # NEW: 'open', 'partial', 'paid', 'overpaid'
    'total_payments': float,      # NEW: Sum of all payments applied
    'balance': float,             # NEW: amount - total_payments
    'last_payment_date': datetime, # NEW: Most recent payment assignment date
    'interest_periods': [         # NEW: Interest calculation periods
        {
            'start_date': datetime,
            'end_date': datetime,  # None if still accruing
            'principal': float,
            'interest_rate': float,
            'interest_amount': float
        }
    ]
}
```

### Phase 3B: User Interface Enhancements (3-4 hours)

#### 1. Enhanced Payment Dialog
- **Payment Assignment Section**:
  - Dropdown/list of open invoices
  - Amount assignment fields  
  - Assignment date picker
  - Real-time balance calculations
  - Validation for over-assignment

#### 2. Enhanced Invoice Table
- **New Columns**:
  - Status (Open/Partial/Paid/Overpaid) 
  - Balance Remaining
  - Total Interest Accrued
  - Last Payment Date
- **Color Coding**:
  - Green: Fully paid
  - Yellow: Partially paid  
  - Red: Overdue (past grace period)

#### 3. Payment Assignment Management
- **Assignment History View**: Show all payment assignments per invoice
- **Reassignment Capability**: Move payment assignments between invoices
- **Unassigned Payments View**: Show payments not yet assigned to invoices

#### 4. Amortization Table Display
- **Per-Invoice Amortization**: Expandable view showing interest accrual timeline
- **Summary View**: Total interest across all invoices
- **Export Capability**: Export amortization schedules to Excel/PDF

### Phase 3C: Calculation Engine (2-3 hours)

#### 1. Interest Calculation Engine
```python
class InterestCalculator:
    def calculate_invoice_interest(self, invoice, as_of_date, rate_config):
        """Calculate interest for a single invoice up to as_of_date"""
        
    def apply_payment_to_invoice(self, payment, invoice, amount, assignment_date):
        """Apply payment amount to invoice and update interest periods"""
        
    def generate_amortization_schedule(self, invoice):
        """Generate detailed amortization schedule for invoice"""
        
    def calculate_total_interest_due(self, invoices, as_of_date):
        """Calculate total interest across all invoices"""
```

#### 2. Payment Processing Logic
- **FIFO Payment Application**: Optional automatic assignment to oldest invoices first
- **Manual Assignment Validation**: Ensure assignments don't exceed payment amounts
- **Balance Tracking**: Real-time balance updates across invoices and payments

### Phase 3D: Report Generation Enhancement (1 hour)

#### Enhanced Excel/PDF Reports
- **Invoice Detail Report**: Per-invoice amortization with payment history
- **Payment Application Report**: Show how payments were applied across invoices  
- **Interest Summary Report**: Total interest calculations with breakdown
- **Aging Report**: Outstanding balances by invoice age

## Testing Strategy with Playwright Integration

### Automated UI Testing with Playwright

Playwright is **perfect** for this implementation because it can:

1. **Visual Regression Testing**: Ensure UI changes don't break layouts
2. **Complex User Workflows**: Test multi-step payment assignment processes  
3. **Data Validation**: Verify calculations appear correctly in tables
4. **Cross-browser Testing**: Ensure compatibility (if web view added later)
5. **Screenshot Documentation**: Generate visual test documentation

#### Test Scenarios for Playwright

```python
# test_invoice_payment_integration.py
@pytest.mark.playwright
class TestInvoicePaymentAssignment:
    
    def test_create_invoice_and_assign_payment(self, playwright_page):
        """Test complete workflow: create invoice -> create payment -> assign payment"""
        
    def test_partial_payment_assignment(self, playwright_page):
        """Test partial payment reduces balance but continues interest"""
        
    def test_payment_reassignment(self, playwright_page):
        """Test moving payment assignments between invoices"""
        
    def test_amortization_table_display(self, playwright_page):
        """Test amortization table shows correct calculations"""
        
    def test_overpayment_handling(self, playwright_page):
        """Test overpayment creates credit or gets reassigned"""
```

### Manual Test Cases

#### Critical User Journeys
1. **New Project Setup**: Create invoices with different dates, apply payments
2. **Complex Payment Scenarios**: Multiple payments, partial payments, reassignments
3. **Interest Calculation Validation**: Verify calculations match manual computations
4. **Report Generation**: Ensure reports reflect payment assignments accurately

## Implementation Priority

### High Priority (Must Have)
1. Payment-to-invoice assignment functionality
2. Per-invoice interest calculation with payment application
3. Basic amortization table display
4. Payment assignment validation

### Medium Priority (Should Have)  
1. Payment reassignment capability
2. Enhanced invoice status tracking
3. Color-coded invoice status display
4. Unassigned payment management

### Low Priority (Nice to Have)
1. Automated FIFO payment assignment
2. Complex overpayment handling
3. Advanced reporting features
4. Payment history audit trail

## Success Criteria

### Functional Requirements
- ✅ Invoices accrue interest from invoice date until payment assignment
- ✅ Payments can be assigned to specific invoices with dates
- ✅ Interest calculation stops/reduces when payments are applied
- ✅ Amortization tables show accurate per-invoice calculations
- ✅ Reports reflect payment assignments and interest calculations

### Technical Requirements  
- ✅ All existing functionality remains intact
- ✅ Data model supports complex payment scenarios
- ✅ UI is intuitive and validates user input
- ✅ Calculations are mathematically accurate
- ✅ Performance remains acceptable with large datasets

### Testing Requirements
- ✅ Playwright tests cover all critical user workflows
- ✅ Unit tests validate calculation engine accuracy  
- ✅ Integration tests verify data persistence
- ✅ Manual testing confirms user experience quality

## Risk Mitigation

### Technical Risks
- **Calculation Complexity**: Interest calculations with multiple payment dates
  - *Mitigation*: Comprehensive unit testing with known calculation scenarios
- **UI Complexity**: Payment assignment interface could be confusing
  - *Mitigation*: Iterative UI design with user feedback
- **Data Migration**: Existing projects need to support new model
  - *Mitigation*: Backward compatibility and data migration utilities

### Business Risks  
- **Calculation Errors**: Incorrect interest calculations could have legal implications
  - *Mitigation*: External validation against manual calculations
- **User Adoption**: Complex new interface might confuse users
  - *Mitigation*: Clear documentation and intuitive design

## Deliverables

1. **Enhanced Data Models**: Updated Invoice/Payment classes with assignment support
2. **UI Components**: Payment assignment dialogs and enhanced tables
3. **Calculation Engine**: Interest calculation with payment application logic
4. **Amortization Display**: Per-invoice amortization table with payment history
5. **Test Suite**: Comprehensive Playwright + unit tests
6. **Documentation**: User guide for new payment assignment functionality

---

**Next Steps:**
1. Review and approve this enhanced Phase 3 plan
2. Create comprehensive test cases
3. Begin implementation with calculation engine
4. Build UI components with Playwright testing
5. Integrate and validate complete workflow

**Estimated Timeline:**
- Week 1: Data model + calculation engine + core tests
- Week 2: UI implementation + Playwright integration + validation
- Week 3: Report enhancement + final testing + documentation