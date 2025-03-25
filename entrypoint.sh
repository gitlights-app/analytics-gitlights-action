#!/bin/sh -l

# Basic debug information
echo "Running GitLights dashboard generation..."

# Run the dashboard generation script
python /app/main.py
EXIT_CODE=$?

# If the script ran successfully, output paths
if [ $EXIT_CODE -eq 0 ]; then
  # Get OUTPUT_PATH from environment variable, use default if not set
  DASHBOARD_PATH=${INPUT_OUTPUT_PATH:-images/all_in_one.png}
  
  # Set the output using GitHub's newer output mechanism if available
  if [ -n "$GITHUB_OUTPUT" ]; then
    echo "dashboard_image=${DASHBOARD_PATH}" >> $GITHUB_OUTPUT
  else
    # Fall back to old syntax for backward compatibility
    echo "::set-output name=dashboard_image::${DASHBOARD_PATH}"
  fi
  
  # Note: image_url will already be set directly in the Python script
  # This is just to document that this output exists
fi

exit $EXIT_CODE
