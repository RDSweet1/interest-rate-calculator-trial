#!/usr/bin/env python3
"""
Test Runner for Interest Rate Calculator
Comprehensive test execution with multiple test types and reporting
"""
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class TestRunner:
    """Main test runner class"""
    
    def __init__(self):
        self.project_root = project_root
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def install_test_dependencies(self):
        """Install test dependencies"""
        print("Installing test dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"
            ], check=True, cwd=self.project_root)
            print("✓ Test dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install test dependencies: {e}")
            return False
        return True
    
    def setup_playwright(self):
        """Setup Playwright browsers"""
        print("Setting up Playwright browsers...")
        try:
            subprocess.run([
                sys.executable, "-m", "playwright", "install"
            ], check=True, cwd=self.project_root)
            print("✓ Playwright browsers installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install Playwright browsers: {e}")
            return False
        return True
    
    def run_unit_tests(self, verbose=False):
        """Run unit tests"""
        print("\n" + "="*60)
        print("RUNNING UNIT TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_unit_core.py",
            "-m", "unit",
            "--tb=short",
            "--cov=.",
            "--cov-report=term-missing",
            "--html=reports/unit_test_report.html",
            "--self-contained-html"
        ]
        
        if verbose:
            cmd.append("-v")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0
        except Exception as e:
            print(f"✗ Unit tests failed: {e}")
            return False
    
    def run_integration_tests(self, verbose=False):
        """Run integration tests"""
        print("\n" + "="*60)
        print("RUNNING INTEGRATION TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_integration.py",
            "-m", "integration",
            "--tb=short",
            "--html=reports/integration_test_report.html",
            "--self-contained-html"
        ]
        
        if verbose:
            cmd.append("-v")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0
        except Exception as e:
            print(f"✗ Integration tests failed: {e}")
            return False
    
    def run_web_tests(self, verbose=False, headless=True):
        """Run web interface tests with Playwright"""
        print("\n" + "="*60)
        print("RUNNING WEB INTERFACE TESTS")
        print("="*60)
        
        # Set environment variables for Playwright
        env = os.environ.copy()
        env["PLAYWRIGHT_HEADLESS"] = "true" if headless else "false"
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_web_interface.py",
            "-m", "web",
            "--tb=short",
            "--html=reports/web_test_report.html",
            "--self-contained-html"
        ]
        
        if verbose:
            cmd.append("-v")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, env=env)
            return result.returncode == 0
        except Exception as e:
            print(f"✗ Web tests failed: {e}")
            return False
    
    def run_desktop_tests(self, verbose=False):
        """Run desktop application tests"""
        print("\n" + "="*60)
        print("RUNNING DESKTOP APPLICATION TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_desktop_automation.py",
            "-m", "desktop",
            "--tb=short",
            "--html=reports/desktop_test_report.html",
            "--self-contained-html"
        ]
        
        if verbose:
            cmd.append("-v")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0
        except Exception as e:
            print(f"✗ Desktop tests failed: {e}")
            return False
    
    def run_smoke_tests(self, verbose=False):
        """Run smoke tests"""
        print("\n" + "="*60)
        print("RUNNING SMOKE TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-m", "smoke",
            "--tb=short",
            "--html=reports/smoke_test_report.html",
            "--self-contained-html"
        ]
        
        if verbose:
            cmd.append("-v")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0
        except Exception as e:
            print(f"✗ Smoke tests failed: {e}")
            return False
    
    def run_all_tests(self, verbose=False, headless=True):
        """Run all test suites"""
        print("\n" + "="*60)
        print("RUNNING ALL TESTS")
        print("="*60)
        
        start_time = time.time()
        results = {}
        
        # Run each test suite
        results['unit'] = self.run_unit_tests(verbose)
        results['integration'] = self.run_integration_tests(verbose)
        results['web'] = self.run_web_tests(verbose, headless)
        results['desktop'] = self.run_desktop_tests(verbose)
        results['smoke'] = self.run_smoke_tests(verbose)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate summary report
        self.generate_summary_report(results, duration)
        
        # Return overall success
        return all(results.values())
    
    def generate_summary_report(self, results, duration):
        """Generate summary test report"""
        print("\n" + "="*60)
        print("TEST SUMMARY REPORT")
        print("="*60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Test Suites: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Duration: {duration:.2f} seconds")
        print()
        
        for test_type, result in results.items():
            status = "✓ PASSED" if result else "✗ FAILED"
            print(f"{test_type.upper():<15} {status}")
        
        # Write summary to file
        summary_file = self.reports_dir / "test_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Interest Rate Calculator Test Summary\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration:.2f} seconds\n\n")
            f.write(f"Results:\n")
            for test_type, result in results.items():
                status = "PASSED" if result else "FAILED"
                f.write(f"  {test_type.upper():<15} {status}\n")
        
        print(f"\nDetailed reports available in: {self.reports_dir}")
        print(f"Summary report: {summary_file}")
    
    def run_performance_tests(self, verbose=False):
        """Run performance tests"""
        print("\n" + "="*60)
        print("RUNNING PERFORMANCE TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-m", "slow",
            "--tb=short",
            "--html=reports/performance_test_report.html",
            "--self-contained-html"
        ]
        
        if verbose:
            cmd.append("-v")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0
        except Exception as e:
            print(f"✗ Performance tests failed: {e}")
            return False
    
    def run_coverage_report(self):
        """Generate detailed coverage report"""
        print("\n" + "="*60)
        print("GENERATING COVERAGE REPORT")
        print("="*60)
        
        try:
            # Generate HTML coverage report
            subprocess.run([
                sys.executable, "-m", "coverage", "html",
                "--directory=reports/coverage_html"
            ], cwd=self.project_root)
            
            # Generate XML coverage report
            subprocess.run([
                sys.executable, "-m", "coverage", "xml",
                "-o", "reports/coverage.xml"
            ], cwd=self.project_root)
            
            print("✓ Coverage reports generated successfully")
            print(f"HTML Report: {self.reports_dir}/coverage_html/index.html")
            print(f"XML Report: {self.reports_dir}/coverage.xml")
            
        except Exception as e:
            print(f"✗ Failed to generate coverage report: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Interest Rate Calculator Test Runner")
    parser.add_argument("--setup", action="store_true", help="Install test dependencies and setup")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--web", action="store_true", help="Run web interface tests only")
    parser.add_argument("--desktop", action="store_true", help="Run desktop tests only")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--headless", action="store_true", default=True, help="Run web tests in headless mode")
    parser.add_argument("--headed", action="store_true", help="Run web tests in headed mode")
    
    args = parser.parse_args()
    
    # Handle headed mode
    if args.headed:
        args.headless = False
    
    runner = TestRunner()
    
    # Setup if requested
    if args.setup:
        if not runner.install_test_dependencies():
            sys.exit(1)
        if not runner.setup_playwright():
            sys.exit(1)
        print("✓ Setup completed successfully")
        return
    
    # Determine which tests to run
    success = True
    
    if args.unit:
        success = runner.run_unit_tests(args.verbose)
    elif args.integration:
        success = runner.run_integration_tests(args.verbose)
    elif args.web:
        success = runner.run_web_tests(args.verbose, args.headless)
    elif args.desktop:
        success = runner.run_desktop_tests(args.verbose)
    elif args.smoke:
        success = runner.run_smoke_tests(args.verbose)
    elif args.performance:
        success = runner.run_performance_tests(args.verbose)
    elif args.all:
        success = runner.run_all_tests(args.verbose, args.headless)
    else:
        # Default: run smoke tests
        success = runner.run_smoke_tests(args.verbose)
    
    # Generate coverage report if requested
    if args.coverage:
        runner.run_coverage_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
