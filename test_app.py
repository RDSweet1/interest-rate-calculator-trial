#!/usr/bin/env python3
"""
Test script to diagnose application startup issues
"""

import sys
import traceback

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except Exception as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    try:
        from tkinter import ttk, messagebox
        print("✓ tkinter.ttk and messagebox imported successfully")
    except Exception as e:
        print(f"✗ tkinter.ttk import failed: {e}")
        return False
    
    try:
        import json
        print("✓ json imported successfully")
    except Exception as e:
        print(f"✗ json import failed: {e}")
        return False
    
    try:
        import os
        print("✓ os imported successfully")
    except Exception as e:
        print(f"✗ os import failed: {e}")
        return False
    
    try:
        from datetime import datetime
        print("✓ datetime imported successfully")
    except Exception as e:
        print(f"✗ datetime import failed: {e}")
        return False
    
    try:
        from pathlib import Path
        print("✓ pathlib imported successfully")
    except Exception as e:
        print(f"✗ pathlib import failed: {e}")
        return False
    
    return True

def test_gui_creation():
    """Test basic GUI creation"""
    print("\nTesting GUI creation...")
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("Test Window")
        root.geometry("300x200")
        
        # Test basic widget creation
        label = tk.Label(root, text="Test Label")
        label.pack()
        
        print("✓ Basic GUI creation successful")
        
        # Don't actually show the window, just test creation
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ GUI creation failed: {e}")
        traceback.print_exc()
        return False

def test_file_operations():
    """Test file operations"""
    print("\nTesting file operations...")
    
    try:
        from pathlib import Path
        
        # Test directory creation
        test_dir = Path("test_projects")
        test_dir.mkdir(exist_ok=True)
        print("✓ Directory creation successful")
        
        # Test file writing
        test_file = test_dir / "test.json"
        import json
        test_data = {"test": "data"}
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        print("✓ File writing successful")
        
        # Test file reading
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        print("✓ File reading successful")
        
        # Cleanup
        test_file.unlink()
        test_dir.rmdir()
        print("✓ File cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ File operations failed: {e}")
        traceback.print_exc()
        return False

def test_application_startup():
    """Test the actual application startup"""
    print("\nTesting application startup...")
    
    try:
        # Import the main application
        from interest_calculator_gui import InterestRateCalculator
        print("✓ Application class imported successfully")
        
        # Try to create the application instance
        app = InterestRateCalculator()
        print("✓ Application instance created successfully")
        
        # Test if we can access the root window
        if hasattr(app, 'root') and app.root:
            print("✓ Root window accessible")
        else:
            print("✗ Root window not accessible")
            return False
        
        # Don't actually run the mainloop, just test creation
        app.root.destroy()
        print("✓ Application startup test successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Application startup failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Interest Rate Calculator - Diagnostic Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test GUI creation
    if not test_gui_creation():
        all_tests_passed = False
    
    # Test file operations
    if not test_file_operations():
        all_tests_passed = False
    
    # Test application startup
    if not test_application_startup():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✓ All tests passed! Application should work.")
    else:
        print("✗ Some tests failed. Check the errors above.")
    
    return all_tests_passed

if __name__ == "__main__":
    main()
