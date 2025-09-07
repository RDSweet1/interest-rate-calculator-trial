"""
Playwright Configuration for Interest Rate Calculator Web Testing
"""
import os
from playwright.sync_api import Playwright, Browser, BrowserContext, Page

class PlaywrightConfig:
    """Configuration class for Playwright testing setup"""
    
    # Base URLs
    BASE_URL = "http://localhost:5000"
    
    # Browser settings
    HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() == "true"
    BROWSER_TYPE = os.getenv("PLAYWRIGHT_BROWSER", "chromium")  # chromium, firefox, webkit
    
    # Viewport settings
    VIEWPORT_WIDTH = 1280
    VIEWPORT_HEIGHT = 720
    
    # Timeouts (in milliseconds)
    DEFAULT_TIMEOUT = 30000
    NAVIGATION_TIMEOUT = 30000
    ACTION_TIMEOUT = 10000
    
    # Test data directories
    SCREENSHOTS_DIR = "tests/screenshots"
    VIDEOS_DIR = "tests/videos"
    TRACES_DIR = "tests/traces"
    
    # Flask app settings
    FLASK_ENV = "testing"
    FLASK_PORT = 5000
    
    @classmethod
    def get_browser_config(cls):
        """Get browser configuration for Playwright"""
        return {
            "headless": cls.HEADLESS,
            "viewport": {"width": cls.VIEWPORT_WIDTH, "height": cls.VIEWPORT_HEIGHT},
            "slow_mo": 100 if not cls.HEADLESS else 0,  # Slow down for visual debugging
        }
    
    @classmethod
    def get_context_config(cls):
        """Get browser context configuration"""
        return {
            "viewport": {"width": cls.VIEWPORT_WIDTH, "height": cls.VIEWPORT_HEIGHT},
            "record_video_dir": cls.VIDEOS_DIR if not cls.HEADLESS else None,
            "record_video_size": {"width": cls.VIEWPORT_WIDTH, "height": cls.VIEWPORT_HEIGHT},
        }
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories for test artifacts"""
        for directory in [cls.SCREENSHOTS_DIR, cls.VIDEOS_DIR, cls.TRACES_DIR]:
            os.makedirs(directory, exist_ok=True)

# Global configuration instance
config = PlaywrightConfig()
