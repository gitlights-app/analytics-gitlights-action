# main.py
import json
import os
import sys
import requests
# Removing excessive logging imports

# Import chart creation functions
from charts import (
    create_indicators_figure,
    create_bar_figure,
    create_pie_figure,
    create_ranking_figure
)
# Import function to combine images
from image_utils import combine_dashboard_images

# Import configuration constants
from config import API_URL

def generate_dashboard(owner=None, repo=None, run_id=None, output_path="images/all_in_one.png", actions_runtime_token=None):
    """
    Generates the dashboard image with the given parameters.
    
    Args:
        actions_runtime_token (str): GitHub Actions runtime token for API authentication.
        owner (str): Repository owner (organization or user).
        repo (str): Repository name.
        run_id (str): Optional run ID for the GitHub Actions workflow.
        output_path (str): Path where the final dashboard image will be saved.
        
    Returns:
        bool: True if the dashboard was generated successfully, False otherwise.
    """
    # Ensure the images directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 1) API Call
    url = API_URL
    params = {}
    
    # Add GitHub-related parameters
    if owner and repo:
        params.update({
            'owner': owner,
            'repo': repo,
            'run_id': run_id
        })
        # Include GitHub data silently


    try:
        headers = {}
        if actions_runtime_token:
            headers['Authorization'] = f"{actions_runtime_token}"
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False
    except requests.exceptions.JSONDecodeError:
        print("Error: Response is not valid JSON")
        return False

    try:
        # 2) Extract necessary information from JSON
        indicators_cfg = data["indicators"]
        bar_cfg        = data["bar_chart"]
        pie_cfg        = data["pie_chart"]
        rank_cfg       = data["ranking"]
        watermark_text = data["watermark_text"]

        # 3) Create figures with Plotly
        fig_indicators = create_indicators_figure(
            titles=indicators_cfg["titles"],
            values=indicators_cfg["values"],
            deltas=indicators_cfg["deltas"]
        )
        fig_bars = create_bar_figure(bar_cfg)
        fig_pie = create_pie_figure(pie_cfg)
        fig_rank = create_ranking_figure(rank_cfg)

        # 4) Export each figure to PNG
        indicators_path = "images/indicators.png"
        bar_path = "images/bars.png"
        pie_path = "images/pie.png"
        ranking_path = "images/ranking.png"
        
        fig_indicators.write_image(indicators_path)
        fig_bars.write_image(bar_path)
        fig_pie.write_image(pie_path)
        fig_rank.write_image(ranking_path)

        print(f"Individual images generated: {indicators_path}, {bar_path}, {pie_path}, {ranking_path}")

        # 5) Combine images into a single dashboard
        combine_dashboard_images(
            indicators_path=indicators_path,
            bar_path=bar_path,
            pie_path=pie_path,
            ranking_path=ranking_path,
            watermark_text=watermark_text,
            output_path=output_path
        )
        
        print(f"Final dashboard image generated: {output_path}")
        
        # Send the dashboard image to the backend for storage
        try:
            backend_url = os.environ.get('BACKEND_URL', 'https://api.gitlights.com/api/gitlights-action/upload-dashboard-image/')
            
            # Open the image file in binary mode
            with open(output_path, 'rb') as img_file:
                # Prepare the payload
                files = {'image': (os.path.basename(output_path), img_file, 'image/png')}
                payload = {
                    'owner': owner,
                    'repo': repo,
                    'run_id': run_id
                }
                
                # Add auth if available
                headers = {}
                if actions_runtime_token:
                    headers['Authorization'] = f"{actions_runtime_token}"
                
                # Send the request
                response = requests.post(backend_url, files=files, data=payload, headers=headers)
                response.raise_for_status()
                
                # Get the image URL from the response
                image_url = response.json().get('image_url')
                if image_url:
                    # Print that upload was successful without showing the full URL (to avoid masking)
                    print(f"Dashboard image uploaded successfully")
                    
                    # Simply output the image URL
                    # Use GitHub Actions output mechanism
                    github_output = os.environ.get('GITHUB_OUTPUT')
                    if github_output:
                        with open(github_output, 'a') as f:
                            f.write(f"image_url={image_url}\n")
                    else:
                        # Fall back to old syntax for backward compatibility
                        print(f"::set-output name=image_url::{image_url}")

                    print(f"Dashboard image uploaded successfully")

                    
                    # Store the URL for local reference
                    os.environ['DASHBOARD_IMAGE_URL'] = image_url
                else:
                    print("Dashboard image uploaded to backend but URL not returned")
                    
        except Exception as e:
            print(f"Error uploading dashboard to backend: {e}")
            # Don't fail the whole process if just the upload fails
            # The image is still generated locally
        
        return True
    except Exception as e:
        print(f"Error generating dashboard: {e}")
        return False


# Removing HTTP debugging function to reduce verbosity

def main():
    """
    Main function to run when the script is executed directly.
    Gets parameters from environment variables if available.
    """
    # Basic logging for runtime parameters
    print("Starting GitLights dashboard generation...")
    
    # GitHub Actions passes input variables with INPUT_ prefix, prioritize those over regular env vars
    owner = os.environ.get('INPUT_OWNER', os.environ.get('OWNER', None))
    repo = os.environ.get('INPUT_REPO', os.environ.get('REPO', None))
    run_id = os.environ.get('INPUT_RUN_ID', os.environ.get('RUN_ID', None))
    output_path = os.environ.get('INPUT_OUTPUT_PATH', os.environ.get('OUTPUT_PATH', 'images/all_in_one.png'))
    
    # These are standard GitHub Actions environment variables, not inputs
    actions_runtime_token = os.environ.get('ACTIONS_RUNTIME_TOKEN', None)
    
    # Simple confirmation of execution

    success = generate_dashboard(owner=owner, repo=repo, run_id=run_id, output_path=output_path, actions_runtime_token=actions_runtime_token)
    
    # Exit with appropriate status code
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()