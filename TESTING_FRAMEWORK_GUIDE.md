# Interest Rate Calculator - Testing Framework Guide

## Overview

This comprehensive testing framework provides multiple testing approaches for the Interest Rate Calculator application, including web interface testing with Playwright, desktop automation, unit tests, and integration tests.

## Framework Components

### 1. Test Types

- **Unit Tests** (`test_unit_core.py`): Test individual functions and components
- **Integration Tests** (`test_integration.py`): Test component interactions and workflows
- **Web Interface Tests** (`test_web_interface.py`): Test Flask web UI with Playwright
- **Desktop Automation Tests** (`test_desktop_automation.py`): Test Tkinter GUI with pywinauto
- **Performance Tests**: Load and performance testing

### 2. Test Infrastructure

- **pytest**: Main testing framework with extensive configuration
- **Playwright**: Modern web testing framework for the Flask interface
- **pywinauto**: Windows desktop application automation
- **Coverage**: Code coverage analysis and reporting
- **Test Watch Mode**: Continuous testing during development

## Quick Start

### 1. Setup Testing Environment

```bash
# Install test dependencies
python run_tests.py --setup

# This installs:
# - pytest and plugins
# - Playwright and browsers
# - pywinauto for desktop automation
# - Coverage tools
```

### 2. Run Tests

```bash
# Run all tests
python run_tests.py --all

# Run specific test types
python run_tests.py --unit          # Unit tests only
python run_tests.py --integration   # Integration tests only
python run_tests.py --web          # Web interface tests only
python run_tests.py --desktop      # Desktop automation tests only
python run_tests.py --smoke        # Quick smoke tests

# Run with coverage
python run_tests.py --all --coverage

# Run in watch mode (continuous testing)
python test_watch.py
```

### 3. View Results

Test reports are generated in the `reports/` directory:
- `pytest_report.html`: Main test results
- `coverage_html/index.html`: Coverage report
- `test_summary.txt`: Summary of all test runs

## Detailed Testing Guide

### Web Interface Testing (Playwright)

Tests the Flask web interface at `http://localhost:5000` when `RUN_FLASK=1`.

**Key Features:**
- Automatic Flask app startup/shutdown
- Cross-browser testing (Chromium, Firefox, WebKit)
- Screenshot capture on failures
- API endpoint testing
- Accessibility testing

**Example Test:**
```python
@pytest.mark.web
def test_project_selection(web_app: Page):
    # Test project dropdown functionality
    dropdown = web_app.locator("#proj")
    expect(dropdown).to_be_visible()
    dropdown.select_option("<default>")
```

**Configuration:**
- `playwright.config.py`: Browser and test settings
- Headless/headed mode support
- Video recording for debugging

### Desktop Application Testing (pywinauto)

Tests the Tkinter desktop application using Windows UI automation.

**Key Features:**
- Window and control interaction
- Dialog testing (Payment/Invoice dialogs)
- TreeView (table) testing
- Button clicking and form filling
- Application stability testing

**Example Test:**
```python
@pytest.mark.desktop
def test_add_payment_dialog(desktop_app):
    # Navigate to payment dialog
    edit_btn = main_window.child_window(title="Edit Project")
    edit_btn.click_input()
    
    add_payment_btn = main_window.child_window(title="Add Payment")
    add_payment_btn.click_input()
    
    # Test dialog functionality
    payment_dialog = desktop_app.window(title_re=".*Payment.*")
    assert payment_dialog.is_visible()
```

**Requirements:**
- Windows OS (pywinauto limitation)
- Desktop application must be running
- UI Automation enabled

### Unit Testing

Tests individual functions and components in isolation.

**Coverage Areas:**
- Utility functions (formatting, parsing, date conversion)
- Interest calculation logic
- Data validation
- File operations
- Edge cases and error handling

**Example Test:**
```python
@pytest.mark.unit
def test_format_currency():
    assert format_currency(1000) == "$1,000.00"
    assert format_currency(1000.50) == "$1,000.50"
    assert format_currency(0) == "$0.00"
```

### Integration Testing

Tests component interactions and complete workflows.

**Coverage Areas:**
- Project CRUD operations
- File system integration
- Application startup/shutdown
- Data flow between components
- Error handling across components

**Example Test:**
```python
@pytest.mark.integration
def test_project_data_to_calculation_flow(sample_project_data):
    # Test complete data flow
    summary_df, schedule_df = parse_project(sample_project_data)
    
    # Verify results
    assert len(summary_df) == 3
    assert len(schedule_df) > 0
```

## Test Configuration

### pytest.ini

Main pytest configuration with:
- Test discovery patterns
- Markers for test categorization
- Coverage settings
- Report generation
- Timeout settings

### Test Fixtures

Located in `tests/conftest.py`:

- `flask_app`: Starts Flask application for web testing
- `desktop_app`: Starts desktop application for UI testing
- `sample_project_data`: Test project data
- `temp_project_file`: Temporary project file for testing
- `web_app`: Playwright page with Flask app loaded

### Test Markers

Use markers to categorize and run specific test types:

```bash
# Run only unit tests
pytest -m unit

# Run only web tests
pytest -m web

# Run only smoke tests
pytest -m smoke

# Exclude slow tests
pytest -m "not slow"
```

## Continuous Testing

### Test Watch Mode

Automatically runs tests when files change:

```bash
# Start watch mode
python test_watch.py

# Watch specific files
python test_watch.py --paths interest_calculator_gui.py interest_app.py

# Run different test types on changes
python test_watch.py --type unit
python test_watch.py --type smoke
```

### CI/CD Integration

The framework is designed for CI/CD integration:

- Exit codes indicate success/failure
- XML and HTML reports for CI systems
- Coverage reports in multiple formats
- Parallel test execution support

## Troubleshooting

### Common Issues

1. **Playwright browsers not installed**
   ```bash
   python -m playwright install
   ```

2. **pywinauto not working**
   - Ensure Windows UI Automation is enabled
   - Run as administrator if needed
   - Check that desktop app is actually running

3. **Flask app not starting**
   - Check port 5000 is available
   - Verify `RUN_FLASK=1` environment variable
   - Check Flask dependencies are installed

4. **Import errors in tests**
   - Ensure project root is in Python path
   - Check all dependencies are installed
   - Verify module names and imports

### Debug Mode

Run tests with verbose output and debug information:

```bash
# Verbose pytest output
python run_tests.py --all --verbose

# Playwright headed mode (see browser)
python run_tests.py --web --headed

# pytest with pdb on failure
pytest --pdb tests/test_unit_core.py
```

### Performance Considerations

- Web tests are slower due to browser startup
- Desktop tests require UI rendering
- Use `--maxfail=1` to stop on first failure
- Run smoke tests for quick feedback
- Use parallel execution: `pytest -n auto`

## Best Practices

### Writing Tests

1. **Use descriptive test names**
   ```python
   def test_payment_dialog_saves_data_correctly():
   ```

2. **Follow AAA pattern** (Arrange, Act, Assert)
   ```python
   def test_currency_formatting():
       # Arrange
       amount = 1000.50
       
       # Act
       result = format_currency(amount)
       
       # Assert
       assert result == "$1,000.50"
   ```

3. **Use fixtures for setup**
   ```python
   def test_project_loading(sample_project_data):
       # Use fixture data instead of creating inline
   ```

4. **Mark tests appropriately**
   ```python
   @pytest.mark.unit
   @pytest.mark.slow
   def test_large_calculation():
   ```

### Test Organization

- Keep tests focused and atomic
- Use clear test categories with markers
- Group related tests in classes
- Use descriptive docstrings
- Separate unit, integration, and UI tests

### Maintenance

- Update tests when functionality changes
- Keep test data realistic but minimal
- Review and update fixtures regularly
- Monitor test execution times
- Clean up temporary files and resources

## Advanced Features

### Custom Test Data

Create custom test data generators:

```python
@pytest.fixture
def large_project_data():
    """Generate project with many payments for performance testing"""
    payments = []
    for i in range(1000):
        payments.append({
            "desc": f"Payment {i}",
            "date": f"2023-{(i % 12) + 1:02d}-01",
            "amount": 1000.00
        })
    return {"payments": payments, ...}
```

### Parallel Testing

Run tests in parallel for faster execution:

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto tests/
```

### Test Reporting

Generate custom reports:

```python
# Custom report generation in run_tests.py
def generate_custom_report(results):
    # Create custom HTML/PDF reports
    # Send email notifications
    # Update dashboards
```

## Integration with Development Workflow

### Pre-commit Hooks

Set up pre-commit hooks to run tests automatically:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
# Add test running hooks
```

### IDE Integration

Configure your IDE to run tests:

- **VS Code**: Python Test Explorer
- **PyCharm**: Built-in pytest runner
- **Cursor**: Terminal integration

### Git Hooks

Add git hooks to run tests on commits:

```bash
#!/bin/sh
# .git/hooks/pre-commit
python run_tests.py --smoke
```

This comprehensive testing framework ensures robust, reliable testing of all application components while supporting continuous development and integration workflows.
