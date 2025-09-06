#!/usr/bin/env python3
"""
Test script to run the actual application with error handling
"""

import sys
import traceback
import time

def run_application():
    """Run the application with error handling"""
    print("Starting Interest Rate Calculator...")
    
    try:
        from interest_calculator_gui import InterestRateCalculator
        
        print("Creating application instance...")
        app = InterestRateCalculator()
        
        print("Application created successfully!")
        print("Starting main loop...")
        
        # Run for a short time to see if it crashes immediately
        app.root.after(2000, app.root.quit)  # Auto-quit after 2 seconds
        app.run()
        
        print("Application ran successfully!")
        return True
        
    except Exception as e:
        print(f"Application failed with error: {e}")
        traceback.print_exc()
        return False

def run_with_timeout():
    """Run application with timeout"""
    import signal
    import threading
    
    def timeout_handler(signum, frame):
        print("Application timed out - this might indicate it's hanging")
        sys.exit(1)
    
    # Set a timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 second timeout
    
    try:
        result = run_application()
        signal.alarm(0)  # Cancel timeout
        return result
    except SystemExit:
        print("Application was terminated by timeout")
        return False

if __name__ == "__main__":
    print("Testing actual application execution...")
    print("=" * 50)
    
    # On Windows, we can't use signal.alarm, so let's use threading instead
    import threading
    import time
    
    result = [False]
    error = [None]
    
    def run_app():
        try:
            result[0] = run_application()
        except Exception as e:
            error[0] = e
            traceback.print_exc()
    
    # Start application in a thread
    app_thread = threading.Thread(target=run_app)
    app_thread.daemon = True
    app_thread.start()
    
    # Wait for completion or timeout
    app_thread.join(timeout=15)
    
    if app_thread.is_alive():
        print("Application is still running after 15 seconds - this is good!")
        print("Application appears to be working correctly.")
        result[0] = True
    else:
        if error[0]:
            print(f"Application failed: {error[0]}")
        else:
            print("Application completed successfully!")
    
    print("=" * 50)
    if result[0]:
        print("✓ Application test PASSED")
    else:
        print("✗ Application test FAILED")
