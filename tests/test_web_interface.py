"""
Playwright tests for Interest Rate Calculator web interface
"""
import pytest
import json
import time
import sys
from pathlib import Path
from playwright.sync_api import Page, expect

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from playwright_config import config
except ImportError:
    # Fallback configuration
    class FallbackConfig:
        BASE_URL = "http://localhost:5000"
    config = FallbackConfig()

class TestWebInterface:
    """Test cases for the web interface functionality"""
    
    @pytest.mark.web
    @pytest.mark.smoke
    def test_homepage_loads(self, web_app: Page):
        """Test that the homepage loads correctly"""
        # Check page title
        expect(web_app).to_have_title("Interest Rate Calculator")
        
        # Check main heading
        heading = web_app.locator("h2")
        expect(heading).to_contain_text("Interest Rate Calculator — HTML")
        
        # Check main sections are present
        expect(web_app.locator("h3:has-text('Projects')")).to_be_visible()
        expect(web_app.locator("h3:has-text('SharePoint Folder Tree')")).to_be_visible()
        expect(web_app.locator("h3:has-text('Generate')")).to_be_visible()

    @pytest.mark.web
    def test_project_selection_dropdown(self, web_app: Page):
        """Test project selection dropdown functionality"""
        # Wait for projects to load
        web_app.wait_for_timeout(1000)
        
        # Check dropdown exists and has default option
        dropdown = web_app.locator("#proj")
        expect(dropdown).to_be_visible()
        
        # Check default project is available
        expect(dropdown.locator("option[value='<default>']")).to_be_visible()

    @pytest.mark.web
    def test_refresh_projects_button(self, web_app: Page):
        """Test the refresh projects button"""
        refresh_btn = web_app.locator("button:has-text('↻')")
        expect(refresh_btn).to_be_visible()
        
        # Click refresh button
        refresh_btn.click()
        
        # Wait for refresh to complete
        web_app.wait_for_timeout(1000)
        
        # Verify dropdown still has options
        dropdown = web_app.locator("#proj")
        expect(dropdown.locator("option")).to_have_count_greater_than(0)

    @pytest.mark.web
    def test_new_project_creation(self, web_app: Page):
        """Test creating a new project"""
        new_btn = web_app.locator("button:has-text('New')")
        expect(new_btn).to_be_visible()
        
        # Click new project button (this will trigger a prompt)
        # Note: We can't easily test prompts in Playwright, so we'll test the button exists
        # In a real test, you'd mock the prompt or use a different UI pattern

    @pytest.mark.web
    def test_sharepoint_search(self, web_app: Page):
        """Test SharePoint folder search functionality"""
        search_input = web_app.locator("#search")
        expect(search_input).to_be_visible()
        expect(search_input).to_have_attribute("placeholder", "Search folders...")
        
        # Test typing in search box
        search_input.fill("Ocean")
        
        # Wait for search results
        web_app.wait_for_timeout(500)
        
        # Check that tree is updated (basic check)
        tree = web_app.locator("#tree")
        expect(tree).to_be_visible()

    @pytest.mark.web
    def test_sharepoint_folder_tree(self, web_app: Page):
        """Test SharePoint folder tree display"""
        # Wait for tree to load
        web_app.wait_for_timeout(1000)
        
        tree = web_app.locator("#tree")
        expect(tree).to_be_visible()
        
        # Check for folder items (using stub data)
        folders = tree.locator("li")
        expect(folders).to_have_count_greater_than(0)

    @pytest.mark.web
    def test_folder_selection(self, web_app: Page):
        """Test selecting a folder from the tree"""
        # Wait for tree to load
        web_app.wait_for_timeout(1000)
        
        # Click on first folder
        first_folder = web_app.locator("#tree li").first
        if first_folder.is_visible():
            first_folder.click()
            
            # Wait for selection to process
            web_app.wait_for_timeout(500)
            
            # Check that selection is displayed
            selection_display = web_app.locator("#sel")
            expect(selection_display).to_be_visible()

    @pytest.mark.web
    def test_generate_outputs_button(self, web_app: Page):
        """Test the generate outputs functionality"""
        generate_btn = web_app.locator("button:has-text('Generate Outputs')")
        expect(generate_btn).to_be_visible()
        
        # Click generate button
        generate_btn.click()
        
        # Wait for generation to complete
        web_app.wait_for_timeout(3000)
        
        # Check output area
        output_area = web_app.locator("#out")
        expect(output_area).to_be_visible()

    @pytest.mark.web
    @pytest.mark.api
    def test_api_projects_endpoint(self, web_app: Page):
        """Test the /api/projects endpoint"""
        # Navigate directly to API endpoint
        response = web_app.request.get(f"{config.BASE_URL}/api/projects")
        assert response.status == 200
        
        data = response.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)

    @pytest.mark.web
    @pytest.mark.api
    def test_api_sharepoint_list_endpoint(self, web_app: Page):
        """Test the /api/sharepoint/list endpoint"""
        response = web_app.request.get(f"{config.BASE_URL}/api/sharepoint/list")
        assert response.status == 200
        
        data = response.json()
        assert "folders" in data
        assert isinstance(data["folders"], list)

    @pytest.mark.web
    @pytest.mark.api
    def test_api_sharepoint_search_endpoint(self, web_app: Page):
        """Test the /api/sharepoint/search endpoint"""
        response = web_app.request.get(f"{config.BASE_URL}/api/sharepoint/search?q=Ocean")
        assert response.status == 200
        
        data = response.json()
        assert "folders" in data
        assert isinstance(data["folders"], list)

    @pytest.mark.web
    @pytest.mark.api
    def test_api_project_get_endpoint(self, web_app: Page):
        """Test the /api/project/get endpoint"""
        response = web_app.request.get(f"{config.BASE_URL}/api/project/get?name=<default>")
        assert response.status == 200
        
        data = response.json()
        assert "title" in data
        assert "billing_date" in data
        assert "as_of_date" in data

    @pytest.mark.web
    @pytest.mark.api
    def test_api_generate_endpoint(self, web_app: Page):
        """Test the /api/generate endpoint"""
        response = web_app.request.post(f"{config.BASE_URL}/api/generate")
        assert response.status == 200
        
        data = response.json()
        assert "excel" in data
        assert "pdf" in data

class TestWebIntegration:
    """Integration tests for web interface workflows"""
    
    @pytest.mark.web
    @pytest.mark.integration
    def test_complete_project_workflow(self, web_app: Page):
        """Test complete project creation and management workflow"""
        # 1. Load homepage
        expect(web_app.locator("h2")).to_contain_text("Interest Rate Calculator")
        
        # 2. Select default project
        dropdown = web_app.locator("#proj")
        dropdown.select_option("<default>")
        
        # 3. Search for a folder
        search_input = web_app.locator("#search")
        search_input.fill("Ocean")
        web_app.wait_for_timeout(500)
        
        # 4. Select a folder (if available)
        first_folder = web_app.locator("#tree li").first
        if first_folder.is_visible():
            first_folder.click()
            web_app.wait_for_timeout(500)
        
        # 5. Generate outputs
        generate_btn = web_app.locator("button:has-text('Generate Outputs')")
        generate_btn.click()
        web_app.wait_for_timeout(3000)
        
        # 6. Verify output
        output_area = web_app.locator("#out")
        expect(output_area).to_be_visible()

    @pytest.mark.web
    @pytest.mark.integration
    @pytest.mark.slow
    def test_multiple_api_calls_performance(self, web_app: Page):
        """Test performance with multiple API calls"""
        start_time = time.time()
        
        # Make multiple API calls
        for _ in range(5):
            web_app.request.get(f"{config.BASE_URL}/api/projects")
            web_app.request.get(f"{config.BASE_URL}/api/sharepoint/list")
            web_app.request.get(f"{config.BASE_URL}/api/project/get?name=<default>")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (adjust as needed)
        assert duration < 10.0, f"API calls took too long: {duration}s"

class TestWebErrorHandling:
    """Test error handling in web interface"""
    
    @pytest.mark.web
    def test_invalid_api_endpoints(self, web_app: Page):
        """Test handling of invalid API endpoints"""
        response = web_app.request.get(f"{config.BASE_URL}/api/nonexistent")
        assert response.status == 404

    @pytest.mark.web
    def test_malformed_api_requests(self, web_app: Page):
        """Test handling of malformed API requests"""
        # Test POST without proper data
        response = web_app.request.post(f"{config.BASE_URL}/api/project/save")
        # Should handle gracefully (exact status depends on implementation)
        assert response.status in [400, 422, 500]

class TestWebAccessibility:
    """Test web interface accessibility"""
    
    @pytest.mark.web
    def test_keyboard_navigation(self, web_app: Page):
        """Test keyboard navigation through interface"""
        # Focus on first interactive element
        web_app.keyboard.press("Tab")
        
        # Should be able to navigate to dropdown
        focused = web_app.locator(":focus")
        expect(focused).to_be_visible()

    @pytest.mark.web
    def test_screen_reader_compatibility(self, web_app: Page):
        """Test basic screen reader compatibility"""
        # Check for proper heading structure
        h2_elements = web_app.locator("h2")
        expect(h2_elements).to_have_count(1)
        
        h3_elements = web_app.locator("h3")
        expect(h3_elements).to_have_count_greater_than(0)
        
        # Check for form labels (basic check)
        inputs = web_app.locator("input")
        for i in range(inputs.count()):
            input_elem = inputs.nth(i)
            # Should have placeholder or associated label
            placeholder = input_elem.get_attribute("placeholder")
            assert placeholder is not None or input_elem.get_attribute("aria-label") is not None
