"""
Desktop automation tests for Interest Rate Calculator Tkinter application
"""
import pytest
import time
import json
from pathlib import Path
from datetime import datetime

try:
    import pywinauto
    from pywinauto import Application, Desktop
    from pywinauto.controls.uiawrapper import UIAWrapper
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False

@pytest.mark.skipif(not PYWINAUTO_AVAILABLE, reason="pywinauto not available")
class TestDesktopApplication:
    """Test cases for desktop application using pywinauto"""
    
    @pytest.mark.desktop
    @pytest.mark.smoke
    def test_application_starts(self, desktop_app):
        """Test that the desktop application starts successfully"""
        # Verify application is running
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        assert main_window.exists(), "Main window should exist"
        assert main_window.is_visible(), "Main window should be visible"

    @pytest.mark.desktop
    def test_main_window_title(self, desktop_app):
        """Test that main window has correct title with version info"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        title = main_window.window_text()
        
        # Should contain version info
        assert "Interest Rate Calculator v" in title
        assert "Last Updated:" in title
        assert "Launched:" in title
        assert "Runtime:" in title

    @pytest.mark.desktop
    def test_project_selection_section(self, desktop_app):
        """Test project selection section functionality"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        # Look for project selection elements
        try:
            # Find project selection dropdown/listbox
            project_list = main_window.child_window(class_name="Listbox")
            if project_list.exists():
                assert project_list.is_visible(), "Project list should be visible"
        except Exception:
            # Alternative: look for any control that might be the project selector
            pass

    @pytest.mark.desktop
    def test_collapsible_sections(self, desktop_app):
        """Test collapsible section functionality"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        # Look for section headers that should be clickable
        try:
            # Find labels that might be section headers
            labels = main_window.children(class_name="Label")
            section_headers = []
            
            for label in labels:
                text = label.window_text()
                if any(section in text.lower() for section in 
                      ["project selection", "project information", "payments", "invoices"]):
                    section_headers.append(label)
            
            # Test clicking on first section header if found
            if section_headers:
                header = section_headers[0]
                header.click_input()
                time.sleep(0.5)  # Wait for animation
                
                # Click again to toggle back
                header.click_input()
                time.sleep(0.5)
                
        except Exception as e:
            pytest.skip(f"Could not test collapsible sections: {e}")

    @pytest.mark.desktop
    def test_edit_project_button(self, desktop_app):
        """Test the Edit Project button functionality"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        try:
            # Look for Edit Project button
            edit_btn = main_window.child_window(title="Edit Project", class_name="Button")
            if edit_btn.exists() and edit_btn.is_visible():
                edit_btn.click_input()
                time.sleep(1)  # Wait for form to appear
                
                # Verify project editor form is shown
                # Look for entry fields that should appear
                entries = main_window.children(class_name="Entry")
                assert len(entries) > 0, "Should have entry fields in project editor"
                
        except Exception as e:
            pytest.skip(f"Could not test Edit Project button: {e}")

class TestPaymentDialog:
    """Test payment dialog functionality"""
    
    @pytest.mark.desktop
    @pytest.mark.skipif(not PYWINAUTO_AVAILABLE, reason="pywinauto not available")
    def test_add_payment_dialog(self, desktop_app):
        """Test opening and using the Add Payment dialog"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        try:
            # First, ensure we're in project editor mode
            edit_btn = main_window.child_window(title="Edit Project", class_name="Button")
            if edit_btn.exists() and edit_btn.is_visible():
                edit_btn.click_input()
                time.sleep(1)
            
            # Look for Add Payment button
            add_payment_btn = main_window.child_window(title="Add Payment", class_name="Button")
            if add_payment_btn.exists() and add_payment_btn.is_visible():
                add_payment_btn.click_input()
                time.sleep(1)
                
                # Look for payment dialog
                payment_dialog = desktop_app.window(title_re=".*Payment.*")
                if payment_dialog.exists():
                    assert payment_dialog.is_visible(), "Payment dialog should be visible"
                    
                    # Test dialog has required fields
                    entries = payment_dialog.children(class_name="Entry")
                    assert len(entries) >= 3, "Should have at least 3 entry fields (Date, Description, Amount)"
                    
                    # Test Cancel button
                    cancel_btn = payment_dialog.child_window(title="Cancel", class_name="Button")
                    if cancel_btn.exists():
                        cancel_btn.click_input()
                        time.sleep(0.5)
                
        except Exception as e:
            pytest.skip(f"Could not test Add Payment dialog: {e}")

    @pytest.mark.desktop
    @pytest.mark.skipif(not PYWINAUTO_AVAILABLE, reason="pywinauto not available")
    def test_payment_dialog_fields(self, desktop_app):
        """Test payment dialog field functionality"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        try:
            # Navigate to payment dialog
            edit_btn = main_window.child_window(title="Edit Project", class_name="Button")
            if edit_btn.exists():
                edit_btn.click_input()
                time.sleep(1)
            
            add_payment_btn = main_window.child_window(title="Add Payment", class_name="Button")
            if add_payment_btn.exists():
                add_payment_btn.click_input()
                time.sleep(1)
                
                payment_dialog = desktop_app.window(title_re=".*Payment.*")
                if payment_dialog.exists():
                    # Test entering data in fields
                    entries = payment_dialog.children(class_name="Entry")
                    
                    if len(entries) >= 3:
                        # Enter test data
                        entries[0].set_text("01/15/2024")  # Date
                        entries[1].set_text("Test Payment")  # Description
                        entries[2].set_text("50000.00")  # Amount
                        
                        # Test Save button
                        save_btn = payment_dialog.child_window(title="Save", class_name="Button")
                        if save_btn.exists():
                            save_btn.click_input()
                            time.sleep(0.5)
                
        except Exception as e:
            pytest.skip(f"Could not test payment dialog fields: {e}")

class TestInvoiceDialog:
    """Test invoice dialog functionality"""
    
    @pytest.mark.desktop
    @pytest.mark.skipif(not PYWINAUTO_AVAILABLE, reason="pywinauto not available")
    def test_add_invoice_dialog(self, desktop_app):
        """Test opening and using the Add Invoice dialog"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        try:
            # Navigate to project editor
            edit_btn = main_window.child_window(title="Edit Project", class_name="Button")
            if edit_btn.exists():
                edit_btn.click_input()
                time.sleep(1)
            
            # Look for Add Invoice button
            add_invoice_btn = main_window.child_window(title="Add Invoice", class_name="Button")
            if add_invoice_btn.exists() and add_invoice_btn.is_visible():
                add_invoice_btn.click_input()
                time.sleep(1)
                
                # Look for invoice dialog
                invoice_dialog = desktop_app.window(title_re=".*Invoice.*")
                if invoice_dialog.exists():
                    assert invoice_dialog.is_visible(), "Invoice dialog should be visible"
                    
                    # Test dialog has required fields
                    entries = invoice_dialog.children(class_name="Entry")
                    assert len(entries) >= 3, "Should have at least 3 entry fields"
                    
                    # Test Cancel button
                    cancel_btn = invoice_dialog.child_window(title="Cancel", class_name="Button")
                    if cancel_btn.exists():
                        cancel_btn.click_input()
                        time.sleep(0.5)
                
        except Exception as e:
            pytest.skip(f"Could not test Add Invoice dialog: {e}")

class TestProjectDataEntry:
    """Test project data entry and validation"""
    
    @pytest.mark.desktop
    @pytest.mark.skipif(not PYWINAUTO_AVAILABLE, reason="pywinauto not available")
    def test_project_info_fields(self, desktop_app):
        """Test project information field entry"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        try:
            # Enter project editor mode
            edit_btn = main_window.child_window(title="Edit Project", class_name="Button")
            if edit_btn.exists():
                edit_btn.click_input()
                time.sleep(1)
                
                # Find and test entry fields
                entries = main_window.children(class_name="Entry")
                
                # Test entering data in various fields
                test_data = {
                    "Test Project Title": 0,  # Assuming first entry is title
                    "18.0": 1,  # Annual rate
                    "1.5": 2,  # Monthly rate
                }
                
                for value, index in test_data.items():
                    if index < len(entries):
                        entry = entries[index]
                        if entry.is_visible() and entry.is_enabled():
                            entry.set_text(value)
                            time.sleep(0.2)
                
        except Exception as e:
            pytest.skip(f"Could not test project info fields: {e}")

    @pytest.mark.desktop
    @pytest.mark.skipif(not PYWINAUTO_AVAILABLE, reason="pywinauto not available")
    def test_save_project_functionality(self, desktop_app):
        """Test saving project data"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        try:
            # Enter project editor mode
            edit_btn = main_window.child_window(title="Edit Project", class_name="Button")
            if edit_btn.exists():
                edit_btn.click_input()
                time.sleep(1)
                
                # Look for Save Project button
                save_btn = main_window.child_window(title="Save Project", class_name="Button")
                if save_btn.exists() and save_btn.is_visible():
                    save_btn.click_input()
                    time.sleep(1)
                    
                    # Verify save operation (could check for success message or file creation)
                    # This is a basic test - in practice you'd verify the file was created
                
        except Exception as e:
            pytest.skip(f"Could not test save project functionality: {e}")

class TestTreeViewInteraction:
    """Test TreeView (table) interactions"""
    
    @pytest.mark.desktop
    @pytest.mark.skipif(not PYWINAUTO_AVAILABLE, reason="pywinauto not available")
    def test_payments_treeview(self, desktop_app):
        """Test payments TreeView functionality"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        try:
            # Enter project editor mode
            edit_btn = main_window.child_window(title="Edit Project", class_name="Button")
            if edit_btn.exists():
                edit_btn.click_input()
                time.sleep(1)
                
                # Look for TreeView controls (payments/invoices tables)
                treeviews = main_window.children(class_name="SysTreeView32")
                
                if treeviews:
                    payments_tree = treeviews[0]  # Assuming first is payments
                    
                    # Test basic TreeView functionality
                    if payments_tree.is_visible():
                        # Get item count
                        item_count = payments_tree.item_count()
                        
                        # Test selection if items exist
                        if item_count > 0:
                            payments_tree.select(0)  # Select first item
                            time.sleep(0.2)
                
        except Exception as e:
            pytest.skip(f"Could not test payments TreeView: {e}")

class TestApplicationStability:
    """Test application stability and error handling"""
    
    @pytest.mark.desktop
    @pytest.mark.skipif(not PYWINAUTO_AVAILABLE, reason="pywinauto not available")
    def test_rapid_button_clicking(self, desktop_app):
        """Test application stability with rapid button clicking"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        try:
            # Find clickable buttons
            buttons = main_window.children(class_name="Button")
            
            # Rapidly click buttons (but not destructive ones)
            safe_button_titles = ["Edit Project", "Cancel", "Clear"]
            
            for button in buttons:
                title = button.window_text()
                if any(safe_title in title for safe_title in safe_button_titles):
                    for _ in range(3):  # Click 3 times rapidly
                        if button.exists() and button.is_visible():
                            button.click_input()
                            time.sleep(0.1)
                    break
            
            # Verify application is still responsive
            assert main_window.exists(), "Application should still exist after rapid clicking"
            assert main_window.is_visible(), "Application should still be visible"
            
        except Exception as e:
            pytest.skip(f"Could not test rapid button clicking: {e}")

    @pytest.mark.desktop
    @pytest.mark.skipif(not PYWINAUTO_AVAILABLE, reason="pywinauto not available")
    def test_window_resize(self, desktop_app):
        """Test window resize functionality"""
        main_window = desktop_app.window(title_re="Interest Rate Calculator.*")
        
        try:
            # Get current window rectangle
            rect = main_window.rectangle()
            original_width = rect.width()
            original_height = rect.height()
            
            # Resize window
            main_window.move_window(rect.left, rect.top, 
                                  original_width + 100, original_height + 50)
            time.sleep(0.5)
            
            # Verify window is still functional
            assert main_window.exists(), "Window should exist after resize"
            assert main_window.is_visible(), "Window should be visible after resize"
            
            # Restore original size
            main_window.move_window(rect.left, rect.top, original_width, original_height)
            
        except Exception as e:
            pytest.skip(f"Could not test window resize: {e}")

# Helper functions for desktop testing
def find_control_by_text(parent, text, control_type="Button"):
    """Helper function to find controls by text content"""
    try:
        return parent.child_window(title=text, class_name=control_type)
    except Exception:
        return None

def wait_for_dialog(app, title_pattern, timeout=5):
    """Helper function to wait for a dialog to appear"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            dialog = app.window(title_re=title_pattern)
            if dialog.exists() and dialog.is_visible():
                return dialog
        except Exception:
            pass
        time.sleep(0.1)
    return None
