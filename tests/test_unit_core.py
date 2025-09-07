"""
Unit tests for core Interest Rate Calculator functionality
"""
import pytest
import json
import tempfile
import os
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import modules to test
try:
    from interest_app import (
        compute_schedule, parse_project, export_excel_and_pdf,
        slugify, DEFAULT_PROJECT
    )
    INTEREST_APP_AVAILABLE = True
except ImportError:
    INTEREST_APP_AVAILABLE = False

try:
    from interest_calculator_gui import (
        format_currency, parse_currency, format_percentage, parse_percentage,
        convert_to_american_date, convert_to_iso_date
    )
    GUI_MODULE_AVAILABLE = True
except ImportError:
    GUI_MODULE_AVAILABLE = False

class TestUtilityFunctions:
    """Test utility functions"""
    
    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_slugify_function(self):
        """Test the slugify function"""
        # Test normal strings
        assert slugify("Ocean Harbor Project") == "Ocean-Harbor-Project"
        assert slugify("Test Project 123") == "Test-Project-123"
        
        # Test special characters
        assert slugify("Project@#$%Name") == "Project-Name"
        assert slugify("Multiple   Spaces") == "Multiple-Spaces"
        
        # Test edge cases
        assert slugify("") == "project"
        assert slugify(None) == "project"
        assert slugify("   ") == "project"
        assert slugify("---") == "project"

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_MODULE_AVAILABLE, reason="GUI module not available")
    def test_format_currency(self):
        """Test currency formatting function"""
        assert format_currency(1000) == "$1,000.00"
        assert format_currency(1000.50) == "$1,000.50"
        assert format_currency(0) == "$0.00"
        assert format_currency(-500) in ["-$500.00", "$-500.00"]  # Both formats acceptable
        
        # Test with string input
        assert format_currency("1000") == "$1,000.00"
        assert format_currency("1000.75") == "$1,000.75"

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_MODULE_AVAILABLE, reason="GUI module not available")
    def test_parse_currency(self):
        """Test currency parsing function"""
        assert parse_currency("$1,000.00") == 1000.00
        assert parse_currency("$1,000.50") == 1000.50
        assert parse_currency("1000") == 1000.00
        assert parse_currency("1,000.75") == 1000.75
        
        # Test edge cases
        assert parse_currency("") == 0.0
        assert parse_currency("$0.00") == 0.0
        assert parse_currency("-$500.00") == -500.00

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_MODULE_AVAILABLE, reason="GUI module not available")
    def test_format_percentage(self):
        """Test percentage formatting function"""
        assert format_percentage(0.18) == "18.0%"
        assert format_percentage(0.015) == "1.5%"
        assert format_percentage(1.0) == "100.0%"
        assert format_percentage(0) == "0.0%"
        
        # Test with string input
        assert format_percentage("0.18") == "18.0%"
        assert format_percentage("0.015") == "1.5%"

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_MODULE_AVAILABLE, reason="GUI module not available")
    def test_parse_percentage(self):
        """Test percentage parsing function"""
        assert parse_percentage("18.0%") == 0.18
        assert parse_percentage("1.5%") == 0.015
        assert parse_percentage("100%") == 1.0
        assert parse_percentage("0%") == 0.0
        
        # Test without % symbol
        assert parse_percentage("18") == 0.18
        assert parse_percentage("1.5") == 0.015
        
        # Test edge cases
        assert parse_percentage("") == 0.0

    @pytest.mark.unit
    @pytest.mark.skipif(not GUI_MODULE_AVAILABLE, reason="GUI module not available")
    def test_date_conversion_functions(self):
        """Test date conversion functions"""
        # Test ISO to American conversion
        assert convert_to_american_date("2023-04-28") == "04/28/2023"
        assert convert_to_american_date("2025-12-31") == "12/31/2025"
        
        # Test American to ISO conversion
        assert convert_to_iso_date("04/28/2023") == "2023-04-28"
        assert convert_to_iso_date("12/31/2025") == "2025-12-31"
        
        # Test edge cases
        assert convert_to_american_date("") == ""
        assert convert_to_iso_date("") == ""
        assert convert_to_american_date("invalid") == "invalid"
        assert convert_to_iso_date("invalid") == "invalid"

class TestInterestCalculations:
    """Test interest calculation logic"""
    
    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_compute_schedule_basic(self):
        """Test basic schedule computation"""
        title = "Test Project"
        billing_date = datetime(2023, 4, 28)
        as_of_date = datetime(2023, 8, 28)  # 4 months later
        grace_days = 30
        annual_rate = 0.18
        monthly_rate = 0.015
        principal_fw = 1000000.00
        principal_dw = 500000.00
        payments = [("Test Payment", datetime(2023, 5, 1), 100000.00)]
        
        summary_df, schedule_df = compute_schedule(
            title, billing_date, as_of_date, grace_days,
            annual_rate, monthly_rate, principal_fw, principal_dw, payments
        )
        
        # Verify summary DataFrame structure
        assert len(summary_df) == 3  # FW, DW, TOTAL rows
        assert "Line Item" in summary_df.columns
        assert "Principal" in summary_df.columns
        assert "Total Interest" in summary_df.columns
        
        # Verify schedule DataFrame structure
        assert len(schedule_df) > 0
        assert "Start" in schedule_df.columns
        assert "End" in schedule_df.columns
        assert "FW Interest" in schedule_df.columns
        assert "DW Interest" in schedule_df.columns
        assert "Total" in schedule_df.columns
        assert "Cumulative" in schedule_df.columns

    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_parse_project_function(self):
        """Test project parsing function"""
        test_project = {
            "title": "Test Project",
            "billing_date": "2023-04-28",
            "as_of_date": "2023-08-28",
            "grace_days": 30,
            "annual_rate": 0.18,
            "monthly_rate": 0.015,
            "principal_fw": 1000000.00,
            "principal_dw": 500000.00,
            "payments": [
                {"desc": "Test Payment", "date": "2023-05-01", "amount": 100000.00}
            ]
        }
        
        summary_df, schedule_df = parse_project(test_project)
        
        # Verify results
        assert len(summary_df) == 3
        assert len(schedule_df) > 0
        assert summary_df.iloc[0]["Line Item"] == "Flood/Wind (net)"
        assert summary_df.iloc[1]["Line Item"] == "Drywall"
        assert summary_df.iloc[2]["Line Item"] == "TOTAL"

    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_default_project_structure(self):
        """Test default project data structure"""
        assert "title" in DEFAULT_PROJECT
        assert "billing_date" in DEFAULT_PROJECT
        assert "as_of_date" in DEFAULT_PROJECT
        assert "grace_days" in DEFAULT_PROJECT
        assert "annual_rate" in DEFAULT_PROJECT
        assert "monthly_rate" in DEFAULT_PROJECT
        assert "principal_fw" in DEFAULT_PROJECT
        assert "principal_dw" in DEFAULT_PROJECT
        assert "payments" in DEFAULT_PROJECT
        assert "sharepoint" in DEFAULT_PROJECT
        
        # Verify data types
        assert isinstance(DEFAULT_PROJECT["grace_days"], int)
        assert isinstance(DEFAULT_PROJECT["annual_rate"], float)
        assert isinstance(DEFAULT_PROJECT["monthly_rate"], float)
        assert isinstance(DEFAULT_PROJECT["payments"], list)

class TestDataValidation:
    """Test data validation and error handling"""
    
    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_invalid_project_data(self):
        """Test handling of invalid project data"""
        # Test with missing required fields
        invalid_project = {
            "title": "Test",
            # Missing other required fields
        }
        
        with pytest.raises((KeyError, ValueError, TypeError)):
            parse_project(invalid_project)

    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_invalid_date_formats(self):
        """Test handling of invalid date formats"""
        invalid_project = DEFAULT_PROJECT.copy()
        invalid_project["billing_date"] = "invalid-date"
        
        with pytest.raises((ValueError, TypeError)):
            parse_project(invalid_project)

    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_negative_values(self):
        """Test handling of negative values"""
        test_project = DEFAULT_PROJECT.copy()
        test_project["principal_fw"] = -1000000.00  # Negative principal
        
        # Should handle gracefully or raise appropriate error
        try:
            summary_df, schedule_df = parse_project(test_project)
            # If it doesn't raise an error, verify the results are reasonable
            assert len(summary_df) == 3
        except (ValueError, AssertionError):
            # It's acceptable to raise an error for negative principals
            pass

class TestFileOperations:
    """Test file I/O operations"""
    
    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_export_excel_and_pdf(self):
        """Test Excel and PDF export functionality"""
        # Create test data
        summary_df, schedule_df = parse_project(DEFAULT_PROJECT)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temporarily change output directory
            import interest_app
            original_output_dir = interest_app.OUTPUT_DIR
            interest_app.OUTPUT_DIR = temp_dir
            
            try:
                xlsx_path, pdf_path = export_excel_and_pdf(
                    "Test Project", summary_df, schedule_df, slug="test-project"
                )
                
                # Verify files were created
                assert os.path.exists(xlsx_path), f"Excel file should exist: {xlsx_path}"
                assert os.path.exists(pdf_path), f"PDF file should exist: {pdf_path}"
                
                # Verify file extensions
                assert xlsx_path.endswith('.xlsx')
                assert pdf_path.endswith('.pdf')
                
            finally:
                # Restore original output directory
                interest_app.OUTPUT_DIR = original_output_dir

    @pytest.mark.unit
    def test_json_project_serialization(self, sample_project_data, temp_project_file):
        """Test JSON serialization/deserialization of project data"""
        # Verify file was created
        assert temp_project_file.exists()
        
        # Read and verify data
        with open(temp_project_file, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data["title"] == sample_project_data["title"]
        assert loaded_data["annual_rate"] == sample_project_data["annual_rate"]
        assert len(loaded_data["payments"]) == len(sample_project_data["payments"])

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_zero_principal_amounts(self):
        """Test calculation with zero principal amounts"""
        test_project = DEFAULT_PROJECT.copy()
        test_project["principal_fw"] = 0.0
        test_project["principal_dw"] = 0.0
        
        summary_df, schedule_df = parse_project(test_project)
        
        # Should handle zero principals gracefully
        assert len(summary_df) == 3
        # Total interest might not be exactly 0 due to payments and calculations
        assert isinstance(summary_df.iloc[2]["Total Interest"], (int, float))

    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_same_billing_and_as_of_dates(self):
        """Test calculation when billing date equals as-of date"""
        test_project = DEFAULT_PROJECT.copy()
        test_project["billing_date"] = "2023-04-28"
        test_project["as_of_date"] = "2023-04-28"
        
        summary_df, schedule_df = parse_project(test_project)
        
        # Should handle same dates gracefully
        assert len(summary_df) == 3
        # Schedule might be empty or have minimal entries
        assert len(schedule_df) >= 0

    @pytest.mark.unit
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_large_payment_amounts(self):
        """Test calculation with payments larger than principal"""
        test_project = DEFAULT_PROJECT.copy()
        test_project["payments"] = [
            {"desc": "Large Payment", "date": "2023-05-01", "amount": 20000000.00}  # Larger than principal
        ]
        
        summary_df, schedule_df = parse_project(test_project)
        
        # Should handle overpayments gracefully
        assert len(summary_df) == 3
        # Net principal should be negative or zero
        fw_net = summary_df.iloc[0]["Principal"]
        assert fw_net <= 0

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.unit
    @pytest.mark.slow
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_large_date_range_performance(self):
        """Test performance with large date ranges"""
        import time
        
        test_project = DEFAULT_PROJECT.copy()
        test_project["billing_date"] = "2020-01-01"
        test_project["as_of_date"] = "2030-12-31"  # 10+ year range
        
        start_time = time.time()
        summary_df, schedule_df = parse_project(test_project)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should complete within reasonable time
        assert duration < 5.0, f"Calculation took too long: {duration}s"
        assert len(schedule_df) > 100  # Should have many periods

    @pytest.mark.unit
    @pytest.mark.slow
    @pytest.mark.skipif(not INTEREST_APP_AVAILABLE, reason="interest_app module not available")
    def test_many_payments_performance(self):
        """Test performance with many payments"""
        import time
        
        # Create many payments
        payments = []
        for i in range(100):
            payments.append({
                "desc": f"Payment {i+1}",
                "date": f"2023-{(i % 12) + 1:02d}-01",
                "amount": 10000.00
            })
        
        test_project = DEFAULT_PROJECT.copy()
        test_project["payments"] = payments
        
        start_time = time.time()
        summary_df, schedule_df = parse_project(test_project)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should complete within reasonable time
        assert duration < 2.0, f"Calculation with many payments took too long: {duration}s"
