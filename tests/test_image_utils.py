import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to sys.path to import from the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from image_utils import encode_image_from_url, combine_dashboard_images


class TestImageUtils(unittest.TestCase):
    """Test cases for the image_utils.py module."""

    @patch('image_utils.requests.get')
    def test_encode_image_from_url_success(self, mock_get):
        """Test encode_image_from_url with successful image retrieval."""
        # Mock response with binary content
        mock_response = MagicMock()
        mock_response.content = b'test_image_content'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the function
        result = encode_image_from_url("http://example.com/image.png")
        
        # Assertions
        self.assertTrue(result.startswith('data:image/png;base64,'))
        mock_get.assert_called_once_with("http://example.com/image.png")

    @patch('image_utils.requests.get')
    def test_encode_image_from_url_failure(self, mock_get):
        """Test encode_image_from_url when image retrieval fails."""
        # Mock response to raise an exception
        mock_get.side_effect = Exception("Failed to download image")
        
        # Call the function
        result = encode_image_from_url("http://example.com/nonexistent.png")
        
        # Assertions
        self.assertEqual(result, "")
        mock_get.assert_called_once_with("http://example.com/nonexistent.png")

    @patch('image_utils.Image.new')
    @patch('image_utils.ImageDraw.Draw')
    @patch('image_utils.ImageFont.truetype')
    @patch('image_utils.requests.get')
    def test_combine_dashboard_images(self, mock_get, mock_truetype, mock_draw, mock_image_new):
        """Test combine_dashboard_images function."""
        # Mock PIL Image and Draw objects
        mock_dashboard = MagicMock()
        mock_ind_img = MagicMock()
        mock_bar_img = MagicMock()
        mock_pie_img = MagicMock()
        mock_rank_img = MagicMock()
        mock_draw_obj = MagicMock()
        mock_font = MagicMock()
        mock_logo = MagicMock()
        
        # Setup return values
        mock_image_new.return_value = mock_dashboard
        mock_draw.return_value = mock_draw_obj
        mock_truetype.return_value = mock_font
        
        # Mock logo response
        mock_response = MagicMock()
        mock_response.content = b'logo_content'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # We need to patch Image.open in a way that works for both the chart images and the logo
        with patch('image_utils.Image.open') as mock_image_open:
            # Set up the mock to return different values for different calls
            mock_image_open.side_effect = [mock_ind_img, mock_bar_img, mock_pie_img, mock_rank_img, mock_logo]
            
            # Configure the mock logo
            mock_logo.convert.return_value = mock_logo
            mock_logo.height = 50  # Set a height for the logo
            
            # Mock BytesIO
            with patch('image_utils.BytesIO') as mock_bytesio:
                mock_bytesio_instance = MagicMock()
                mock_bytesio.return_value = mock_bytesio_instance
                
                # Call the function
                combine_dashboard_images(
                    indicators_path="indicators.png",
                    bar_path="bar.png",
                    pie_path="pie.png",
                    ranking_path="ranking.png",
                    watermark_text="Test Watermark",
                    output_path="test_output.png"
                )
                
                # Assertions
                mock_image_new.assert_called_once()
                # Should be called 5 times: 4 for chart images and 1 for logo
                self.assertEqual(mock_image_open.call_count, 5)
                
                # Verify the images were pasted
                # 4 charts + logo = 5 paste calls
                self.assertEqual(mock_dashboard.paste.call_count, 5)
                
                # Verify the watermark was added
                mock_draw_obj.text.assert_called_once()
                
                # Verify the final image was saved
                mock_dashboard.save.assert_called_once_with("test_output.png")

    @patch('image_utils.Image.new')
    @patch('image_utils.Image.open')
    @patch('image_utils.ImageDraw.Draw')
    @patch('image_utils.ImageFont.truetype')
    @patch('image_utils.requests.get')
    def test_combine_dashboard_images_font_exception(self, mock_get, mock_truetype, 
                                                  mock_draw, mock_image_open, mock_image_new):
        """Test combine_dashboard_images when font loading fails."""
        # Mock PIL Image and Draw objects
        mock_dashboard = MagicMock()
        mock_ind_img = MagicMock()
        mock_bar_img = MagicMock()
        mock_pie_img = MagicMock()
        mock_rank_img = MagicMock()
        mock_draw_obj = MagicMock()
        mock_default_font = MagicMock()
        
        # Setup return values
        mock_image_new.return_value = mock_dashboard
        mock_image_open.side_effect = [mock_ind_img, mock_bar_img, mock_pie_img, mock_rank_img]
        mock_draw.return_value = mock_draw_obj
        
        # Font exception
        mock_truetype.side_effect = Exception("Font not found")
        
        # Mock logo response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock default font
        with patch('image_utils.ImageFont.load_default', return_value=mock_default_font):
            with patch('image_utils.BytesIO'):
                with patch('image_utils.Image.open') as mock_logo_open:
                    mock_logo = MagicMock()
                    mock_logo_open.return_value = mock_logo
                    mock_logo.convert.return_value = mock_logo
                    mock_logo.height = 50
                    
                    # Call the function
                    combine_dashboard_images(
                        indicators_path="indicators.png",
                        bar_path="bar.png",
                        pie_path="pie.png",
                        ranking_path="ranking.png",
                        watermark_text="Test Watermark",
                        output_path="test_output.png"
                    )
                    
                    # Assertions - should use default font
                    mock_draw_obj.text.assert_called_once()
                    
    @patch('image_utils.Image.new')
    @patch('image_utils.Image.open')
    @patch('image_utils.ImageDraw.Draw')
    @patch('image_utils.ImageFont.truetype')
    @patch('image_utils.requests.get')
    def test_combine_dashboard_images_logo_exception(self, mock_get, mock_truetype, 
                                                  mock_draw, mock_image_open, mock_image_new):
        """Test combine_dashboard_images when logo retrieval fails."""
        # Mock PIL Image and Draw objects
        mock_dashboard = MagicMock()
        mock_ind_img = MagicMock()
        mock_bar_img = MagicMock()
        mock_pie_img = MagicMock()
        mock_rank_img = MagicMock()
        mock_draw_obj = MagicMock()
        mock_font = MagicMock()
        
        # Setup return values
        mock_image_new.return_value = mock_dashboard
        mock_image_open.side_effect = [mock_ind_img, mock_bar_img, mock_pie_img, mock_rank_img]
        mock_draw.return_value = mock_draw_obj
        mock_truetype.return_value = mock_font
        
        # Logo exception
        mock_get.side_effect = Exception("Failed to download logo")
        
        # Call the function
        combine_dashboard_images(
            indicators_path="indicators.png",
            bar_path="bar.png",
            pie_path="pie.png",
            ranking_path="ranking.png",
            watermark_text="Test Watermark",
            output_path="test_output.png"
        )
        
        # Assertions
        # Should still save the image even if logo retrieval fails
        mock_dashboard.save.assert_called_once_with("test_output.png")


if __name__ == '__main__':
    unittest.main()
