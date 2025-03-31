# image_utils.py
import base64
import requests
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

# Import configuration values
from config import (
    DASHBOARD_WIDTH, DASHBOARD_HEIGHT, DASHBOARD_BACKGROUND_COLOR,
    WATERMARK_FONT_SIZE, WATERMARK_FONT_FAMILY, WATERMARK_TEXT_COLOR,
    WATERMARK_POSITION_OFFSET_X, WATERMARK_POSITION_OFFSET_Y,
    GITLIGHTS_LOGO_URL, LOGO_MAX_SIZE, LOGO_POSITION_X, LOGO_POSITION_Y
)

def encode_image_from_url(url):
    """
    Downloads the image from the URL and returns it in base64 to use in layout_image (Plotly).
    """
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        encoded = base64.b64encode(resp.content).decode('ascii')
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Error downloading image: {e}")
        return ""

def combine_dashboard_images(indicators_path, bar_path, pie_path, ranking_path,
                             watermark_text, output_path="images/all_in_one.png"):
    """
    Combines the 4 generated images (indicators, bars, pie chart, and ranking)
    into a single dashboard and adds the watermark and logo.

    Args:
        indicators_path (str): Path to the indicators image.
        bar_path (str): Path to the bar chart image.
        pie_path (str): Path to the pie chart image.
        ranking_path (str): Path to the ranking image.
        watermark_text (str): Text for the watermark.
        output_path (str): Path where the final image will be saved.
    """
    final_width = DASHBOARD_WIDTH
    final_height = DASHBOARD_HEIGHT

    # Create empty canvas
    dashboard_img = Image.new("RGB", (final_width, final_height), color=DASHBOARD_BACKGROUND_COLOR)

    # Load individual images
    ind_img = Image.open(indicators_path).convert("RGB")
    bar_img = Image.open(bar_path).convert("RGB")
    pie_img = Image.open(pie_path).convert("RGB")
    rank_img = Image.open(ranking_path).convert("RGB")

    # Paste images in their positions
    # Adjust coordinates according to your dimensions
    dashboard_img.paste(ind_img, (0, 0))        # (2400×300)
    dashboard_img.paste(bar_img, (0, 300))      # (2400×800)
    dashboard_img.paste(pie_img, (0, 1100))     # (1200×800)
    dashboard_img.paste(rank_img, (1200, 1100)) # (1200×800)

    # Add watermark in the bottom right corner
    draw = ImageDraw.Draw(dashboard_img)
    text_x = final_width - WATERMARK_POSITION_OFFSET_X
    text_y = final_height - WATERMARK_POSITION_OFFSET_Y

    try:
        font = ImageFont.truetype(WATERMARK_FONT_FAMILY, WATERMARK_FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()

    draw.text((text_x, text_y), watermark_text, fill=WATERMARK_TEXT_COLOR, font=font)

    # Add Gitlights logo in the bottom left corner
    try:
        resp = requests.get(GITLIGHTS_LOGO_URL)
        resp.raise_for_status()
        logo = Image.open(BytesIO(resp.content)).convert("RGBA")
        logo.thumbnail(LOGO_MAX_SIZE, Image.Resampling.LANCZOS)

        # Paste the logo at the fixed position
        dashboard_img.paste(logo, (LOGO_POSITION_X, LOGO_POSITION_Y), logo)
    except Exception as e:
        print(f"Error downloading or pasting the Gitlights logo: {e}")

    # Finally, save the combined image
    dashboard_img.save(output_path)
    print(f"Final image generated: {output_path}")
