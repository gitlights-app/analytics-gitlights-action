# 📊 GitHub Analytics Dashboard in your README

Looking to embed real, auto-updated **GitHub Analytics** directly into your repository?

**GitLights** is a GitHub Action that automatically generates a **visual dashboard with GitHub Insights** based on your repository's activity. The dashboard includes key metrics, activity trends, contribution breakdowns, and contributor rankings — all as a single image you can display in your `README.md` or documentation.

This is the easiest way to make your GitHub repository more transparent, measurable, and engaging — without any manual setup.

> 🧩 **Important:** Before using this action, install the official  
> [GitLights Analytics app from the GitHub Marketplace](https://github.com/marketplace/gitlights-analytics).  
> It grants access to your repository’s analytics data via the GitLights API.

---

## 📈 What's included in the dashboard?

All data reflects the activity available in your GitLights account for this repository, giving you a fresh and focused overview.

- **4 key GitHub KPIs**:
  - Total commits
  - Total pull requests
  - Total comments
  - Total reviews

- **Time-series chart** showing weekly evolution of those 4 metrics
- **Pie chart** showing investment balance by contribution type (feature, fix, docs, etc.)
- **Contributor ranking table** with a custom **GitHub Insights Score** calculated by GitLights

👉 **The dashboard image looks like this**:

<img src="https://api.gitlights.com/api/gitlights-action/dashboard-image/SZCQyg7XRDo1bz0tfvBB_mXN_ovxk8fZK2cHo8j90YRScDQSprfl2yZwRxZwtIstylddboqKDyJDJzH0H452n5dbJ8jQ-b8PX4If5bqDEZCRsMcDN6HbQdjq" alt="GitLights Analytics Dashboard" width="500" />

This dashboard turns raw GitHub data into **actionable GitHub Insights**, perfect for tracking progress, identifying patterns, and celebrating contributors.

---

## ⚙️ How to set it up

### 1. Add the GitHub Action

First, create a file named `generate-dashboard.yml` in the `.github/workflows` directory of your repository, then add the following code:

```yaml
name: Generate GitLights Dashboard

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  generate-dashboard:
    runs-on: ubuntu-latest
    name: Generate Dashboard
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        
      - name: Generate GitLights dashboard
        id: gitlights
        uses: gitlights-app/analytics-gitlights-action@1.2.1
        with:
          owner: ${{ github.repository_owner }}
          repo: ${{ github.event.repository.name }}
          run_id: ${{ github.run_id }}
        
      - name: Save Dashboard URL to File
        if: success()
        run: |
          mkdir -p ./artifacts
          echo "${{ steps.gitlights.outputs.image_url }}" > ./artifacts/dashboard_url.txt
      
      - name: Upload Dashboard URL
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: gitlights-dashboard-url
          path: ./artifacts/dashboard_url.txt
          retention-days: 5
          if-no-files-found: error
```

---

### 2. Retrieve the image URL (just once)

After the first workflow run:

1. Go to the **Actions** tab in your repo
2. Open the latest run of the dashboard workflow
3. Navigate to the **Summary** tab of the workflow page
4. Look for the **Artifacts** section at the bottom of the summary
5. Download the file named `gitlights-dashboard-url`
6. Extract and open the `dashboard_url.txt` file inside and copy the image URL

---

### 3. Add the dashboard to your README

Paste this line into your `README.md` (replace the URL with your own):

```markdown
## GitHub Analytics Dashboard
<img src="https://api.gitlights.com/api/gitlights-action/dashboard-image/your_image_id" alt="GitLights Analytics Dashboard" width="500" />
```

✅ **You only do this once**  
🔁 The URL never changes, even though the image gets updated automatically on each commit  
📊 Your README will always display the latest **GitHub Analytics dashboard** — no manual updates needed
📏 You can adjust the `width` attribute according to your preference or requirements

---

## ✅ Why use GitLights?

- 📈 **Real GitHub Insights**, visually explained
- 🔄 **Fully automated** updates with every commit
- 👥 **Celebrate contributors** with ranking tables
- 📎 **Easy integration** with documentation and README files
- 🔒 Secure and self-contained: no external dashboards, no tokens exposed

---

<p align="center">
  <i>Powered by <a href="https://github.com/gitlights-app">GitLights</a> — Illuminate your GitHub Analytics</i>
</p>
