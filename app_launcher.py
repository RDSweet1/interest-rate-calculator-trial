#!/usr/bin/env python3
"""
Robust Application Launcher for Interest Rate Calculator
Ensures the app launches, stays visible, and handles all error conditions
"""

import sys
import os
import time
import traceback
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

class AppLauncher:
    def __init__(self):
        self.app_file = "interest_calculator_gui.py"
        self.app_instance = None
        self.launch_attempts = 0
        self.max_attempts = 3
        
    def check_prerequisites(self):
        """Check all prerequisites before launching"""
        print("Checking prerequisites...")
        
        # Check if main app file exists
        if not os.path.exists(self.app_file):
            raise FileNotFoundError(f"Application file '{self.app_file}' not found")
        
        # Check Python version
        if sys.version_info < (3, 6):
            raise RuntimeError(f"Python 3.6+ required, found {sys.version}")
        
        # Test imports
        required_modules = ['tkinter', 'json', 'pathlib', 'datetime']
        for module in required_modules:
            try:
                __import__(module)
            except ImportError as e:
                raise ImportError(f"Required module '{module}' not available: {e}")
        
        # Test tkinter GUI creation
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the test window
            root.destroy()
        except Exception as e:
            raise RuntimeError(f"Tkinter GUI not available: {e}")
        
        print("✓ All prerequisites met")
        
    def launch_direct(self):
        """Launch the app directly in the same process"""
        print("Attempting direct launch...")
        
        try:
            # Import and run the application
            sys.path.insert(0, '.')
            import interest_calculator_gui
            
            # Create application instance
            app = interest_calculator_gui.InterestRateCalculator()
            
            # Ensure window is visible and on top
            app.root.deiconify()  # Make sure it's not minimized
            app.root.lift()
            app.root.attributes('-topmost', True)
            app.root.focus_force()
            
            # Remove topmost after a moment so it doesn't stay always on top
            app.root.after(1000, lambda: app.root.attributes('-topmost', False))
            
            print("✓ Application launched successfully")
            print("✓ Window should be visible and focused")
            
            # Store reference
            self.app_instance = app
            
            # Run the application
            app.run()
            
            return True
            
        except Exception as e:
            print(f"✗ Direct launch failed: {e}")
            traceback.print_exc()
            return False
    
    def launch_subprocess(self):
        """Launch the app in a subprocess"""
        print("Attempting subprocess launch...")
        
        try:
            # Launch as subprocess
            process = subprocess.Popen(
                [sys.executable, self.app_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait a moment to see if it starts
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print("✓ Application launched in subprocess")
                print("✓ Process is running")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"✗ Subprocess failed with exit code: {process.returncode}")
                if stdout:
                    print(f"STDOUT: {stdout.decode()}")
                if stderr:
                    print(f"STDERR: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"✗ Subprocess launch failed: {e}")
            return False
    
    def create_minimal_app(self):
        """Create a minimal version of the app if main app fails"""
        print("Creating minimal fallback application...")
        
        try:
            root = tk.Tk()
            root.title("Interest Rate Calculator - Minimal Mode")
            root.geometry("600x400")
            
            # Center the window
            root.update_idletasks()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            x = (width - 600) // 2
            y = (height - 400) // 2
            root.geometry(f"600x400+{x}+{y}")
            
            # Make it visible and focused
            root.lift()
            root.attributes('-topmost', True)
            root.focus_force()
            root.after(1000, lambda: root.attributes('-topmost', False))
            
            # Create basic interface
            main_frame = tk.Frame(root, padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            title_label = tk.Label(main_frame, 
                                 text="Interest Rate Calculator", 
                                 font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 20))
            
            error_label = tk.Label(main_frame, 
                                 text="The full application encountered an error.\nThis is a minimal fallback version.",
                                 font=("Arial", 10),
                                 fg="red")
            error_label.pack(pady=(0, 20))
            
            # Basic functionality
            tk.Label(main_frame, text="Project Title:").pack(anchor=tk.W)
            title_entry = tk.Entry(main_frame, width=50)
            title_entry.pack(pady=(0, 10))
            
            tk.Label(main_frame, text="Principal Amount:").pack(anchor=tk.W)
            principal_entry = tk.Entry(main_frame, width=20)
            principal_entry.pack(pady=(0, 10))
            
            tk.Label(main_frame, text="Interest Rate (%):").pack(anchor=tk.W)
            rate_entry = tk.Entry(main_frame, width=20)
            rate_entry.pack(pady=(0, 20))
            
            def calculate():
                try:
                    principal = float(principal_entry.get() or 0)
                    rate = float(rate_entry.get() or 0) / 100
                    monthly_interest = principal * rate / 12
                    result_label.config(text=f"Monthly Interest: ${monthly_interest:,.2f}")
                except ValueError:
                    result_label.config(text="Please enter valid numbers")
            
            calc_button = tk.Button(main_frame, text="Calculate", command=calculate)
            calc_button.pack(pady=(0, 10))
            
            result_label = tk.Label(main_frame, text="", font=("Arial", 12, "bold"))
            result_label.pack()
            
            # Retry button
            def retry_full_app():
                root.destroy()
                self.launch_attempts = 0
                self.launch_with_fallback()
            
            retry_button = tk.Button(main_frame, text="Retry Full Application", 
                                   command=retry_full_app, bg="lightblue")
            retry_button.pack(pady=(20, 0))
            
            print("✓ Minimal application created and visible")
            root.mainloop()
            
            return True
            
        except Exception as e:
            print(f"✗ Even minimal app failed: {e}")
            return False
    
    def show_error_dialog(self, error_message):
        """Show error dialog to user"""
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            messagebox.showerror(
                "Application Launch Error",
                f"Failed to launch Interest Rate Calculator:\n\n{error_message}\n\nPlease check the console for more details."
            )
            
            root.destroy()
        except:
            print(f"Could not show error dialog: {error_message}")
    
    def launch_with_fallback(self):
        """Launch with multiple fallback strategies"""
        self.launch_attempts += 1
        
        print(f"\n{'='*60}")
        print(f"LAUNCH ATTEMPT {self.launch_attempts}/{self.max_attempts}")
        print(f"{'='*60}")
        
        try:
            # Check prerequisites first
            self.check_prerequisites()
            
            # Try direct launch first
            if self.launch_direct():
                return True
            
            # If direct launch fails, try subprocess
            if self.launch_subprocess():
                return True
            
            # If both fail and we haven't exceeded attempts, try minimal app
            if self.launch_attempts >= self.max_attempts:
                print("\nAll launch attempts failed. Creating minimal fallback...")
                return self.create_minimal_app()
            else:
                print(f"\nRetrying in 2 seconds... (Attempt {self.launch_attempts + 1}/{self.max_attempts})")
                time.sleep(2)
                return self.launch_with_fallback()
                
        except Exception as e:
            error_msg = f"Launch attempt {self.launch_attempts} failed: {e}"
            print(f"✗ {error_msg}")
            traceback.print_exc()
            
            if self.launch_attempts >= self.max_attempts:
                self.show_error_dialog(error_msg)
                return self.create_minimal_app()
            else:
                time.sleep(2)
                return self.launch_with_fallback()
    
    def monitor_app(self):
        """Monitor the running application"""
        if self.app_instance and hasattr(self.app_instance, 'root'):
            try:
                # Check if window still exists
                if self.app_instance.root.winfo_exists():
                    print("✓ Application is running normally")
                else:
                    print("! Application window closed")
            except:
                print("! Application monitoring failed")

def main():
    """Main launcher function"""
    print("Interest Rate Calculator - Robust Launcher")
    print("=" * 60)
    
    launcher = AppLauncher()
    
    try:
        success = launcher.launch_with_fallback()
        
        if success:
            print("\n" + "=" * 60)
            print("✓ APPLICATION LAUNCHED SUCCESSFULLY")
            print("✓ Window should be visible and focused")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("✗ ALL LAUNCH ATTEMPTS FAILED")
            print("=" * 60)
            
    except KeyboardInterrupt:
        print("\n\nLaunch interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
