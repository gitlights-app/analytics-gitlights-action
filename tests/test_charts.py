import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import from the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from charts import (
    create_indicators_figure,
    create_bar_figure,
    create_pie_figure,
    create_ranking_figure
)


class TestCharts(unittest.TestCase):
    """Test cases for the charts.py module."""

    def test_create_indicators_figure(self):
        """Test create_indicators_figure function."""
        # Test data
        titles = ["Indicator 1", "Indicator 2", "Indicator 3", "Indicator 4"]
        values = [100, 200, 300, 400]
        deltas = [0.05, -0.1, 0.2, 0]
        
        # Call the function
        fig = create_indicators_figure(titles, values, deltas)
        
        # Basic assertions (we can't deeply validate the plotly figure)
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 4)  # Should have 4 indicators
        
        # Verify delta values in each indicator
        for i, trace in enumerate(fig.data):
            self.assertEqual(trace.value, values[i])
            delta_ref = values[i] / (1 + deltas[i]) if deltas[i] != -1 else 0
            self.assertEqual(trace.delta.reference, delta_ref)

    def test_create_bar_figure(self):
        """Test create_bar_figure function."""
        # Test data
        cfg_bar = {
            "title": "Monthly Activity",
            "months": ["Jan", "Feb", "Mar"],
            "commits": [10, 20, 30],
            "prs": [5, 10, 15],
            "comments": [3, 6, 9],
            "reviews": [4, 8, 12]
        }
        
        # Call the function
        fig = create_bar_figure(cfg_bar)
        
        # Assertions
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 4)  # Should have 4 bar series (commits, PRs, comments, reviews)
        
        # Check data for each series
        self.assertEqual(fig.data[0].name, "Commits")
        self.assertEqual(list(fig.data[0].x), cfg_bar["months"])
        self.assertEqual(list(fig.data[0].y), cfg_bar["commits"])
        
        self.assertEqual(fig.data[1].name, "Pull Requests")
        self.assertEqual(list(fig.data[1].x), cfg_bar["months"])
        self.assertEqual(list(fig.data[1].y), cfg_bar["prs"])
        
        self.assertEqual(fig.data[2].name, "Comments")
        self.assertEqual(list(fig.data[2].x), cfg_bar["months"])
        self.assertEqual(list(fig.data[2].y), cfg_bar["comments"])
        
        self.assertEqual(fig.data[3].name, "Reviews")
        self.assertEqual(list(fig.data[3].x), cfg_bar["months"])
        self.assertEqual(list(fig.data[3].y), cfg_bar["reviews"])
        
        # Check title
        self.assertEqual(fig.layout.title.text, cfg_bar["title"])

    def test_create_pie_figure(self):
        """Test create_pie_figure function."""
        # Test data
        cfg_pie = {
            "title": "Contribution Distribution",
            "labels": ["User A", "User B", "User C"],
            "values": [50, 30, 20]
        }
        
        # Call the function
        fig = create_pie_figure(cfg_pie)
        
        # Assertions
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)  # Should have 1 pie chart
        
        # Check pie chart data
        pie_data = fig.data[0]
        self.assertEqual(list(pie_data.labels), cfg_pie["labels"])
        self.assertEqual(list(pie_data.values), cfg_pie["values"])
        
        # Check title
        self.assertEqual(fig.layout.title.text, cfg_pie["title"])

    @patch('charts.encode_image_from_url')
    def test_create_ranking_figure(self, mock_encode_image):
        """Test create_ranking_figure function."""
        # Mock the image encoding function
        mock_encode_image.return_value = "data:image/png;base64,mockedbase64data"
        
        # Test data
        cfg_rank = {
            "title": "Top Contributors",
            "devs": [
                {
                    "name": "User A",
                    "avatar": "http://example.com/avatar1.png",
                    "commits": 50,
                    "prs": 20,
                    "comments": 10,
                    "reviews": 30
                },
                {
                    "name": "User B",
                    "avatar": "http://example.com/avatar2.png",
                    "commits": 40,
                    "prs": 15,
                    "comments": 8,
                    "reviews": 25
                }
            ]
        }
        
        # Call the function
        fig = create_ranking_figure(cfg_rank)
        
        # Assertions
        self.assertIsNotNone(fig)
        # In Plotly, annotations can be a tuple or list depending on the version
        self.assertTrue(isinstance(fig.layout.annotations, tuple))
        
        # Convert to list if it's a tuple for easier iteration
        annotations = list(fig.layout.annotations)
        
        # Check if headers are in annotations
        for header in ["Developer", "Commits", "PR", "Comments", "Reviews"]:
            header_annotation = next((a for a in annotations if f"<b>{header}</b>" in a.text), None)
            self.assertIsNotNone(header_annotation, f"Header '{header}' not found in annotations")
        
        # Check if dev names are in annotations
        for dev in cfg_rank["devs"]:
            dev_annotation = next((a for a in annotations if f"<b>{dev['name']}</b>" in a.text), None)
            self.assertIsNotNone(dev_annotation, f"Developer '{dev['name']}' not found in annotations")
            
            # Check if metrics are in annotations
            metrics = ["commits", "prs", "comments", "reviews"]
            for metric in metrics:
                metric_value = str(dev[metric])
                metric_annotation = next((a for a in annotations if a.text == metric_value), None)
                self.assertIsNotNone(metric_annotation, f"Metric '{metric}' with value '{metric_value}' not found for {dev['name']}")
        
        # Verify the image encoding function was called for each avatar
        self.assertEqual(mock_encode_image.call_count, len(cfg_rank["devs"]))


if __name__ == '__main__':
    unittest.main()
