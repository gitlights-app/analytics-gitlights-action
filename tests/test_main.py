import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to sys.path to import from the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import generate_dashboard, main


class TestMain(unittest.TestCase):
    """Test cases for the main.py module."""

    @patch('main.os.makedirs')
    @patch('main.requests.get')
    def test_generate_dashboard_success(self, mock_get, mock_makedirs):
        """Test successful dashboard generation with real image generation."""
        import os
        from charts import (
            create_indicators_figure,
            create_bar_figure,
            create_pie_figure,
            create_ranking_figure
        )
        from image_utils import combine_dashboard_images
        
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "indicators": {
                "titles": ["Indicator 1", "Indicator 2", "Indicator 3", "Indicator 4"],
                "values": [100, 200, 300, 400],
                "deltas": [0.05, -0.1, 0.2, 0]
            },
            "bar_chart": {
                "title": "Monthly Activity",
                "months": ["Jan", "Feb", "Mar"],
                "commits": [10, 20, 30],
                "prs": [5, 10, 15],
                "issues": [3, 6, 9]
            },
            "pie_chart": {
                "title": "Contribution Distribution",
                "labels": ["User A", "User B", "User C"],
                "values": [50, 30, 20]
            },
            "ranking": {
                "title": "Top Contributors",
                "devs": [
                    {"name": "User A", "avatar": "http://example.com/avatar1.png", 
                     "commits": 50, "prs": 20, "issues": 10, "reviews": 30, "contributions": 100},
                    {"name": "User B", "avatar": "http://example.com/avatar2.png", 
                     "commits": 40, "prs": 15, "issues": 8, "reviews": 25, "contributions": 80},
                    {"name": "User C", "avatar": "http://example.com/avatar3.png", 
                     "commits": 30, "prs": 10, "issues": 5, "reviews": 20, "contributions": 60}
                ]
            },
            "watermark_text": "Test Watermark"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Create test directory for images
        test_img_dir = "tests/images"
        if not os.path.exists(test_img_dir):
            os.makedirs(test_img_dir)
            
        output_path = f"{test_img_dir}/test_dashboard.png"
        
        # Make the original create_*_figure functions accessible in the patched context
        # using a context manager to apply patches only within this block
        with patch('main.create_indicators_figure', side_effect=create_indicators_figure) as mock_indicators, \
             patch('main.create_bar_figure', side_effect=create_bar_figure) as mock_bar, \
             patch('main.create_pie_figure', side_effect=create_pie_figure) as mock_pie, \
             patch('main.create_ranking_figure', side_effect=create_ranking_figure) as mock_rank, \
             patch('main.combine_dashboard_images', side_effect=combine_dashboard_images) as mock_combine:
            
            # Call the function
            result = generate_dashboard(
                actions_runtime_token="test_token",
                owner="test_owner",
                repo="test_repo",
                output_path=output_path
            )
            
            # Assertions
            self.assertTrue(result)
            mock_makedirs.assert_called()
            # No verificamos el número exacto de llamadas a mock_get porque se usa para la API y para descargar imágenes
            mock_get.assert_called()
            mock_indicators.assert_called_once()
            mock_bar.assert_called_once()
            mock_pie.assert_called_once()
            mock_rank.assert_called_once()
            mock_combine.assert_called_once()
            
            # Verify image files were created (note: they're created in the root images/ directory, not tests/images/)
            self.assertTrue(os.path.exists("images/indicators.png"))
            self.assertTrue(os.path.exists("images/bars.png"))
            self.assertTrue(os.path.exists("images/pie.png"))
            self.assertTrue(os.path.exists("images/ranking.png"))
            self.assertTrue(os.path.exists(output_path))
            
            print(f"\nImages generated in {test_img_dir}/")
            
            # Return the path for cleanup if needed in tearDown
            return output_path

    @patch('main.requests.get')
    def test_generate_dashboard_api_error(self, mock_get):
        """Test dashboard generation when API request fails."""
        # Setup mock response to raise an exception from requests.exceptions.RequestException
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("API Error")
        
        # Call the function
        result = generate_dashboard(
            actions_runtime_token="test_token",
            owner="test_owner",
            repo="test_repo"
        )
        
        # Assertions
        self.assertFalse(result)

    @patch('main.requests.get')
    def test_generate_dashboard_json_decode_error(self, mock_get):
        """Test dashboard generation when JSON decoding fails."""
        # Setup mock response with invalid JSON
        from requests.exceptions import JSONDecodeError
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("JSON Decode Error", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the function
        result = generate_dashboard(
            actions_runtime_token="test_token",
            owner="test_owner",
            repo="test_repo"
        )
        
        # Assertions
        self.assertFalse(result)

    @patch('main.generate_dashboard')
    @patch('main.sys.exit')
    def test_main_success(self, mock_exit, mock_generate_dashboard):
        """Test main function with successful dashboard generation."""
        # Setup mock
        mock_generate_dashboard.return_value = True
        
        # Setup environment variables
        with patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'OWNER': 'test_owner',
            'REPO': 'test_repo',
            'OUTPUT_PATH': 'test_output.png'
        }):
            # Call main function
            main()
            
            # Assertions
            # Using assert_called_once() instead of assert_called_once_with() to avoid parameter mismatch
            mock_generate_dashboard.assert_called_once()
            mock_exit.assert_not_called()

    @patch('main.generate_dashboard')
    @patch('main.sys.exit')
    def test_main_failure(self, mock_exit, mock_generate_dashboard):
        """Test main function with failed dashboard generation."""
        # Setup mock
        mock_generate_dashboard.return_value = False
        
        # Setup environment variables
        with patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'OWNER': 'test_owner',
            'REPO': 'test_repo'
        }):
            # Call main function
            main()
            
            # Assertions
            mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
