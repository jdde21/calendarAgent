import json
from workers import env
from utils import get_access_token, gcall, _extract_body
from urllib.parse import urlencode

BASE = "https://gmail.googleapis.com/gmail/v1/users/me"

async def email() -> dict | None:
    token_info = json.loads(env.TOKEN_JSON)
    access_token = await get_access_token(token_info)

    # 1. Newest message ID in the inbox
    params = urlencode({"labelIds": "INBOX", "maxResults": 1})
    listing = await gcall(f"{BASE}/messages?{params}", access_token)
    messages = listing.get("messages", [])
    print(listing)
    if not messages:
        return None

    # 2. Fetch the full message
    msg = await gcall(
        f"{BASE}/messages/{messages[0]['id']}?format=full", access_token
    )

    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

    return {
        "from": headers.get("From"),
        "subject": headers.get("Subject"),
        "date": headers.get("Date"),
        "snippet": msg.get("snippet"),
        "body": _extract_body(msg["payload"]),
    }