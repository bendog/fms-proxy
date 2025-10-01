import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import StreamingResponse

OUTLOOK_PATH_MUST_CONTAIN: str = os.environ.get("OUTLOOK_PATH_MUST_CONTAIN", "owa/calendar/")


app = FastAPI(title="FMS Proxy", description="FastAPI service with a default landing page.")


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    # Simple default landing page
    return """
        <!DOCTYPE html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\" />
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
            <title>FMS Proxy</title>
            <style>
                body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
                       margin: 0; padding: 0; background: #0f172a; color: #e2e8f0; }
                .container { max-width: 860px; margin: 0 auto; padding: 48px 24px; }
                h1 { font-size: 28px; margin: 0 0 8px; }
                p { color: #cbd5e1; line-height: 1.6; }
                code { background: #111827; padding: 2px 6px; border-radius: 4px; }
                a { color: #93c5fd; }
                .card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 20px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class=\"container\">
                <h1>FMS Proxy</h1>
                <p>Service is running. Use this server to proxy Outlook ICS requests.</p>
            </div>
        </body>
        </html>
        """


OUTLOOK_HOST: str = "outlook.office365.com"
outlook_client = httpx.AsyncClient(
    base_url=f"https://{OUTLOOK_HOST}/",
    timeout=httpx.Timeout(30.0),
)
OVERRIDE_HEADERS: dict[str, str] = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/140.0.0.0",
    "host": OUTLOOK_HOST,
}

HeadersRaw = list[tuple[bytes, bytes]]


def override_headers(headers: HeadersRaw) -> HeadersRaw:
    """Go through the headers and override any headers which are matched in OVERRIDE_HEADERS"""
    new_headers: HeadersRaw = []
    for key_bytes, value_bytes in headers:
        key_str = key_bytes.decode("utf-8").lower()
        if key_str in OVERRIDE_HEADERS:
            new_headers.append((key_bytes, OVERRIDE_HEADERS[key_str].encode("utf-8")))
        else:
            new_headers.append((key_bytes, value_bytes))
    return new_headers


async def outlook_reverse_proxy(request: Request):
    """Reverse proxy for Outlook ICS requests"""
    outlook_path: str = request.path_params["path"]
    if OUTLOOK_PATH_MUST_CONTAIN not in outlook_path:
        raise HTTPException(status_code=400, detail="This path is not permitted.")

    url = httpx.URL(path=outlook_path, query=request.url.query.encode("utf-8"))
    rp_req = outlook_client.build_request(
        request.method,
        url,
        headers=override_headers(request.headers.raw),
        content=await request.body(),
    )
    rp_resp = await outlook_client.send(rp_req, stream=True)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )


app.add_route("/outlook/{path:path}", outlook_reverse_proxy, ["GET"])
