#!/usr/bin/env python3
"""
Comprehensive diagnostic test for Interest Rate Calculator
Tests the top 10 reasons why the application might not open
"""

import sys
import traceback
import os
from pathlib import Path

def test_1_syntax_errors():
    """Test 1: Check for syntax errors in the main file"""
    print("=" * 60)
    print("TEST 1: Checking for syntax errors...")
    try:
        with open('interest_calculator_gui.py', 'r') as f:
            code = f.read()
        
        # Try to compile the code
        compile(code, 'interest_calculator_gui.py', 'exec')
        print("✓ No syntax errors found")
        return True
    except SyntaxError as e:
        print(f"✗ SYNTAX ERROR: {e}")
        print(f"  Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"✗ ERROR reading file: {e}")
        return False

def test_2_import_errors():
    """Test 2: Check for import errors"""
    print("=" * 60)
    print("TEST 2: Checking imports...")
    
    imports_to_test = [
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.font',
        'json',
        'os',
        'datetime',
        'pathlib',
        'traceback'
    ]
    
    all_good = True
    for imp in imports_to_test:
        try:
            if '.' in imp:
                module, submodule = imp.split('.', 1)
                exec(f"import {module}")
                exec(f"from {module} import {submodule}")
            else:
                exec(f"import {imp}")
            print(f"✓ {imp} imported successfully")
        except Exception as e:
            print(f"✗ IMPORT ERROR {imp}: {e}")
            all_good = False
    
    return all_good

def test_3_tkinter_availability():
    """Test 3: Test tkinter GUI creation"""
    print("=" * 60)
    print("TEST 3: Testing tkinter GUI creation...")
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Create a test window
        root = tk.Tk()
        root.title("Test Window")
        root.geometry("300x200")
        
        # Test basic widgets
        label = ttk.Label(root, text="Test Label")
        label.pack()
        
        button = ttk.Button(root, text="Test Button")
        button.pack()
        
        # Test font creation
        import tkinter.font as tkfont
        base_font = tkfont.nametofont("TkDefaultFont")
        test_font = (base_font.actual("family"), max(1, int(base_font.actual("size") * 1.3)), "bold")
        
        test_label = ttk.Label(root, text="Test Font", font=test_font)
        test_label.pack()
        
        print("✓ Tkinter GUI creation successful")
        
        # Don't show the window, just test creation
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ TKINTER ERROR: {e}")
        traceback.print_exc()
        return False

def test_4_file_permissions():
    """Test 4: Check file and directory permissions"""
    print("=" * 60)
    print("TEST 4: Testing file permissions...")
    try:
        # Test creating projects directory
        projects_dir = Path("projects")
        projects_dir.mkdir(exist_ok=True)
        print("✓ Projects directory created/exists")
        
        # Test writing to projects directory
        test_file = projects_dir / "test.json"
        with open(test_file, 'w') as f:
            f.write('{"test": "data"}')
        print("✓ Can write to projects directory")
        
        # Test reading from projects directory
        with open(test_file, 'r') as f:
            data = f.read()
        print("✓ Can read from projects directory")
        
        # Cleanup
        test_file.unlink()
        print("✓ File permissions test passed")
        return True
        
    except Exception as e:
        print(f"✗ FILE PERMISSION ERROR: {e}")
        return False

def test_5_class_initialization():
    """Test 5: Test class initialization step by step"""
    print("=" * 60)
    print("TEST 5: Testing class initialization...")
    try:
        # Import the main module
        sys.path.insert(0, '.')
        
        # Test importing the module
        import interest_calculator_gui as app_module
        print("✓ Module imported successfully")
        
        # Test date conversion functions
        test_date = app_module.convert_to_american_date("2023-04-28")
        print(f"✓ Date conversion works: {test_date}")
        
        # Test CollapsibleSection class
        import tkinter as tk
        from tkinter import ttk
        
        root = tk.Tk()
        section = app_module.CollapsibleSection(root, "Test Section")
        print("✓ CollapsibleSection created successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ CLASS INITIALIZATION ERROR: {e}")
        traceback.print_exc()
        return False

def test_6_full_app_creation():
    """Test 6: Test full application creation without mainloop"""
    print("=" * 60)
    print("TEST 6: Testing full application creation...")
    try:
        sys.path.insert(0, '.')
        import interest_calculator_gui as app_module
        
        # Create the application instance
        app = app_module.InterestRateCalculator()
        print("✓ Application instance created")
        
        # Test if root window exists
        if hasattr(app, 'root') and app.root:
            print("✓ Root window created")
        else:
            print("✗ Root window not found")
            return False
        
        # Test if main components exist
        if hasattr(app, 'project_frame'):
            print("✓ Project frame exists")
        else:
            print("✗ Project frame not found")
        
        # Don't run mainloop, just test creation
        app.root.destroy()
        print("✓ Application creation test passed")
        return True
        
    except Exception as e:
        print(f"✗ APPLICATION CREATION ERROR: {e}")
        traceback.print_exc()
        return False

def test_7_window_display():
    """Test 7: Test window display and focus"""
    print("=" * 60)
    print("TEST 7: Testing window display...")
    try:
        import tkinter as tk
        
        root = tk.Tk()
        root.title("Display Test")
        root.geometry("400x300")
        
        # Test window positioning
        root.update_idletasks()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        x = (width - 400) // 2
        y = (height - 300) // 2
        root.geometry(f"400x300+{x}+{y}")
        
        # Test window focus
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(lambda: root.attributes('-topmost', False))
        
        print("✓ Window display test setup successful")
        
        # Auto-close after 2 seconds
        root.after(2000, root.quit)
        
        # This will actually show the window briefly
        print("✓ Window should appear for 2 seconds...")
        root.mainloop()
        
        root.destroy()
        print("✓ Window display test completed")
        return True
        
    except Exception as e:
        print(f"✗ WINDOW DISPLAY ERROR: {e}")
        traceback.print_exc()
        return False

def test_8_event_handling():
    """Test 8: Test event handling and bindings"""
    print("=" * 60)
    print("TEST 8: Testing event handling...")
    try:
        import tkinter as tk
        from tkinter import ttk
        
        root = tk.Tk()
        
        # Test event binding
        def test_callback(*args):
            print("✓ Event callback triggered")
        
        label = ttk.Label(root, text="Test Label")
        label.bind("<Button-1>", test_callback)
        
        # Test manual event trigger
        label.event_generate("<Button-1>")
        
        root.destroy()
        print("✓ Event handling test passed")
        return True
        
    except Exception as e:
        print(f"✗ EVENT HANDLING ERROR: {e}")
        return False

def test_9_memory_and_resources():
    """Test 9: Check memory and resource usage"""
    print("=" * 60)
    print("TEST 9: Testing memory and resources...")
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        print(f"✓ Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
        print(f"✓ CPU percent: {process.cpu_percent():.2f}%")
        
        return True
        
    except ImportError:
        print("! psutil not available, skipping detailed resource check")
        print("✓ Basic resource test passed")
        return True
    except Exception as e:
        print(f"✗ RESOURCE ERROR: {e}")
        return False

def test_10_run_with_timeout():
    """Test 10: Run the actual application with timeout"""
    print("=" * 60)
    print("TEST 10: Running actual application with timeout...")
    try:
        import subprocess
        import time
        
        # Start the application in a subprocess
        process = subprocess.Popen([sys.executable, 'interest_calculator_gui.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for 5 seconds
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ Application is running (process still active)")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            # Process ended, check output
            stdout, stderr = process.communicate()
            print(f"✗ Application exited with code: {process.returncode}")
            if stdout:
                print(f"STDOUT: {stdout.decode()}")
            if stderr:
                print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"✗ SUBPROCESS ERROR: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("Interest Rate Calculator - Comprehensive Diagnostic Test")
    print("=" * 60)
    
    tests = [
        test_1_syntax_errors,
        test_2_import_errors,
        test_3_tkinter_availability,
        test_4_file_permissions,
        test_5_class_initialization,
        test_6_full_app_creation,
        test_7_window_display,
        test_8_event_handling,
        test_9_memory_and_resources,
        test_10_run_with_timeout
    ]
    
    results = []
    for i, test in enumerate(tests, 1):
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ TEST {i} FAILED WITH EXCEPTION: {e}")
            traceback.print_exc()
            results.append(False)
        
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, result in enumerate(results, 1):
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"Test {i:2d}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()
