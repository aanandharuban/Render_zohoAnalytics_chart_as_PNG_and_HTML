
import base64
import json
import os
from urllib.parse import quote
import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.apps import AppConfig, ResourceCSP

load_dotenv()

CLIENT_ID     = os.getenv("ZOHO_CLIENT_ID",     "")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "")
ORG_ID        = os.getenv("ZOHO_ORG_ID",        "")

TOKEN_URL = "https://accounts.zoho.in/oauth/v2/token"
EXPORT_URL = (
    "https://analyticsapi.zoho.in/restapi/v2"
    "/workspaces/{workspace_id}/views/{view_id}/data"
)

mcp = FastMCP("Zoho Analytics Chart Viewer")

VIEW_URI = "ui://zoho-chart/view.html"



def _get_access_token() -> str:
    resp = httpx.post(
        TOKEN_URL,
        data={
            "grant_type":    "refresh_token",
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"Token error: {data}")
    return data["access_token"]


def _export_raw(workspace_id: str, view_id: str,
                access_token: str, fmt: str,
                extra: dict | None = None) -> bytes:
    cfg    = {"responseFormat": fmt, **(extra or {})}
    config = json.dumps(cfg, separators=(",", ":"))
    url    = EXPORT_URL.format(workspace_id=workspace_id, view_id=view_id)
    resp   = httpx.get(
        f"{url}?CONFIG={quote(config)}",
        headers={
            "Authorization":     f"Zoho-oauthtoken {access_token}",
            "ZANALYTICS-ORGID": ORG_ID,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content


@mcp.tool(app=AppConfig(resource_uri=VIEW_URI))
def fetch_chart(workspace_id: str, view_id: str) -> dict:
    """
    Fetch Zoho Analytics chart as a PNG image and return as base64.
    The UI will render it with interactive features.
    """
    token = _get_access_token()
    
    png_bytes = _export_raw(
        workspace_id, 
        view_id, 
        token, 
        "image", 
        {"imageFormat": "png"}
    )
    
    b64 = base64.b64encode(png_bytes).decode("ascii")
    
    return {
        "png_base64":   b64,
        "view_id":      view_id,
        "workspace_id": workspace_id,
    }


@mcp.resource(
    VIEW_URI,
    app=AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com"])),
)
def chart_view() -> str:
    """
    Custom HTML UI for the Zoho Analytics chart viewer.
    Receives tool result via app.ontoolresult and displays the chart.
    """
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Zoho Analytics Chart Viewer</title>
<style>
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: #000000;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #e2e8f0;
    height: 100%;
  }
  .container {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 20px;
    background: #1a1a1a;
    border-bottom: 1px solid #333;
    flex-shrink: 0;
  }
  .toolbar .title {
    font-size: 16px;
    font-weight: 600;
    color: #e2e8f0;
  }
  .toolbar .actions {
    display: flex;
    gap: 8px;
  }
  .toolbar button {
    padding: 8px 16px;
    font-size: 13px;
    background: #333;
    color: #e2e8f0;
    border: 1px solid #444;
    border-radius: 6px;
    cursor: pointer;
    transition: background .15s ease;
  }
  .toolbar button:hover {
    background: #444;
  }
  .toolbar button.primary {
    background: #3b82f6;
    border-color: #3b82f6;
  }
  .toolbar button.primary:hover {
    background: #2563eb;
  }
  .chart-wrap {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 20px;
  }
  .stage {
    position: relative;
    max-width: 100%;
    max-height: 100%;
    transition: transform .25s ease;
    cursor: zoom-in;
  }
  .stage.zoomed {
    transform: scale(1.8);
    cursor: zoom-out;
  }
  .stage img {
    display: block;
    max-width: 100%;
    max-height: 100%;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,.8);
    background: #fff;
  }
  .hint {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 12px;
    color: #94a3b8;
    background: rgba(0,0,0,.7);
    padding: 6px 12px;
    border-radius: 6px;
  }
  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #94a3b8;
    font-size: 14px;
  }
  .error {
    display: none;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #fecaca;
    background: #7f1d1d;
    padding: 20px;
    text-align: center;
  }
</style>
</head>
<body>
  <div class="container">
    <div class="toolbar">
      <div class="title" id="chartTitle">Zoho Chart</div>
      <div class="actions">
        <button id="zoomBtn">Zoom</button>
        <button id="dlPngBtn" class="primary">Download PNG</button>
        <button id="dlHtmlBtn" class="primary">Download HTML</button>
      </div>
    </div>
    <div class="chart-wrap" id="chartWrap">
      <div class="loading" id="loading">Loading chart...</div>
      <div class="error" id="error"></div>
      <div class="stage" id="stage" style="display:none;">
        <img id="chartImg" alt="Zoho chart" />
      </div>
      <div class="hint" id="hint" style="display:none;">Click image to zoom</div>
    </div>
  </div>

<script type="module">
  import { App } from "https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps";

  const app = new App({ name: "Zoho Chart Viewer", version: "1.0.0" });

  // DOM elements
  const chartTitle = document.getElementById('chartTitle');
  const chartImg = document.getElementById('chartImg');
  const stage = document.getElementById('stage');
  const hint = document.getElementById('hint');
  const zoomBtn = document.getElementById('zoomBtn');
  const dlPngBtn = document.getElementById('dlPngBtn');
  const dlHtmlBtn = document.getElementById('dlHtmlBtn');
  const loading = document.getElementById('loading');
  const error = document.getElementById('error');

  let currentData = null;

  // Receive tool result from host
  app.ontoolresult = ({ content }) => {
    try {
      const text = content?.find(c => c.type === 'text');
      if (!text) throw new Error('No data returned from server');
      
      const data = JSON.parse(text.text);
      currentData = data;
      
      // Display the chart
      const dataUri = `data:image/png;base64,${data.png_base64}`;
      chartImg.src = dataUri;
      chartTitle.textContent = `Zoho Chart - ${data.view_id}`;
      
      // Show chart, hide loading
      loading.style.display = 'none';
      stage.style.display = 'block';
      hint.style.display = 'block';
      
    } catch (err) {
      loading.style.display = 'none';
      error.style.display = 'flex';
      error.textContent = 'Failed to load chart: ' + err.message;
    }
  };

  // Zoom toggle
  stage.addEventListener('click', () => stage.classList.toggle('zoomed'));
  zoomBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    stage.classList.toggle('zoomed');
  });

  // Download PNG
  dlPngBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (!currentData) return;
    
    const a = document.createElement('a');
    a.href = chartImg.src;
    a.download = `zoho-chart-${currentData.view_id}.png`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  });

  // Download HTML
  dlHtmlBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (!currentData) return;
    
    // Create standalone HTML with embedded PNG
    const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Zoho Chart - ${currentData.view_id}</title>
<style>
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: #000000;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #e2e8f0;
    height: 100%;
  }
  .wrap {
    width: 100%;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .stage {
    position: relative;
    max-width: 100%;
    max-height: 100%;
    transition: transform .25s ease;
    cursor: zoom-in;
  }
  .stage.zoomed {
    transform: scale(1.8);
    cursor: zoom-out;
  }
  .stage img {
    display: block;
    max-width: 100%;
    max-height: 100%;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,.8);
    background: #fff;
  }
  .hint {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 12px;
    color: #94a3b8;
    background: rgba(0,0,0,.7);
    padding: 6px 12px;
    border-radius: 6px;
  }
</style>
</head>
<body>
  <div class="wrap">
    <div class="stage" onclick="this.classList.toggle('zoomed')">
      <img src="${chartImg.src}" alt="Zoho chart ${currentData.view_id}" />
    </div>
    <div class="hint">Click image to zoom</div>
  </div>
</body>
</html>`;
    
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `zoho-chart-${currentData.view_id}.html`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });

  // Connect to host
  await app.connect();
</script>
</body>
</html>"""


if __name__ == "__main__":
    mcp.run()