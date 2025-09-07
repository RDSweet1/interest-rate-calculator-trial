"""
Debug interest calculation differences to ensure mathematical accuracy
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from interest_calculation_engine import InterestCalculationEngine, calculate_compound_interest

def debug_calculation_difference():
    print("DEBUGGING INTEREST CALCULATION DIFFERENCES")
    print("=" * 60)
    
    # Test parameters
    principal = 10000.0
    monthly_rate = 0.015
    months = 12
    
    # Method 1: Simple compound formula
    expected = calculate_compound_interest(principal, monthly_rate, months)
    print(f"Method 1 (Simple): ${expected:.2f}")
    
    # Method 2: Engine calculation with exact 12 months
    engine = InterestCalculationEngine(monthly_rate=monthly_rate)
    
    # Create test invoice with exact dates
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)  # 364 days
    
    test_invoice = {
        'id': 'TEST-001', 
        'date': '2023-01-01',
        'amount': principal,
        'status': 'open'
    }
    
    result = engine.calculate_invoice_interest(test_invoice, '2023-12-31')
    actual = float(result['total_interest'])
    print(f"Method 2 (Engine): ${actual:.2f}")
    
    # Check the calculation details
    if result['interest_periods']:
        period = result['interest_periods'][0]
        days = period['days']
        months_calc = days / 30.44
        print(f"Days: {days}")
        print(f"Months calculated: {months_calc:.4f}")
        print(f"Expected months: {months}")
        
        # Manual calculation with same method
        principal_decimal = Decimal(str(principal))
        rate_decimal = Decimal(str(monthly_rate))
        months_decimal = Decimal(str(months_calc))
        
        compound_amount = principal_decimal * ((Decimal('1') + rate_decimal) ** months_decimal)
        manual_interest = compound_amount - principal_decimal
        print(f"Manual with engine method: ${float(manual_interest):.2f}")
    
    # Method 3: Try with exactly 12 months (365 days)
    engine_365 = InterestCalculationEngine(monthly_rate=monthly_rate)
    test_invoice_365 = {
        'id': 'TEST-365',
        'date': '2023-01-01', 
        'amount': principal,
        'status': 'open'
    }
    result_365 = engine_365.calculate_invoice_interest(test_invoice_365, '2024-01-01')  # Exactly 365 days
    actual_365 = float(result_365['total_interest'])
    print(f"Method 3 (365 days): ${actual_365:.2f}")
    
    if result_365['interest_periods']:
        period_365 = result_365['interest_periods'][0]
        days_365 = period_365['days']
        months_365 = days_365 / 30.44
        print(f"Days (365): {days_365}")
        print(f"Months (365): {months_365:.4f}")
    
    # The issue might be the days/month conversion
    print("\nTesting different day-to-month conversions:")
    conversions = [
        ("30 days/month", 30),
        ("30.44 days/month (avg)", 30.44),
        ("365/12 days/month", 365/12),
        ("Exact months", 12)
    ]
    
    for name, divisor in conversions:
        if name == "Exact months":
            months_test = 12
        else:
            months_test = 365 / divisor
            
        interest_test = calculate_compound_interest(principal, monthly_rate, months_test)
        print(f"{name}: {months_test:.4f} months = ${interest_test:.2f}")

if __name__ == "__main__":
    debug_calculation_difference()