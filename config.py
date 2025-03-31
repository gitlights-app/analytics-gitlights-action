"""
Configuration constants for the GitLights dashboard generation.
This file contains all the global configuration parameters used in the dashboard generation process.
"""

# Indicator chart configuration
INDICATOR_WIDTH = 2400
INDICATOR_HEIGHT = 300
INDICATOR_NUMBER_FONT_SIZE = 50
INDICATOR_FONT_FAMILY = "DejaVu Sans"
INDICATOR_FONT_SIZE = 40
INDICATOR_FONT_COLOR = "black"
INDICATOR_INCREASING_COLOR = "green"
INDICATOR_DECREASING_COLOR = "red"

# Bar chart configuration
BAR_CHART_WIDTH = 2400
BAR_CHART_HEIGHT = 800
BAR_CHART_TITLE_FONT_SIZE = 28
BAR_CHART_LEGEND_FONT_SIZE = 28
BAR_CHART_FONT_SIZE = 26
BAR_CHART_FONT_FAMILY = "DejaVu Sans"
BAR_CHART_FONT_COLOR = "black"
BAR_COLOR_COMMITS = "#AEC6CF"
BAR_COLOR_PRS = "#FFDAB9"
BAR_COLOR_ISSUES = "#FFB5E8"
BAR_CHART_LEGEND_Y_OFFSET = -0.2

# Pie chart configuration
PIE_CHART_WIDTH = 1200
PIE_CHART_HEIGHT = 800
PIE_TEXTINFO = "label+percent"
PIE_INSIDE_TEXT_ORIENTATION = "radial"

# Ranking table configuration
RANKING_WIDTH = 1200
RANKING_HEIGHT = 800
RANKING_TITLE_FONT_SIZE = 28
RANKING_TITLE_FONT_COLOR = "black"
RANKING_HEADER_FONT_SIZE = 22
RANKING_HEADER_FONT_COLOR = "black"
RANKING_CELL_FONT_SIZE = 22
RANKING_CELL_FONT_COLOR = "black"
RANKING_AXIS_RANGE = [0, 1]
RANKING_COLUMN_POSITIONS = {
    "dev":           0.15,  # Developer = avatar + name
    "commits":       0.42,
    "prs":           0.58,
    "issues":        0.74,
    "reviews":       0.90
}
RANKING_HEADERS = ["Developer", "Commits", "PR", "Comments", "Reviews"]
RANKING_MEDAL_COLORS = ["#FFD700", "#C0C0C0", "#CD7F32"]  # Gold, Silver, Bronze
RANKING_AVATAR_SIZE = 0.08

# Dashboard layout configuration
DASHBOARD_WIDTH = 2400
DASHBOARD_HEIGHT = 300 + 800 + 800  # 1900
DASHBOARD_BACKGROUND_COLOR = (255, 255, 255)  # White

# General plotly configuration
PLOTLY_TEMPLATE = "plotly_white"
BACKGROUND_COLOR = "white"

# Watermark and Logo Configuration
WATERMARK_FONT_SIZE = 30
WATERMARK_FONT_FAMILY = "DejaVuSans.ttf"
WATERMARK_TEXT_COLOR = (50, 50, 50)
WATERMARK_POSITION_OFFSET_X = 350
WATERMARK_POSITION_OFFSET_Y = 40

GITLIGHTS_LOGO_URL = "https://avatars.githubusercontent.com/ml/16163?s=400&v=4"
LOGO_MAX_SIZE = (75, 75)
LOGO_POSITION_X = 20
LOGO_POSITION_Y = 20

# API configuration
API_URL = "https://api.gitlights.com/api/gitlights-action/get-main-dashboard-data/"
