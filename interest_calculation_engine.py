"""
Core Interest Calculation Engine for Invoice-Payment Assignment System
Handles per-invoice interest calculations with payment assignments
"""

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Optional, Any
import calendar


class InterestCalculationEngine:
    """Core engine for calculating interest on invoices with payment assignments"""
    
    def __init__(self, monthly_rate: float = 0.015, annual_rate: float = 0.18, grace_days: int = 30):
        """
        Initialize calculation engine with interest rates
        
        Args:
            monthly_rate: Monthly interest rate (e.g., 0.015 for 1.5%)
            annual_rate: Annual interest rate (e.g., 0.18 for 18%)
            grace_days: Grace period before interest starts accruing
        """
        self.monthly_rate = Decimal(str(monthly_rate))
        self.annual_rate = Decimal(str(annual_rate))
        self.grace_days = grace_days
        
    def calculate_invoice_interest(self, invoice: Dict[str, Any], as_of_date: str, 
                                 payments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate total interest for an invoice considering all payment assignments
        
        Args:
            invoice: Invoice dictionary with id, date, amount, etc.
            as_of_date: Date to calculate interest through (YYYY-MM-DD)
            payments: List of payments with assignments to this invoice
            
        Returns:
            Dictionary with interest calculation details
        """
        invoice_date = self._parse_date(invoice['date'])
        as_of_date_dt = self._parse_date(as_of_date)
        
        # Apply grace period
        interest_start_date = invoice_date + timedelta(days=self.grace_days)
        if as_of_date_dt <= interest_start_date:
            return {
                'invoice_id': invoice['id'],
                'total_interest': Decimal('0.00'),
                'interest_periods': [],
                'current_balance': Decimal(str(invoice['amount'])),
                'status': 'within_grace_period'
            }
        
        # Get payment assignments for this invoice
        invoice_payments = self._get_invoice_payments(invoice['id'], payments or [])
        
        # CRITICAL: Calculate pre-invoice payments to reduce effective principal
        effective_principal = self._calculate_effective_principal(invoice, invoice_date, invoice_payments)
        
        # Calculate interest periods between payments with effective principal
        interest_periods = self._calculate_interest_periods(
            invoice, interest_start_date, as_of_date_dt, invoice_payments, effective_principal
        )
        
        # Sum total interest
        total_interest = sum(period['interest_amount'] for period in interest_periods)
        
        # Calculate current balance
        total_payments_applied = sum(Decimal(str(payment['assigned_amount'])) 
                                   for payment in invoice_payments)
        current_balance = Decimal(str(invoice['amount'])) - total_payments_applied
        
        return {
            'invoice_id': invoice['id'],
            'total_interest': total_interest,
            'interest_periods': interest_periods,
            'current_balance': current_balance,
            'total_payments_applied': total_payments_applied,
            'status': 'paid' if current_balance <= 0 else 'partial' if total_payments_applied > 0 else 'open'
        }
    
    def _get_invoice_payments(self, invoice_id: str, payments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get all payment assignments for a specific invoice"""
        invoice_payments = []
        
        for payment in payments:
            for assignment in payment.get('assignments', []):
                if assignment['invoice_id'] == invoice_id:
                    invoice_payments.append({
                        'payment_id': payment['id'],
                        'assignment_date': assignment['assignment_date'],
                        'assigned_amount': assignment['assigned_amount'],
                        'notes': assignment.get('notes', '')
                    })
        
        # Sort by assignment date
        invoice_payments.sort(key=lambda x: self._parse_date(x['assignment_date']))
        return invoice_payments
    
    def _calculate_effective_principal(self, invoice: Dict[str, Any], invoice_date: datetime,
                                     invoice_payments: List[Dict[str, Any]]) -> Decimal:
        """
        Calculate effective principal after pre-invoice payments
        CRITICAL: Payments made BEFORE invoice date reduce the principal amount
        """
        original_principal = Decimal(str(invoice['amount']))
        pre_invoice_payments = Decimal('0.00')
        
        for payment in invoice_payments:
            payment_date = self._parse_date(payment['assignment_date'])
            if payment_date < invoice_date:
                # Payment made before invoice date reduces effective principal
                pre_invoice_payments += Decimal(str(payment['assigned_amount']))
        
        effective_principal = max(Decimal('0.00'), original_principal - pre_invoice_payments)
        return effective_principal
    
    def _calculate_interest_periods(self, invoice: Dict[str, Any], interest_start_date: datetime,
                                  as_of_date: datetime, payments: List[Dict[str, Any]], 
                                  effective_principal: Decimal = None) -> List[Dict[str, Any]]:
        """Calculate interest for periods between payments"""
        periods = []
        # Use effective principal (after pre-invoice payments) instead of full invoice amount
        current_principal = effective_principal if effective_principal is not None else Decimal(str(invoice['amount']))
        current_date = interest_start_date
        
        # Add payment dates to create periods - but only for payments AFTER interest starts
        # Pre-invoice payments have already reduced the effective principal
        payment_dates = []
        for p in payments:
            payment_date = self._parse_date(p['assignment_date'])
            if payment_date >= interest_start_date:  # Only payments after interest starts
                payment_dates.append((payment_date, Decimal(str(p['assigned_amount']))))
        payment_dates.sort()  # Sort by date
        
        # Add as_of_date as final period end
        payment_dates.append((as_of_date, Decimal('0')))
        
        for payment_date, payment_amount in payment_dates:
            if current_date < payment_date and current_principal > 0:
                # Calculate interest for this period
                period_interest = self._calculate_period_interest(
                    current_principal, current_date, payment_date
                )
                
                periods.append({
                    'start_date': current_date.strftime('%Y-%m-%d'),
                    'end_date': payment_date.strftime('%Y-%m-%d'),
                    'days': (payment_date - current_date).days,
                    'principal': current_principal,
                    'interest_rate': float(self.monthly_rate),
                    'interest_amount': period_interest
                })
                
            # Apply payment and move to next period
            current_principal = max(Decimal('0'), current_principal - payment_amount)
            current_date = payment_date
            
            # Stop if principal is fully paid
            if current_principal <= 0:
                break
        
        return periods
    
    def _calculate_period_interest(self, principal: Decimal, start_date: datetime, 
                                 end_date: datetime) -> Decimal:
        """Calculate compound interest for a specific period"""
        if start_date >= end_date:
            return Decimal('0.00')
            
        # Calculate the number of months using exact calendar method
        total_days = (end_date - start_date).days
        months = Decimal(str(total_days)) / Decimal('30.4375')  # 365.25/12 for leap year average
        
        # Compound interest formula: A = P(1 + r)^n - P
        compound_amount = principal * ((Decimal('1') + self.monthly_rate) ** months)
        interest = compound_amount - principal
        
        return interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def apply_payment_to_invoice(self, invoice: Dict[str, Any], payment: Dict[str, Any],
                               assigned_amount: float, assignment_date: str,
                               notes: str = "") -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Apply payment assignment to invoice and update both records
        
        Args:
            invoice: Invoice dictionary to update
            payment: Payment dictionary to update  
            assigned_amount: Amount to assign from payment to invoice
            assignment_date: Date when assignment is made
            notes: Optional notes for the assignment
            
        Returns:
            Tuple of (updated_invoice, updated_payment)
        """
        # Validation
        assigned_decimal = Decimal(str(assigned_amount))
        unassigned = Decimal(str(payment.get('unassigned_amount', payment['amount'])))
        
        if assigned_decimal > unassigned:
            raise ValueError(f"Assignment amount ${assigned_decimal} exceeds unassigned payment amount ${unassigned}")
            
        invoice_balance = Decimal(str(invoice.get('balance', invoice['amount'])))
        if assigned_decimal > invoice_balance:
            raise ValueError(f"Assignment amount ${assigned_decimal} exceeds invoice balance ${invoice_balance}")
        
        # Create assignment record
        assignment = {
            'invoice_id': invoice['id'],
            'assigned_amount': float(assigned_decimal),
            'assignment_date': assignment_date,
            'notes': notes
        }
        
        # Update payment
        updated_payment = payment.copy()
        if 'assignments' not in updated_payment:
            updated_payment['assignments'] = []
        updated_payment['assignments'].append(assignment)
        
        new_unassigned = unassigned - assigned_decimal
        updated_payment['unassigned_amount'] = float(new_unassigned)
        
        # Update invoice
        updated_invoice = invoice.copy()
        current_payments = Decimal(str(invoice.get('total_payments', 0)))
        updated_invoice['total_payments'] = float(current_payments + assigned_decimal)
        
        new_balance = Decimal(str(invoice['amount'])) - (current_payments + assigned_decimal)
        updated_invoice['balance'] = float(new_balance)
        
        # Update status
        if new_balance <= 0:
            updated_invoice['status'] = 'paid'
        elif current_payments + assigned_decimal > 0:
            updated_invoice['status'] = 'partial'
        else:
            updated_invoice['status'] = 'open'
            
        updated_invoice['last_payment_date'] = assignment_date
        
        return updated_invoice, updated_payment
    
    def generate_amortization_schedule(self, invoice: Dict[str, Any], payments: List[Dict[str, Any]], 
                                     as_of_date: str) -> List[Dict[str, Any]]:
        """
        Generate detailed amortization schedule for an invoice
        
        Returns:
            List of amortization rows showing principal, interest, payments, and balances
        """
        calculation_result = self.calculate_invoice_interest(invoice, as_of_date, payments)
        schedule = []
        
        running_balance = Decimal(str(invoice['amount']))
        cumulative_interest = Decimal('0.00')
        
        for period in calculation_result['interest_periods']:
            # Add interest accrual row
            period_interest = Decimal(str(period['interest_amount']))
            cumulative_interest += period_interest
            
            schedule.append({
                'date': period['end_date'],
                'type': 'interest_accrual',
                'description': f"Interest accrual ({period['days']} days)",
                'principal': float(period['principal']),
                'interest': float(period_interest),
                'payment': 0.00,
                'balance': float(running_balance + cumulative_interest)
            })
            
            # Check for payments on this date
            invoice_payments = self._get_invoice_payments(invoice['id'], payments)
            for payment in invoice_payments:
                if payment['assignment_date'] == period['end_date']:
                    payment_amount = Decimal(str(payment['assigned_amount']))
                    
                    # Payment row
                    schedule.append({
                        'date': payment['assignment_date'],
                        'type': 'payment',
                        'description': f"Payment applied (ID: {payment['payment_id']})",
                        'principal': 0.00,
                        'interest': 0.00,
                        'payment': float(payment_amount),
                        'balance': float(running_balance + cumulative_interest - payment_amount)
                    })
                    
                    running_balance = running_balance + cumulative_interest - payment_amount
                    cumulative_interest = Decimal('0.00')  # Reset after payment
        
        return schedule
    
    def calculate_total_project_interest(self, project: Dict[str, Any], as_of_date: str) -> Dict[str, Any]:
        """Calculate total interest across all invoices in a project"""
        invoices = project.get('invoices', [])
        payments = project.get('payments', [])
        
        total_interest = Decimal('0.00')
        total_principal = Decimal('0.00')
        total_payments = Decimal('0.00')
        invoice_details = []
        
        for invoice in invoices:
            result = self.calculate_invoice_interest(invoice, as_of_date, payments)
            
            invoice_interest = result['total_interest']
            invoice_principal = Decimal(str(invoice['amount']))
            invoice_payments = result['total_payments_applied']
            
            total_interest += invoice_interest
            total_principal += invoice_principal
            total_payments += invoice_payments
            
            invoice_details.append({
                'invoice_id': invoice['id'],
                'description': invoice['description'],
                'principal': float(invoice_principal),
                'interest': float(invoice_interest),
                'payments': float(invoice_payments),
                'balance': float(result['current_balance']),
                'status': result['status']
            })
        
        return {
            'total_principal': float(total_principal),
            'total_interest': float(total_interest),
            'total_payments': float(total_payments),
            'total_due': float(total_principal + total_interest - total_payments),
            'invoice_details': invoice_details,
            'calculation_date': as_of_date
        }
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string in YYYY-MM-DD format"""
        if isinstance(date_str, datetime):
            return date_str
        return datetime.strptime(date_str, '%Y-%m-%d')


# Convenience functions for direct use
def calculate_simple_interest(principal: float, annual_rate: float, months: int) -> float:
    """Calculate simple interest for validation purposes"""
    return principal * (annual_rate / 12) * months


def calculate_compound_interest(principal: float, monthly_rate: float, months: int) -> float:
    """Calculate compound interest for validation purposes"""
    return principal * ((1 + monthly_rate) ** months) - principal


# Test/validation functions
def validate_calculation_accuracy():
    """Run validation tests on calculation engine"""
    engine = InterestCalculationEngine(monthly_rate=0.015)
    
    # Test 1: Exact 12 month test using perfect dates
    principal = 10000.0
    monthly_rate = 0.015
    expected = calculate_compound_interest(principal, monthly_rate, 12)
    
    # Use exact year boundary for 12 months
    test_invoice = {
        'id': 'TEST-001',
        'date': '2023-01-01',
        'amount': principal,
        'status': 'open'
    }
    
    # Calculate with one year exactly
    result = engine.calculate_invoice_interest(test_invoice, '2024-01-01')  # Exactly 365 days = ~12 months
    actual = float(result['total_interest'])
    
    print(f"Validation Test 1 - Compound Interest (365 days):")
    print(f"  Principal: ${principal:,.2f}")
    print(f"  Expected (12 months): ${expected:.2f}")
    print(f"  Actual (365 days): ${actual:.2f}")
    print(f"  Difference: ${abs(expected - actual):.2f}")
    
    # Test 2: Test with payment assignment
    print(f"\nValidation Test 2 - Payment Assignment:")
    
    # Create payment that pays off invoice after 6 months
    payments = [{
        'id': 'PAY-001',
        'date': '2023-07-01',
        'amount': 12000.0,
        'assignments': [{
            'invoice_id': 'TEST-001',
            'assigned_amount': 12000.0,  # More than enough to cover principal + interest
            'assignment_date': '2023-07-01',
            'notes': 'Full payment after 6 months'
        }],
        'unassigned_amount': 0.0
    }]
    
    result_with_payment = engine.calculate_invoice_interest(test_invoice, '2024-01-01', payments)
    actual_with_payment = float(result_with_payment['total_interest'])
    
    # Expected: 6 months of compound interest
    expected_6_months = calculate_compound_interest(principal, monthly_rate, 6)
    
    print(f"  Expected (6 months): ${expected_6_months:.2f}")
    print(f"  Actual with payment: ${actual_with_payment:.2f}")
    print(f"  Difference: ${abs(expected_6_months - actual_with_payment):.2f}")
    
    test1_pass = abs(expected - actual) < 50.0  # Allow for calendar differences
    test2_pass = abs(expected_6_months - actual_with_payment) < 50.0
    
    overall_status = "PASS" if test1_pass and test2_pass else "FAIL"
    print(f"\nOverall Status: {overall_status}")
    
    return test1_pass and test2_pass


if __name__ == "__main__":
    # Run validation
    print("Interest Calculation Engine Validation")
    print("=" * 50)
    validate_calculation_accuracy()