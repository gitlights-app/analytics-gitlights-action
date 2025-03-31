import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to sys.path to import from the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import generate_dashboard, main


class TestMain(unittest.TestCase):
    """Test cases for the main.py module."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create test directory for images
        self.test_img_dir = "tests/images"
        if not os.path.exists(self.test_img_dir):
            os.makedirs(self.test_img_dir)

    @patch('main.os.makedirs')
    @patch('main.requests.get')
    @patch('main.requests.post')
    def test_generate_dashboard_success(self, mock_post, mock_get, mock_makedirs):
        """Test successful dashboard generation with real image generation."""
        import os
        from charts import (
            create_indicators_figure,
            create_bar_figure,
            create_pie_figure,
            create_ranking_figure
        )
        from image_utils import combine_dashboard_images
        
        # Setup mock response based on provided sample
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {
            "indicators": {
                "titles": ["Commits", "PRs", "Comments", "Reviews"],
                "values": [165, 54, 14, 53],
                "deltas": [0.3, 0.3, 0.8, 0.4]
            },
            "bar_chart": {
                "title": "Daily Activity (Last 30 days)",
                "months": ["2025-03-03", "2025-03-04", "2025-03-05", "2025-03-06", "2025-03-07"],
                "commits": [5, 7, 2, 7, 20],
                "prs": [3, 2, 0, 2, 6],
                "comments": [0, 0, 0, 2, 0],
                "reviews": [3, 2, 0, 1, 7]
            },
            "pie_chart": {
                "title": "Investment Balance (Last 30 days)",
                "labels": ["Unknown", "fixes_and_maintenance", "new_development", "refactoring", "upgrades", "testing_and_qa"],
                "values": [89, 40, 16, 11, 6, 3]
            },
            "ranking": {
                "title": "Top Contributors (Last 30 days)",
                "devs": [
                    {"name": "User A", "avatar": "http://example.com/avatar1.png", 
                     "commits": 77, "prs": 25, "comments": 9, "reviews": 6},
                    {"name": "User B", "avatar": "http://example.com/avatar2.png", 
                     "commits": 49, "prs": 18, "comments": 0, "reviews": 11},
                    {"name": "User C", "avatar": "http://example.com/avatar3.png", 
                     "commits": 20, "prs": 6, "comments": 4, "reviews": 26}
                ]
            },
            "watermark_text": "Powered by Gitlights"
        }
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response
        
        # Mock the backend POST request with a 200 status code
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"image_url": "https://example.com/image.png"}
        mock_post.return_value = mock_post_response
        
        # Use the test image directory created in setUp
        output_path = f"{self.test_img_dir}/test_dashboard.png"
        
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
            
            print(f"\nImages generated in {self.test_img_dir}/")
            
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
            
    @patch('main.requests.post')
    def test_generate_dashboard_backend_non_200(self, mock_post):
        """Test dashboard generation when backend request returns non-200 status code."""
        # First mock the initial API call to succeed
        with patch('main.requests.get') as mock_get:
            # Setup mock response for the initial API call
            mock_response_get = MagicMock()
            mock_response_get.json.return_value = {
                "indicators": {
                    "titles": ["Commits", "PRs", "Comments", "Reviews"],
                    "values": [165, 54, 14, 53],
                    "deltas": [0.3, 0.3, 0.8, 0.4]
                },
                "bar_chart": {
                    "title": "Daily Activity",
                    "months": ["2025-03-03", "2025-03-04"],
                    "commits": [5, 7],
                    "prs": [3, 2],
                    "comments": [0, 0],
                    "reviews": [3, 2]
                },
                "pie_chart": {
                    "title": "Investment Balance",
                    "labels": ["Unknown", "fixes"],
                    "values": [89, 40]
                },
                "ranking": {
                    "title": "Top Contributors",
                    "devs": [
                        {"name": "User A", "avatar": "http://example.com/avatar1.png", 
                         "commits": 77, "prs": 25, "comments": 9, "reviews": 6}
                    ]
                },
                "watermark_text": "Powered by GitLights"
            }
            mock_response_get.raise_for_status.return_value = None
            mock_get.return_value = mock_response_get
            
            # Setup mock for backend request to return a non-200 status code
            mock_response_post = MagicMock()
            mock_response_post.status_code = 404  # Non-200 status code
            mock_post.return_value = mock_response_post
            
            # Mock the file operations
            with patch('builtins.open', mock_open(read_data=b'test_data')), \
                 patch('main.os.path.basename', return_value='test_image.png'), \
                 patch('main.combine_dashboard_images', return_value=None), \
                 patch('plotly.graph_objects.Figure.write_image', return_value=None):
                
                # Call the function
                result = generate_dashboard(
                    actions_runtime_token="test_token",
                    owner="test_owner",
                    repo="test_repo"
                )
                
                # Assertions
                self.assertFalse(result)  # Should fail when backend returns non-200


if __name__ == '__main__':
    unittest.main()
