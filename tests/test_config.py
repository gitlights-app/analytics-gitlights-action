import os
import sys
import unittest

# Add the parent directory to sys.path to import from the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config


class TestConfig(unittest.TestCase):
    """Test cases for the config.py module."""

    def test_indicator_config_values(self):
        """Test indicator configuration values."""
        self.assertEqual(config.INDICATOR_WIDTH, 2400)
        self.assertEqual(config.INDICATOR_HEIGHT, 300)
        self.assertEqual(config.INDICATOR_NUMBER_FONT_SIZE, 50)
        self.assertEqual(config.INDICATOR_FONT_FAMILY, "DejaVu Sans")
        self.assertEqual(config.INDICATOR_FONT_COLOR, "black")
        self.assertEqual(config.INDICATOR_INCREASING_COLOR, "green")
        self.assertEqual(config.INDICATOR_DECREASING_COLOR, "red")

    def test_bar_chart_config_values(self):
        """Test bar chart configuration values."""
        self.assertEqual(config.BAR_CHART_WIDTH, 2400)
        self.assertEqual(config.BAR_CHART_HEIGHT, 800)
        self.assertEqual(config.BAR_CHART_TITLE_FONT_SIZE, 28)
        self.assertEqual(config.BAR_CHART_FONT_FAMILY, "DejaVu Sans")
        self.assertEqual(config.BAR_COLOR_COMMITS, "#AEC6CF")
        self.assertEqual(config.BAR_COLOR_PRS, "#FFDAB9")
        self.assertEqual(config.BAR_COLOR_ISSUES, "#FFB5E8")

    def test_pie_chart_config_values(self):
        """Test pie chart configuration values."""
        self.assertEqual(config.PIE_CHART_WIDTH, 1200)
        self.assertEqual(config.PIE_CHART_HEIGHT, 800)
        self.assertEqual(config.PIE_TEXTINFO, "label+percent")
        self.assertEqual(config.PIE_INSIDE_TEXT_ORIENTATION, "radial")

    def test_ranking_config_values(self):
        """Test ranking configuration values."""
        self.assertEqual(config.RANKING_WIDTH, 1200)
        self.assertEqual(config.RANKING_HEIGHT, 800)
        self.assertEqual(config.RANKING_TITLE_FONT_SIZE, 28)
        self.assertEqual(config.RANKING_AXIS_RANGE, [0, 1])
        self.assertEqual(len(config.RANKING_HEADERS), 5)
        self.assertEqual(config.RANKING_HEADERS[0], "Developer")
        self.assertEqual(len(config.RANKING_MEDAL_COLORS), 3)

    def test_dashboard_config_values(self):
        """Test dashboard configuration values."""
        self.assertEqual(config.DASHBOARD_WIDTH, 2400)
        self.assertEqual(config.DASHBOARD_HEIGHT, 300 + 800 + 800)  # 1900
        self.assertEqual(config.DASHBOARD_BACKGROUND_COLOR, (255, 255, 255))

    def test_watermark_and_logo_config(self):
        """Test watermark and logo configuration."""
        self.assertEqual(config.WATERMARK_FONT_SIZE, 30)
        self.assertEqual(config.WATERMARK_FONT_FAMILY, "DejaVuSans.ttf")
        self.assertEqual(config.WATERMARK_TEXT_COLOR, (50, 50, 50))
        self.assertEqual(config.LOGO_MAX_SIZE, (75, 75))

    def test_api_config(self):
        """Test API configuration."""
        self.assertEqual(config.API_URL, "https://api.gitlights.com/api/gitlights-action/get-main-dashboard-data/")


if __name__ == '__main__':
    unittest.main()
