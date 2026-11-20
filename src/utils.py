import json
from urllib.parse import urlencode
import base64
from js import fetch, Object
from pyodide.ffi import to_js

async def get_access_token(token_info: dict) -> str:
    resp = await fetch(
        token_info.get("token_uri", "https://oauth2.googleapis.com/token"),
        _opts(
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=urlencode({
                "client_id": token_info["client_id"],
                "client_secret": token_info["client_secret"],
                "refresh_token": token_info["refresh_token"],
                "grant_type": "refresh_token",
            }),
        ),
    )
    data = json.loads(await resp.text())
    if "access_token" not in data:
        raise RuntimeError(f"Token refresh failed: {data}")
    return data["access_token"]

def _opts(**kw):
    # convert a Python dict into a plain JS object for fetch
    return to_js(kw, dict_converter=Object.fromEntries)

async def gcall(url: str, access_token: str) -> dict:
    resp = await fetch(url, _opts(headers={"Authorization": f"Bearer {access_token}"}))
    text = await resp.text()
    return json.loads(text)
  
async def list_submissions(course_id: str, access_token: str, BASE: str) -> list:
    params = urlencode({"userId": "me", "pageSize": 100})
    url = f"{BASE}/courses/{course_id}/courseWork/-/studentSubmissions?{params}"
    data = await gcall(url, access_token)
    return data.get("studentSubmissions", [])

def _decode_b64url(data: str) -> str:
    # Gmail omits padding, so add it back before decoding
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")


def _extract_body(payload: dict) -> str:
    # Find the text/plain body in simple or multipart messages
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return _decode_b64url(payload["body"]["data"])
    for part in payload.get("parts", []):
        body = _extract_body(part)
        if body:
            return body
    return ""