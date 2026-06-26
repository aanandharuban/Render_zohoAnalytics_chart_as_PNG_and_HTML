# 📊 Zoho Analytics Chart Viewer

> A **FastMCP** server that securely fetches and renders **live Zoho Analytics charts** inside a modern **Prefab UI**, preserving full chart interactivity including hover tooltips, drill-downs, filters, and dynamic rendering.

---

## ✨ Features

- 🔐 Secure OAuth 2.0 authentication with Zoho Analytics
- 📊 Fetch live charts directly from Zoho Analytics
- 🎨 Modern responsive UI built using Prefab Components
- ⚡ Preserves complete chart interactivity
- 🖱️ Hover tooltips, drill-downs and filters remain functional
- 🖼️ Secure sandboxed iframe rendering
- 📥 Download rendered charts as HTML
- 🚀 FastMCP Apps integration
- 🔒 No credentials exposed to the frontend

---

# Preview

```
┌──────────────────────────────────────────────┐
│                Prefab UI                     │
│                                              │
│  Workspace ID  [_________________________]   │
│                                              │
│  View ID       [_________________________]   │
│                                              │
│           [ Show Chart ]                     │
└──────────────────────────────────────────────┘

                 │
                 ▼

        FastMCP Tool: fetch_chart()

                 │
                 ▼

      Zoho Analytics Export API

                 │
                 ▼

      Interactive HTML Chart

                 │
                 ▼

      Sandboxed iframe Renderer
```

---

# Architecture

```
User
 │
 ▼
Prefab UI
 │
 ▼
FastMCP Tool
(fetch_chart)
 │
 ▼
OAuth Authentication
 │
 ▼
Zoho Analytics API
 │
 ▼
HTML Chart Response
 │
 ▼
Sandboxed iframe
 │
 ▼
Interactive Chart
```

---

# Project Structure

```
zoho-chart-viewer/
│
├── server.py              # FastMCP server
├── .env                   # Zoho credentials
├── .venv/                 # Python virtual environment
└── README.md
```

---

# Prerequisites

Before starting, ensure you have:

- Python 3.10+
- Zoho Analytics account
- Zoho OAuth Client
- Refresh Token
- Organization ID
- Workspace ID
- View (Report) ID

---

# Installation

## 1. Clone or create the project

```bash
mkdir zoho-chart-viewer
cd zoho-chart-viewer
```

---

## 2. Create a virtual environment

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install "fastmcp[apps]>=2.14.1" httpx python-dotenv
```

---

# Configuration

Create a `.env` file in the project root.

```env
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORG_ID=your_org_id

ANALYTICS_URL=https://analyticsapi.zoho.com
ACCESS_URL=https://accounts.zoho.com/oauth/v2/token
```

---

# Getting Zoho Credentials

## Client ID & Client Secret

1. Visit the Zoho API Console.
2. Create a new OAuth Client.
3. Copy the generated:

- Client ID
- Client Secret

---

## Refresh Token

Generate a refresh token with the scope:

```
ZohoAnalytics.data.READ
```

Store the generated token inside `.env`.

---

## Organization ID

Inside Zoho Analytics:

```
Profile
    ↓
Organization Settings
        ↓
Organization ID
```

---

# Running the Application

Start the FastMCP development server:

```bash
fastmcp dev apps server.py
```

The server typically starts at:

```
http://127.0.0.1:8080
```

Open the URL in your browser.

---

# Using the Application

Enter:

### Workspace ID

Example:

```
498732000000002017
```

### View ID

Example:

```
498732000000051003
```

Click

```
Show Chart
```

The application will fetch the chart directly from Zoho Analytics and display it inside a sandboxed iframe while preserving full interactivity.

---

# How It Works

## Step 1

User enters

- Workspace ID
- View ID

↓

## Step 2

FastMCP calls

```
fetch_chart()
```

↓

## Step 3

OAuth Refresh Token

↓

Access Token

↓

## Step 4

Zoho Analytics Export API

↓

Returns interactive HTML

↓

## Step 5

Prefab UI embeds the HTML inside a sandboxed iframe.

↓

## Step 6

User interacts with the chart exactly as inside Zoho Analytics.

---

# API Flow

```
User
 │
 ▼
Prefab Form
 │
 ▼
fetch_chart()
 │
 ▼
Get Access Token
 │
 ▼
Zoho Analytics Export API
 │
 ▼
HTML Response
 │
 ▼
Iframe Renderer
 │
 ▼
Interactive Chart
```

---

# FastMCP Tool

## fetch_chart

Fetches a live Zoho Analytics chart as interactive HTML.

### Parameters

| Parameter | Type | Description |
|------------|------|-------------|
| workspace_id | string | Zoho Analytics Workspace ID |
| view_id | string | Zoho Analytics Report/View ID |

---

### Returns

```json
{
  "status": "success",
  "html": "<html>...</html>"
}
```

---

# Finding IDs

## Workspace ID

Navigate to your workspace.

Example URL

```
https://analytics.zoho.com/workspace/498732000000002017/
```

Workspace ID:

```
498732000000002017
```

---

## View ID

Open the report.

Example URL

```
https://analytics.zoho.com/.../view/498732000000051003
```

View ID:

```
498732000000051003
```

---

# Environment Variables

| Variable | Required | Description |
|------------|-----------|------------|
| ZOHO_CLIENT_ID | ✅ | OAuth Client ID |
| ZOHO_CLIENT_SECRET | ✅ | OAuth Client Secret |
| ZOHO_REFRESH_TOKEN | ✅ | OAuth Refresh Token |
| ZOHO_ORG_ID | ✅ | Organization ID |
| ANALYTICS_URL | ✅ | Zoho Analytics API URL |
| ACCESS_URL | ✅ | OAuth Token URL |

---

# Troubleshooting

## 401 Unauthorized

Possible causes:

- Invalid Client ID
- Invalid Client Secret
- Expired Refresh Token
- Incorrect OAuth Scope

---

## 400 Bad Request

Verify:

- Workspace ID
- View ID
- User permissions
- Organization ID

---

## Chart Does Not Load

Check:

- Internet connection
- Browser console
- iframe restrictions
- Workspace permissions
- Report accessibility

---

## Failed to Fetch Chart

Possible reasons:

- Zoho API unavailable
- OAuth token expired
- Network timeout
- Rate limiting

---

# Security

This project follows several security best practices:

- OAuth credentials never reach the frontend
- Tokens remain on the server
- HTML is rendered inside a sandboxed iframe
- Sensitive values are stored in `.env`
- HTTPS is recommended for production deployments
- Never commit `.env` to version control

---

# Dependencies

| Package | Purpose |
|----------|----------|
| fastmcp[apps] | FastMCP server framework |
| httpx | Async HTTP client |
| python-dotenv | Environment variable management |
| Prefab UI | FastMCP frontend components |

---

# Development

Run in development mode:

```bash
fastmcp dev apps server.py
```

---

# Production

For production deployments:

```bash
fastmcp run server.py
```

Deploy behind a reverse proxy such as Nginx or Caddy with HTTPS enabled.

---

# Future Improvements

- 📈 Dashboard support
- 📊 Multiple chart rendering
- 📁 Export to PNG, PDF, and SVG
- 🔄 Auto-refresh charts
- 🌙 Dark mode
- 📱 Mobile responsive layout
- 🔍 Global search for reports
- 📤 Shareable chart links
- 📂 Workspace browser
- 📋 Report metadata viewer

---

# License

This project is released under the **MIT License**.

Feel free to use, modify, and distribute it according to the license terms.

---

# Acknowledgements

Built using:

- FastMCP
- Prefab UI
- Zoho Analytics REST API
- Python
- HTTPX

---

# Version History

## v1.0.0

- Initial release
- FastMCP Apps integration
- OAuth 2.0 authentication
- Interactive HTML chart rendering
- Prefab UI implementation
- Sandboxed iframe embedding
- Live Zoho Analytics integration

---

## ⭐ If this project helps you, consider giving it a star!
