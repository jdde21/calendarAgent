import json
from urllib.parse import urlencode
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