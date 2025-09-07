#!/usr/bin/env python3
"""
Test Watch Mode for Interest Rate Calculator
Automatically runs tests when files change for continuous development
"""
import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TestWatchHandler(FileSystemEventHandler):
    """Handler for file system events that triggers test runs"""
    
    def __init__(self, test_runner_path):
        self.test_runner_path = test_runner_path
        self.last_run = 0
        self.debounce_seconds = 2  # Wait 2 seconds between runs
        
    def should_trigger_tests(self, event):
        """Determine if the event should trigger tests"""
        if event.is_directory:
            return False
            
        # Only trigger on Python files
        if not event.src_path.endswith('.py'):
            return False
            
        # Ignore test files themselves to prevent infinite loops
        if 'test_' in os.path.basename(event.src_path):
            return False
            
        # Ignore __pycache__ and other temp files
        if '__pycache__' in event.src_path or event.src_path.endswith('.pyc'):
            return False
            
        return True
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not self.should_trigger_tests(event):
            return
            
        current_time = time.time()
        if current_time - self.last_run < self.debounce_seconds:
            return
            
        self.last_run = current_time
        
        print(f"\n{'='*60}")
        print(f"File changed: {event.src_path}")
        print(f"Running tests at {time.strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        self.run_tests()
    
    def run_tests(self):
        """Run the test suite"""
        try:
            # Run smoke tests by default (fast feedback)
            result = subprocess.run([
                sys.executable, self.test_runner_path, "--smoke", "--verbose"
            ], cwd=Path(self.test_runner_path).parent)
            
            if result.returncode == 0:
                print("✓ Tests PASSED")
            else:
                print("✗ Tests FAILED")
                
        except Exception as e:
            print(f"Error running tests: {e}")

class TestWatcher:
    """Main test watcher class"""
    
    def __init__(self, watch_paths=None, test_type="smoke"):
        self.project_root = Path(__file__).parent
        self.test_runner_path = self.project_root / "run_tests.py"
        self.test_type = test_type
        
        # Default paths to watch
        if watch_paths is None:
            watch_paths = [
                self.project_root / "interest_calculator_gui.py",
                self.project_root / "interest_app.py",
                self.project_root / "app_launcher.py",
            ]
        
        self.watch_paths = [Path(p) for p in watch_paths]
        self.observer = Observer()
        
    def start_watching(self):
        """Start watching for file changes"""
        print("Interest Rate Calculator - Test Watch Mode")
        print("="*60)
        print(f"Watching files for changes...")
        print(f"Test type: {self.test_type}")
        print("Press Ctrl+C to stop")
        print()
        
        # Create event handler
        handler = TestWatchHandler(str(self.test_runner_path))
        
        # Watch the project root directory
        self.observer.schedule(handler, str(self.project_root), recursive=False)
        
        # Start the observer
        self.observer.start()
        
        try:
            # Run initial test suite
            print("Running initial test suite...")
            handler.run_tests()
            
            # Keep watching
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nStopping test watcher...")
            self.observer.stop()
            
        self.observer.join()
        print("Test watcher stopped.")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Watch Mode for Interest Rate Calculator")
    parser.add_argument("--type", choices=["smoke", "unit", "all"], default="smoke",
                       help="Type of tests to run on changes")
    parser.add_argument("--paths", nargs="+", help="Specific paths to watch")
    
    args = parser.parse_args()
    
    # Check if watchdog is available
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("Error: watchdog package is required for test watch mode")
        print("Install it with: pip install watchdog")
        sys.exit(1)
    
    # Create and start watcher
    watcher = TestWatcher(watch_paths=args.paths, test_type=args.type)
    watcher.start_watching()

if __name__ == "__main__":
    main()
