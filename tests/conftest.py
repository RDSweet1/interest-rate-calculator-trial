"""
Pytest configuration and fixtures for Interest Rate Calculator tests
"""
import os
import sys
import json
import tempfile
import shutil
import subprocess
import time
import pytest
import psutil
from pathlib import Path
from datetime import datetime
from typing import Generator, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import Playwright, Browser, BrowserContext, Page, sync_playwright
from playwright.sync_api import expect

# Import playwright config from parent directory
sys.path.insert(0, str(project_root))
try:
    from playwright_config import config
except ImportError:
    # Fallback configuration if playwright_config is not available
    class FallbackConfig:
        BASE_URL = "http://localhost:5000"
        HEADLESS = True
        BROWSER_TYPE = "chromium"
        VIEWPORT_WIDTH = 1280
        VIEWPORT_HEIGHT = 720
        DEFAULT_TIMEOUT = 30000
        SCREENSHOTS_DIR = "tests/screenshots"
        VIDEOS_DIR = "tests/videos"
        TRACES_DIR = "tests/traces"
        
        @classmethod
        def get_browser_config(cls):
            return {"headless": cls.HEADLESS}
        
        @classmethod
        def get_context_config(cls):
            return {"viewport": {"width": cls.VIEWPORT_WIDTH, "height": cls.VIEWPORT_HEIGHT}}
        
        @classmethod
        def setup_directories(cls):
            for directory in [cls.SCREENSHOTS_DIR, cls.VIDEOS_DIR, cls.TRACES_DIR]:
                Path(directory).mkdir(exist_ok=True)
    
    config = FallbackConfig()

# Test data directories
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEMP_PROJECTS_DIR = Path(__file__).parent / "temp_projects"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before running tests"""
    # Create test directories
    config.setup_directories()
    TEST_DATA_DIR.mkdir(exist_ok=True)
    TEMP_PROJECTS_DIR.mkdir(exist_ok=True)
    
    yield
    
    # Cleanup after tests
    if TEMP_PROJECTS_DIR.exists():
        shutil.rmtree(TEMP_PROJECTS_DIR)

@pytest.fixture(scope="session")
def flask_app():
    """Start Flask application for web testing"""
    # Set environment variables for Flask testing
    os.environ["RUN_FLASK"] = "1"
    os.environ["FLASK_ENV"] = "testing"
    
    # Start Flask app in subprocess
    process = subprocess.Popen([
        sys.executable, "interest_app.py"
    ], cwd=project_root)
    
    # Wait for Flask app to start
    time.sleep(3)
    
    # Verify Flask app is running
    import requests
    try:
        response = requests.get(f"{config.BASE_URL}/", timeout=5)
        assert response.status_code == 200
    except Exception as e:
        process.terminate()
        pytest.fail(f"Flask app failed to start: {e}")
    
    yield process
    
    # Cleanup: terminate Flask process
    try:
        process.terminate()
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

@pytest.fixture(scope="session")
def playwright_instance():
    """Create Playwright instance for the session"""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright):
    """Create browser instance for the session"""
    browser_type = getattr(playwright_instance, config.BROWSER_TYPE)
    browser = browser_type.launch(**config.get_browser_config())
    yield browser
    browser.close()

@pytest.fixture
def context(browser: Browser):
    """Create browser context for each test"""
    context = browser.new_context(**config.get_context_config())
    yield context
    context.close()

@pytest.fixture
def page(context: BrowserContext):
    """Create page for each test"""
    page = context.new_page()
    page.set_default_timeout(config.DEFAULT_TIMEOUT)
    yield page

@pytest.fixture
def web_app(page: Page, flask_app):
    """Navigate to web application"""
    page.goto(config.BASE_URL)
    page.wait_for_load_state("networkidle")
    yield page

@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "title": "Test Project",
        "billing_date": "2023-04-28",
        "as_of_date": "2025-09-05",
        "grace_days": 30,
        "annual_rate": 0.18,
        "monthly_rate": 0.015,
        "principal_fw": 13365247.68,
        "principal_dw": 1113503.81,
        "payments": [
            {"desc": "Test Payment 1", "date": "2023-01-04", "amount": 100000.00},
            {"desc": "Test Payment 2", "date": "2023-01-24", "amount": 860000.00}
        ],
        "invoices": [
            {"date": "2023-01-01", "description": "Test Invoice 1", "amount": 50000.00},
            {"date": "2023-02-01", "description": "Test Invoice 2", "amount": 75000.00}
        ],
        "sharepoint": {"folder_id": None, "folder_path": None}
    }

@pytest.fixture
def temp_project_file(sample_project_data):
    """Create temporary project file for testing"""
    temp_file = TEMP_PROJECTS_DIR / "test_project.json"
    with open(temp_file, 'w') as f:
        json.dump(sample_project_data, f, indent=2)
    yield temp_file
    if temp_file.exists():
        temp_file.unlink()

@pytest.fixture
def desktop_app():
    """Start desktop application for UI testing"""
    # Import here to avoid issues if pywinauto is not available
    try:
        import pywinauto
        from pywinauto import Application
    except ImportError:
        pytest.skip("pywinauto not available for desktop testing")
    
    # Start the desktop application
    process = subprocess.Popen([
        sys.executable, "app_launcher.py"
    ], cwd=project_root)
    
    # Wait for application to start
    time.sleep(3)
    
    # Connect to the application
    try:
        app = Application().connect(title_re="Interest Rate Calculator.*")
        yield app
    except Exception as e:
        process.terminate()
        pytest.fail(f"Failed to connect to desktop app: {e}")
    finally:
        # Cleanup
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

@pytest.fixture
def mock_sharepoint_data():
    """Mock SharePoint data for testing"""
    return {
        "folders": [
            {"id": "f1", "name": "Accounting", "children": [
                {"id": "f1a", "name": "2024"},
                {"id": "f1b", "name": "2025"}
            ]},
            {"id": "f2", "name": "Ocean Harbor", "children": [
                {"id": "f2a", "name": "Claims"},
                {"id": "f2b", "name": "Invoices"}
            ]},
            {"id": "f3", "name": "Legal"}
        ]
    }

# Test markers for different test categories
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "web: Web interface tests")
    config.addinivalue_line("markers", "desktop: Desktop application tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location"""
    for item in items:
        # Add markers based on test file location
        if "test_web" in item.fspath.basename:
            item.add_marker(pytest.mark.web)
        elif "test_desktop" in item.fspath.basename:
            item.add_marker(pytest.mark.desktop)
        elif "test_unit" in item.fspath.basename:
            item.add_marker(pytest.mark.unit)
        elif "test_integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)

@pytest.fixture
def screenshot_on_failure(request, page: Page):
    """Take screenshot on test failure"""
    yield
    if request.node.rep_call.failed:
        screenshot_path = config.SCREENSHOTS_DIR + f"/{request.node.name}_failure.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for screenshot fixture"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
