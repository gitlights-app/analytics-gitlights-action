# 📊 GitHub Analytics Dashboard in your README

Looking to embed real, auto-updated **GitHub Analytics** directly into your repository?

**GitLights** is a GitHub Action that automatically generates a **visual dashboard with GitHub Insights** based on your repository's activity over the **last 30 days**. The dashboard includes key metrics, activity trends, contribution breakdowns, and contributor rankings — all as a single image you can display in your `README.md` or documentation.

This is the easiest way to make your GitHub repository more transparent, measurable, and engaging — without any manual setup.

> 🧩 **Important:** Before using this action, install the official  
> [GitLights Analytics app from the GitHub Marketplace](https://github.com/marketplace/gitlights-analytics).  
> It grants access to your repository’s analytics data via the GitLights API.

---

## 📈 What's included in the dashboard?

All data reflects activity from the **past month only** (not the full history), giving you a fresh and focused overview.

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

```yaml
name: Generate GitHub Analytics Dashboard

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  generate-dashboard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate GitHub Analytics Dashboard
        uses: gitlights-app/analytics-gitlights-action@v1

      - name: Upload Dashboard Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: gitlights-dashboard
          path: |
            images/all_in_one.png
            dashboard_url.txt
```

---

### 2. Retrieve the image URL (just once)

After the first workflow run:

1. Go to the **Actions** tab in your repo
2. Open the latest run of the dashboard workflow
3. Scroll to the **Artifacts** section
4. Download the file named `dashboard_url.txt`
5. Open the file and copy the image URL

---

### 3. Add the dashboard to your README

Paste this line into your `README.md` (replace the URL with your own):

```markdown
## GitHub Analytics Dashboard (last 30 days)
![GitLights Dashboard](https://api.gitlights.com/api/gitlights-action/dashboard-image/your_image_id)
```

✅ **You only do this once**  
🔁 The URL never changes, even though the image gets updated automatically on each commit  
📊 Your README will always display the latest **GitHub Analytics dashboard** — no manual updates needed

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
