## Getting Started

This guide helps you set up and run the project with both Google Calendar and Gmail features.

### 1) Prerequisites
- Python 3.8+
- A Google Cloud project
- Desktop OAuth Client (we use the Installed App flow)
- Browser available on the machine where you run the server

### 2) Enable APIs in Google Cloud
Enable these APIs in the same GCP project:
- Google Calendar API
- Gmail API

### 3) Create OAuth 2.0 Client (Desktop App)
1. Open the Google Cloud Console → APIs & Services → Credentials.
2. Create Credentials → OAuth client ID → Application type: Desktop app.
3. Copy the Client ID and Client Secret.
4. OAuth consent screen:
   - User type: External
   - Add test users (the Google accounts that will sign in)
   - Add scopes (you’ll still need to request them in your app):
     - Calendar: `https://www.googleapis.com/auth/calendar`
     - Gmail (as needed): `https://www.googleapis.com/auth/gmail.readonly`, `https://www.googleapis.com/auth/gmail.send`, `https://www.googleapis.com/auth/gmail.labels`, `https://www.googleapis.com/auth/gmail.modify`
5. Add redirect URI: `http://localhost:8080/oauth2callback` (adjust port if you change OAUTH_CALLBACK_PORT).

### 4) Configure environment variables
Copy `example.env` to `.env` and set values:

```dotenv
GOOGLE_CLIENT_ID='YOUR_CLIENT_ID'
GOOGLE_CLIENT_SECRET='YOUR_CLIENT_SECRET'
TOKEN_FILE_PATH='.gcp-saved-tokens.json'
OAUTH_CALLBACK_PORT=8080
GOOGLE_SCOPES='https://www.googleapis.com/auth/calendar, https://www.googleapis.com/auth/gmail.readonly, https://www.googleapis.com/auth/gmail.send, https://www.googleapis.com/auth/gmail.labels, https://www.googleapis.com/auth/gmail.modify'
```

Notes:
- Prefer `GOOGLE_SCOPES` to include all needed APIs. Alternatively, set `CALENDAR_SCOPES` and `GMAIL_SCOPES` (comma-separated) and they’ll be merged.
- If you previously authenticated with fewer scopes, delete the token file (`.gcp-saved-tokens.json`) and re-authenticate to grant the new ones.

### 5) Install dependencies
```bash
pip install -r requirements.txt
```

### 6) First run (authenticate)
```bash
python run_server.py
```
- A browser window opens. Approve the requested scopes.
- Tokens are saved to `TOKEN_FILE_PATH`.
- The FastAPI server starts at `http://127.0.0.1:8000`.

### 7) Try a few HTTP requests
- Health: `GET /health`
- Calendars: `GET /calendars`
- Find events: `GET /calendars/primary/events?max_results=5`
- Gmail labels: `GET /gmail/labels`
- Gmail search: `GET /gmail/messages?q=from:me&label_ids=INBOX&max_results=10`
- Gmail send (compose): `POST /gmail/messages:composeAndSend` with JSON:
  {
    "from_addr": "you@example.com",
    "to_addrs": ["someone@example.com"],
    "subject": "Hello",
    "body_text": "Hi!"
  }

### 8) Using via MCP (Cursor / Claude Desktop)
Point your MCP client to run this project’s entrypoint (`run_server.py`). Example JSON (see your client docs for exact location):

```json
{
  "tools": {
    "google_calendar": {
      "command": "python",
      "args": ["C:/path/to/calendar-mcp/run_server.py"]
    }
  }
}
```

Then invoke tools such as:
- `find_events(calendar_id="primary", max_results=5)`
- `gmail_list_messages(q="subject:Invoice", label_ids=["INBOX","UNREAD"])`
- `gmail_compose_and_send(from_addr="you@example.com", to_addrs=["a@b.com"], subject="Hi", body_text="Hello")`

### 9) Common issues
- 400/403 from Gmail: Ensure your token has Gmail scopes. Delete token file and re-auth.
- Invalid label: Use real label IDs from `GET /gmail/labels` (e.g., `INBOX`, `UNREAD`, or custom `Label_XXXX`).
- Redirect URI mismatch: Ensure `http://localhost:8080/oauth2callback` is in your OAuth client and matches `.env`.
- Multiple scopes: The consent screen governs what’s allowed, but your app must still request scopes via `GOOGLE_SCOPES`.

### 10) Where to next
- See `DOCS.md` for full architecture, endpoint reference, and MCP tool catalog.
- Check `calendar_mcp.log` for detailed logs.
