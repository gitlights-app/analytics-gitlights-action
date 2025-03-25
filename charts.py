# charts.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import configuration values from config.py
from config import (
    # Indicator chart config
    INDICATOR_WIDTH, INDICATOR_HEIGHT, INDICATOR_NUMBER_FONT_SIZE,
    INDICATOR_FONT_FAMILY, INDICATOR_FONT_SIZE, INDICATOR_FONT_COLOR,
    INDICATOR_INCREASING_COLOR, INDICATOR_DECREASING_COLOR,
    
    # Bar chart config
    BAR_CHART_WIDTH, BAR_CHART_HEIGHT, BAR_CHART_TITLE_FONT_SIZE,
    BAR_CHART_LEGEND_FONT_SIZE, BAR_CHART_FONT_SIZE, BAR_CHART_FONT_FAMILY,
    BAR_CHART_FONT_COLOR, BAR_COLOR_COMMITS, BAR_COLOR_PRS, BAR_COLOR_ISSUES,
    BAR_CHART_LEGEND_Y_OFFSET,
    
    # Pie chart config
    PIE_CHART_WIDTH, PIE_CHART_HEIGHT, PIE_TEXTINFO, PIE_INSIDE_TEXT_ORIENTATION,
    
    # Ranking table config
    RANKING_AXIS_RANGE, RANKING_COLUMN_POSITIONS,
    RANKING_TITLE_FONT_SIZE, RANKING_TITLE_FONT_COLOR, RANKING_HEADERS,
    RANKING_HEADER_FONT_SIZE, RANKING_HEADER_FONT_COLOR,
    RANKING_CELL_FONT_SIZE, RANKING_CELL_FONT_COLOR,
    RANKING_MEDAL_COLORS, RANKING_AVATAR_SIZE,
    
    # General plotly config
    PLOTLY_TEMPLATE, BACKGROUND_COLOR
)

# Import function to convert image URLs to base64
from image_utils import encode_image_from_url

def create_indicators_figure(titles, values, deltas):
    """
    Creates a figure with 4 indicators (1 row, 4 columns).
    Each indicator shows a value and its delta (green if positive, red if negative).

    Args:
        titles (list): List with the titles of each indicator.
        values (list): List with the numerical values of each indicator.
        deltas (list): List of deltas, as fractions. Example: 0.05 indicates +5%.

    Returns:
        plotly.graph_objs._figure.Figure: Figure with the 4 indicators.
    """
    fig_ind = make_subplots(
        rows=1, cols=4,
        subplot_titles=titles,
        specs=[[{"type": "indicator"}]*4]
    )

    for i in range(4):
        base_val = values[i]
        delta_val = deltas[i]  # fracción de cambio
        ref_val = base_val / (1 + delta_val) if delta_val != -1 else 0

        fig_ind.add_trace(
            go.Indicator(
                mode="number+delta",
                value=base_val,
                delta={
                    "reference": ref_val,
                    "valueformat": ".1f",
                    "increasing": {"color": INDICATOR_INCREASING_COLOR},
                    "decreasing": {"color": INDICATOR_DECREASING_COLOR}
                },
                number={"font": {"size": INDICATOR_NUMBER_FONT_SIZE, "color": INDICATOR_FONT_COLOR}}
            ),
            row=1, col=i+1
        )

    fig_ind.update_layout(
        template=PLOTLY_TEMPLATE,
        width=INDICATOR_WIDTH,
        height=INDICATOR_HEIGHT,
        font=dict(family=INDICATOR_FONT_FAMILY, size=INDICATOR_FONT_SIZE, color=INDICATOR_FONT_COLOR),
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR
    )
    return fig_ind


def create_bar_figure(cfg_bar):
    """
    Creates a stacked bar chart.
    cfg_bar is a dictionary with keys: "title", "months", "commits", "prs", "issues".

    Args:
        cfg_bar (dict): Parameters for the bar chart. Must contain:
            - title (str): Chart title
            - months (list): List of months (X axis)
            - commits (list): Commit data
            - prs (list): PR data
            - issues (list): Issue data

    Returns:
        plotly.graph_objs._figure.Figure: Stacked bar chart figure.
    """
    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        name="Commits",
        x=cfg_bar["months"],
        y=cfg_bar["commits"],
        marker_color=BAR_COLOR_COMMITS
    ))
    fig_bar.add_trace(go.Bar(
        name="Pull Requests",
        x=cfg_bar["months"],
        y=cfg_bar["prs"],
        marker_color=BAR_COLOR_PRS
    ))
    fig_bar.add_trace(go.Bar(
        name="Issues",
        x=cfg_bar["months"],
        y=cfg_bar["issues"],
        marker_color=BAR_COLOR_ISSUES
    ))

    fig_bar.update_layout(
        template=PLOTLY_TEMPLATE,
        title={
            "text": cfg_bar["title"],
            "font": {"size": BAR_CHART_TITLE_FONT_SIZE, "color": BAR_CHART_FONT_COLOR}
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=BAR_CHART_LEGEND_Y_OFFSET,
            xanchor="center",
            x=0.5,
            font=dict(size=BAR_CHART_LEGEND_FONT_SIZE, color=BAR_CHART_FONT_COLOR)
        ),
        barmode="stack",
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        width=BAR_CHART_WIDTH,
        height=BAR_CHART_HEIGHT,
        font=dict(family=BAR_CHART_FONT_FAMILY, size=BAR_CHART_FONT_SIZE, color=BAR_CHART_FONT_COLOR)
    )
    return fig_bar


def create_pie_figure(cfg_pie):
    """
    Creates a pie chart.
    cfg_pie is a dictionary with keys: "title", "labels", "values".

    Args:
        cfg_pie (dict): Parameters for the pie chart. Must contain:
            - title (str): Title
            - labels (list): Labels
            - values (list): Values

    Returns:
        plotly.graph_objs._figure.Figure: Pie chart figure.
    """
    fig_pie = go.Figure()
    fig_pie.add_trace(go.Pie(
        labels=cfg_pie["labels"],
        values=cfg_pie["values"],
        textinfo=PIE_TEXTINFO,
        insidetextorientation=PIE_INSIDE_TEXT_ORIENTATION
    ))

    fig_pie.update_layout(
        template=PLOTLY_TEMPLATE,
        title={
            "text": cfg_pie["title"],
            "font": {"size": BAR_CHART_TITLE_FONT_SIZE, "color": BAR_CHART_FONT_COLOR}
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        width=PIE_CHART_WIDTH,
        height=PIE_CHART_HEIGHT,
        font=dict(family=BAR_CHART_FONT_FAMILY, size=BAR_CHART_FONT_SIZE, color=BAR_CHART_FONT_COLOR)
    )
    return fig_pie


def create_ranking_figure(cfg_rank):
    """
    Creates the developer ranking table (with avatar and metrics).
    cfg_rank: {
        "title": "...",
        "devs": [
            {
                "name": "...",
                "avatar": "http://url_avatar",
                "commits": ...,
                "prs": ...,
                "issues": ...,
                "reviews": ...,
                "contributions": ...
            },
            ...
        ]
    }

    Returns:
        plotly.graph_objs._figure.Figure: Figure with the ranking table.
    """
    fig_rank = go.Figure()

    # Configure invisible axes
    fig_rank.update_xaxes(range=RANKING_AXIS_RANGE, visible=False)
    fig_rank.update_yaxes(range=RANKING_AXIS_RANGE, visible=False)

    fig_rank.update_layout(
        template=PLOTLY_TEMPLATE,
        title={
            "text": cfg_rank["title"],
            "font": {"size": RANKING_TITLE_FONT_SIZE, "color": RANKING_TITLE_FONT_COLOR}
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        width=1200,
        height=800
    )

    devs = cfg_rank["devs"]
    # Row calculation
    n_rows = len(devs) + 2
    row_height = 1.0 / n_rows

    header_row_index = 1
    y_header = 1 - row_height * header_row_index + row_height / 2

    col_positions = RANKING_COLUMN_POSITIONS
    headers = RANKING_HEADERS

    # Header rendering
    for i, header in enumerate(headers):
        if i == 0:
            x_pos = col_positions["dev"]
        elif i == 1:
            x_pos = col_positions["commits"]
        elif i == 2:
            x_pos = col_positions["prs"]
        elif i == 3:
            x_pos = col_positions["issues"]
        elif i == 4:
            x_pos = col_positions["reviews"]
        else:
            x_pos = col_positions["contributions"]

        fig_rank.add_annotation(
            x=x_pos,
            y=y_header,
            text=f"<b>{header}</b>",
            xref="x", yref="y",
            showarrow=False,
            font=dict(color=RANKING_HEADER_FONT_COLOR, size=RANKING_HEADER_FONT_SIZE)
        )

    # Rendering of each developer row
    for i, dev in enumerate(devs):
        row_index = i + 2
        y_pos = 1 - row_height * row_index + row_height / 2

        dev_name = dev["name"]
        font_color = RANKING_CELL_FONT_COLOR

        # Medals for top 3
        if i == 0:  # 1st place
            dev_name = f"<b>{dev_name}</b>"
            font_color = RANKING_MEDAL_COLORS[0]  # Gold
        elif i == 1:  # 2nd place
            dev_name = f"<b>{dev_name}</b>"
            font_color = RANKING_MEDAL_COLORS[1]  # Silver
        elif i == 2:  # 3rd place
            dev_name = f"<b>{dev_name}</b>"
            font_color = RANKING_MEDAL_COLORS[2]  # Bronze

        # Name
        fig_rank.add_annotation(
            x=col_positions["dev"] + 0.05,
            y=y_pos,
            text=dev_name,
            xref="x", yref="y",
            showarrow=False,
            font=dict(color=font_color, size=RANKING_CELL_FONT_SIZE)
        )

        # Commits
        fig_rank.add_annotation(
            x=col_positions["commits"],
            y=y_pos,
            text=str(dev["commits"]),
            xref="x", yref="y",
            showarrow=False,
            font=dict(color=RANKING_CELL_FONT_COLOR, size=RANKING_CELL_FONT_SIZE)
        )

        # PRs
        fig_rank.add_annotation(
            x=col_positions["prs"],
            y=y_pos,
            text=str(dev["prs"]),
            xref="x", yref="y",
            showarrow=False,
            font=dict(color=RANKING_CELL_FONT_COLOR, size=RANKING_CELL_FONT_SIZE)
        )

        # Issues
        fig_rank.add_annotation(
            x=col_positions["issues"],
            y=y_pos,
            text=str(dev["issues"]),
            xref="x", yref="y",
            showarrow=False,
            font=dict(color=RANKING_CELL_FONT_COLOR, size=RANKING_CELL_FONT_SIZE)
        )

        # Reviews
        fig_rank.add_annotation(
            x=col_positions["reviews"],
            y=y_pos,
            text=str(dev["reviews"]),
            xref="x", yref="y",
            showarrow=False,
            font=dict(color=RANKING_CELL_FONT_COLOR, size=RANKING_CELL_FONT_SIZE)
        )

        # Total contributions
        fig_rank.add_annotation(
            x=col_positions["contributions"],
            y=y_pos,
            text=str(dev["contributions"]),
            xref="x", yref="y",
            showarrow=False,
            font=dict(color=RANKING_CELL_FONT_COLOR, size=RANKING_CELL_FONT_SIZE)
        )

        # Avatar
        avatar_encoded = encode_image_from_url(dev["avatar"])
        fig_rank.add_layout_image(
            dict(
                source=avatar_encoded,
                x=col_positions["dev"] - RANKING_AVATAR_SIZE,
                y=y_pos + 0.05,
                xref="x",
                yref="y",
                sizex=RANKING_AVATAR_SIZE,
                sizey=RANKING_AVATAR_SIZE,
                xanchor="left",
                yanchor="top"
            )
        )

    return fig_rank
