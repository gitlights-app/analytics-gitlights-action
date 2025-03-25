# Analytics Dashboard For Your README

This GitHub Action generates an insightful, visual analytics dashboard for your repositories. It creates comprehensive dashboards with indicators, bar charts, pie charts, and ranking tables powered by the GitLights API to transform raw GitHub data into actionable insights.

## 🎯 Purpose and Benefits

The GitLights Analytics Dashboard Generator is designed to:

- **Visualize GitHub repository metrics** in an easy-to-interpret dashboard
- **Track repository health and activity** through time-series analytics
- **Identify trends and patterns** in your development workflow
- **Showcase contributor engagement** with clear, shareable visuals
- **Improve team visibility** with automated, scheduled insights

## ✨ Features

- Generates rich, comprehensive **GitHub analytics dashboards** with multiple visualizations
- Displays key repository metrics using intuitive **GitHub insights** charts
- Creates dashboards on schedule or on-demand for continuous **GitHub data visualization**
- Customizable output paths for easy integration with documentation or reporting
- Lightweight implementation with minimal configuration required

## Usage

### Basic Usage

```yaml
name: Generate GitHub Analytics Dashboard

on:
  push:
    branches:
      - main  # Update on every commit to main branch
  workflow_dispatch:  # Allow manual triggering

jobs:
  generate-dashboard:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        
      - name: Generate GitHub Analytics Dashboard
        id: gitlights
        uses: gitlights-app/analytics-gitlights-action@v1
        # No inputs required! The action works without any configuration
      
      - name: Upload Dashboard Image
        uses: actions/upload-artifact@v3
        with:
          name: dashboard-image
          path: images/all_in_one.png
```

### Note on Configuration

This action requires **no inputs** to function properly. All necessary parameters are automatically inferred from the context of your GitHub repository. The action can be used with minimal configuration as shown in the example above.

For specialized use cases, the action does accept certain inputs, but these are entirely optional and rarely needed.

### Outputs

| Output | Description |
|--------|-------------|
| `dashboard_image` | Path to the generated dashboard image |

### Using the Dashboard in Your README

The action generates an image at a fixed path (`images/all_in_one.png` by default). To display this dashboard in your README, simply add the following Markdown code to your README.md file:

```markdown
## Repository Analytics Dashboard

![GitLights Analytics Dashboard](./images/all_in_one.png)
```

When you set up the action to run on every commit to your main branch, the dashboard image will be automatically updated each time, with no manual intervention required. Since the image is always generated with the same filename and path, your README will always display the most current analytics without needing any changes to the README itself.

## Example Workflows

### Example 1: Generate and Save Dashboard to Repository

This workflow generates a dashboard on every commit to the main branch and commits the updated image back to your repository:

```yaml
name: GitHub Analytics Dashboard Update

on:
  push:
    branches:
      - main  # Update on every commit to main branch
  workflow_dispatch:  # Allow manual triggering

jobs:
  update-dashboard:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Generate GitHub Analytics Dashboard
        id: gitlights
        uses: gitlights-app/analytics-gitlights-action@v1
        with:
          owner: ${{ github.repository_owner }}
          repo: ${{ github.event.repository.name }}
          run_id: ${{ github.run_id }}
        
      - name: Access Dashboard URL
        run: |
          # Save URL to GitHub's environment file for use in subsequent steps
          echo "DASHBOARD_URL=${{ steps.gitlights.outputs.image_url }}" >> $GITHUB_ENV
          
          # Now the URL is available as ${{ env.DASHBOARD_URL }} in all later steps
        
      - name: Commit and Push
        run: |
          git config --global user.name 'GitHub Action'
          git config --global user.email 'action@github.com'
          git add images/all_in_one.png
          git commit -m "Update GitHub analytics dashboard [skip ci]" || echo "No changes to commit"
          git push
```

### Example 2: Generate Dashboard for Project Documentation

Use this workflow to create analytics dashboards for your project's documentation site:

```yaml
name: Update Documentation Dashboard

on:
  push:
    branches:
      - main  # Update when main is updated
  workflow_dispatch:

jobs:
  update-docs-dashboard:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Generate GitHub Analytics Dashboard
        id: gitlights
        uses: gitlights-app/analytics-gitlights-action@v1
        with:
          output_path: 'docs/assets/images/github-analytics-dashboard.png'
        
      - name: Use Dashboard URL
        run: |
          echo "Dashboard generated at: ${{ steps.gitlights.outputs.dashboard_image }}"
          # Save URL to GitHub's environment file for later steps
          echo "DASHBOARD_URL=${{ steps.gitlights.outputs.image_url }}" >> $GITHUB_ENV
          
          # The URL can now be accessed as ${{ env.DASHBOARD_URL }} in subsequent steps
      
      - name: Update documentation
        uses: EndBug/add-and-commit@v9
        with:
          add: 'docs/assets/images/github-analytics-dashboard.png'
          message: 'docs: update GitHub analytics dashboard'
          push: true
```

### Example 3: Multi-Repository Analytics Dashboard

Generate dashboards for multiple repositories in your organization with automatic updates:

```yaml
name: Organization GitHub Analytics

on:
  push:
    branches:
      - main  # Update on every commit to main branch
  workflow_dispatch:

jobs:
  generate-analytics:
    strategy:
      matrix:
        repo: ['main-app', 'backend-api', 'frontend-client']
    
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Generate GitHub Analytics Dashboard
        id: gitlights
        uses: gitlights-app/analytics-gitlights-action@v1
        with:
          owner: 'your-organization'
          repo: ${{ matrix.repo }}
          output_path: 'reports/${{ matrix.repo }}-analytics.png'
          
      - name: Process Dashboard URL
        run: |
          echo "Generated ${{ matrix.repo }} dashboard at: ${{ steps.gitlights.outputs.dashboard_image }}"
          # For multiple repos, we use unique environment variable names
          echo "DASHBOARD_URL_${{ matrix.repo }}=${{ steps.gitlights.outputs.image_url }}" >> $GITHUB_ENV
          
          # This creates variables like ${{ env.DASHBOARD_URL_main-app }} for each repo
      
      - name: Archive reports
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.repo }}-analytics
          path: reports/${{ matrix.repo }}-analytics.png
```

## Configuration Options

### Inputs

| Parameter | Description | Required | Default |
|-----------|-------------|----------|--------|
| `owner` | Repository owner (organization or user) | No | Extracted from GitHub context |
| `repo` | Repository name | No | Extracted from GitHub context |
| `run_id` | GitHub Actions workflow run ID | No | Current workflow run ID |
| `output_path` | Path where the final dashboard image will be saved | No | `images/all_in_one.png` |

### Outputs

| Output | Description |
|--------|-------------|
| `dashboard_image` | Path to the generated dashboard image |
| `image_url` | URL to the uploaded dashboard image (requires authentication) |
| `redirect_html` | Path to an HTML file that redirects to the dashboard image URL |

#### Using the HTML Redirect File

For security reasons, GitHub automatically masks sensitive information in URLs (including authentication tokens). To easily access the dashboard image URL without dealing with masked tokens, the action generates an HTML redirect file. Here's how to use it:

1. **Upload the HTML file as an artifact**:
   ```yaml
   - name: Upload Dashboard Files
     uses: actions/upload-artifact@v3
     with:
       name: gitlights-dashboard
       path: |
         ${{ steps.gitlights.outputs.dashboard_image }}
         ${{ steps.gitlights.outputs.redirect_html }}
   ```

2. **Download and open the HTML file**:
   After the workflow completes, download the artifact containing both the dashboard image and the HTML redirect file. When you open the HTML file in a browser, it will automatically redirect you to the dashboard URL with the proper authentication token.

This approach simplifies the user experience while maintaining security by keeping the authentication token within the workflow context.

## Dashboard Components

The generated GitHub analytics dashboard includes these key visualizations:

1. **Key Performance Indicators** - Essential metrics including:
   - Total commits, pull requests, and issues
   - Active contributors and participation rates
   - Repository health scores
   - Recent activity trends

2. **Temporal Activity Analysis** - Bar charts visualizing:
   - Monthly/weekly development activity
   - Commit frequency patterns
   - Pull request and issue resolution rates
   - Release cadence (when applicable)

3. **Contribution Distribution** - Pie charts displaying:
   - Code contribution distribution across team members
   - Types of contributions (features, fixes, documentation)
   - Issue category breakdown
   - Pull request review distribution

4. **Contributor Rankings** - Tables highlighting:
   - Most active contributors with detailed metrics
   - Top reviewers and their impact
   - Issue resolution champions
   - Documentation contributors

These visualizations transform raw GitHub data into meaningful GitHub insights that help teams identify patterns, recognize contributions, and make data-driven decisions about their development process.

## Chart Details

### 📊 Bar Charts
The bar charts use a consistent color scheme to make it easy to track metrics over time. The charts automatically adjust their scale based on your repository's activity level, ensuring that patterns remain visible regardless of whether your project has 10 or 10,000 contributions.

### 🍩 Pie Charts
Interactive pie charts break down repository activity by category, showing proportional distribution with clear labels. These charts use a carefully selected color palette that maintains accessibility for most forms of color vision deficiency.

### 📈 Trend Indicators
The dashboard includes intuitive up/down arrows with percentage changes to highlight whether metrics are improving or declining compared to previous periods.

### 📋 Ranking Tables
Contributor tables include profile images, names, and key contribution metrics, making it easy to recognize your most active team members at a glance.

## Why Use GitLights Analytics Dashboards?

- **Zero Maintenance** - Images update automatically on every commit with no manual intervention
- **Evidence-Based Development** - Make decisions backed by visual GitHub analytics
- **Stakeholder Communication** - Share meaningful GitHub insights with non-technical stakeholders
- **Team Recognition** - Highlight and celebrate contributor achievements
- **Process Improvement** - Identify bottlenecks and optimize your development workflow
- **Documentation Enhancement** - Enrich your project documentation with always current GitHub dashboards

## Local Development

To run the GitHub analytics dashboard generator locally:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables:
   ```
   export GITHUB_TOKEN=your_github_token
   export OWNER=repository_owner
   export REPO=repository_name
   export OUTPUT_PATH=output/path.png
   ```
4. Run the script: `python main.py`

## Testing

The project includes a comprehensive test suite with 21 tests covering all components. To run the tests:

```bash
docker run --entrypoint="" -v $(pwd):/app gitlights-action python -m pytest
```

## Related Projects

- [GitLights API](https://github.com/gitlights-app/gitlights-api) - The API powering these analytics dashboards
- [GitHub Metrics Collector](https://github.com/gitlights-app/metrics-collector) - Tool for collecting additional GitHub metrics

## License

MIT

---

<p align="center">
  <i>Powered by <a href="https://github.com/gitlights-app">GitLights</a> - Illuminating GitHub Analytics Dashboards</i>
</p>

## Displaying the Dashboard in Your README

After running the action, you'll need to download the text file from the workflow artifacts. This file contains the URL to your dashboard image.

Follow these steps:

1. Go to your GitHub repository
2. Navigate to the Actions tab
3. Select the workflow run that generated the dashboard
4. Scroll down to the Artifacts section
5. Download the artifact that contains the image URL
6. Open the text file and copy the URL
7. Add the following line to your README.md (replace the URL with your own):

```markdown
![GitLights Dashboard](https://api.gitlights.com/api/gitlights-action/dashboard-image/your_unique_image_id)
```

Example:

```markdown
![GitLights Dashboard](https://api.gitlights.com/api/gitlights-action/dashboard-image/zNv1Q_HPzrg67DIPphTnyveSoGJKXl49TzYQOpaFTc5f5f_mTzCdp8Tk5dEsDQ3psJ1xCtKv9iKb58Gc7u17WoihXB__gyjmod7N3bDf410gwp10qKeeBJ1V)
```

**Note:** You only need to do this process once. The dashboard image will be automatically updated with each new commit while maintaining the same URL.

