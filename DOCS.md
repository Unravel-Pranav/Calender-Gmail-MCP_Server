# Project Documentation

## Overview
This project provides an MCP-compatible server that exposes Google Calendar and Gmail capabilities through a FastAPI backend and an MCP bridge. It enables LLMs and tools to perform scheduling, analysis, and email workflows.

## Architecture
- `src/auth.py`: Handles OAuth 2.0 Installed App flow, token storage, and refresh. Scopes are built from `GOOGLE_SCOPES` or the union of `CALENDAR_SCOPES` + `GMAIL_SCOPES`.
- `src/server.py`: FastAPI application exposing REST endpoints for Calendar and Gmail.
- `src/calendar_actions.py`: Calendar business logic (list/find/create/update/delete, attendees, free/busy, mutual scheduling, busyness analysis).
- `src/gmail_actions.py`: Gmail business logic (list messages, get message, send message, list labels, modify labels).
- `src/mcp_bridge.py`: MCP tools mapping that call the HTTP API.
- `src/models.py`: Pydantic data models for Calendar requests/responses and analysis payloads.
- `run_server.py`: Entrypoint that runs the server and MCP bridge as appropriate.

## Authentication & Scopes
- Set `GOOGLE_SCOPES` to a comma-separated list of all scopes you need (recommended). Example:
  `https://www.googleapis.com/auth/calendar, https://www.googleapis.com/auth/gmail.readonly, https://www.googleapis.com/auth/gmail.send, https://www.googleapis.com/auth/gmail.labels, https://www.googleapis.com/auth/gmail.modify`
- Alternatively, set `CALENDAR_SCOPES` and `GMAIL_SCOPES`; they will be merged.
- If you expand scopes after first auth, delete the token file and re-authenticate.

## Endpoints (selection)

### Health
- `GET /health`: Returns server status and whether credentials are valid.

### Calendars
- `GET /calendars`: List calendars. Optional `min_access_role`.
- `POST /calendars`: Create a calendar.
- `GET /calendars/{calendar_id}/events`: Find events. Supports `time_min`, `time_max`, `q`, `max_results`, `single_events`, `order_by`.
- `POST /calendars/{calendar_id}/events`: Create event (detailed model).
- `POST /calendars/{calendar_id}/events/quickAdd`: Quick add via text.
- `PATCH /calendars/{calendar_id}/events/{event_id}`: Update event.
- `DELETE /calendars/{calendar_id}/events/{event_id}`: Delete event.
- `POST /calendars/{calendar_id}/events/{event_id}/attendees`: Add attendees.

### Advanced Scheduling & Analysis
- `POST /events/check_attendee_status`
- `POST /freeBusy`
- `POST /schedule_mutual`
- `POST /project_recurring`
- `POST /analyze_busyness`

### Gmail
- `GET /gmail/labels`: List labels.
- `GET /gmail/messages`: List messages. Query via `q`, filter with `label_ids`, limit with `max_results`.
- `GET /gmail/messages/{message_id}`: Get a message. `format` can be `minimal|full|raw|metadata`.
- `POST /gmail/messages:sendRaw`: Send base64url-encoded RFC 2822 message.
- `POST /gmail/messages:composeAndSend`: Compose and send plain text email.
- `POST /gmail/messages/{message_id}:modify`: Add/remove labels.

## MCP Tools (selection)
- Calendar:
  - `list_calendars(min_access_role?)`
  - `find_events(calendar_id, time_min?, time_max?, query?, max_results?)`
  - `create_event(...)`, `quick_add_event(...)`, `update_event(...)`, `delete_event(...)`, `add_attendee(...)`
  - `check_attendee_status(...)`, `query_free_busy(...)`, `schedule_mutual(...)`, `analyze_busyness(...)`
- Gmail:
  - `gmail_list_labels(user_id?)`: Lists labels.
  - `gmail_list_messages(q?, max_results?, label_ids?, user_id?)`: Searches mail (Gmail query syntax) and filters by labels.
  - `gmail_get_message(message_id, format?, user_id?)`
  - `gmail_send_raw(raw_base64url, user_id?)`
  - `gmail_compose_and_send(from_addr, to_addrs[], subject, body_text, user_id?)`
  - `gmail_modify_labels(message_id, add_labels?, remove_labels?, user_id?)`

## Data Models (high-level)
- Calendar models (events, attendees, reminders, calendar list) live in `src/models.py` and mirror Google Calendar v3 structures using Pydantic.
- Gmail endpoints return raw Google API responses (dicts) intentionally, since Gmail shapes vary widely per request/format.

## Logging
- Logs go to `calendar_mcp.log` by default. Increase verbosity in code if needed.

## Error Handling & Tips
- Gmail 400 “Invalid label”: Use real label IDs. Get them from `/gmail/labels`.
- 403/401: Re-authenticate or ensure scopes include required Gmail/Calendar permissions.
- Time parsing: Calendar endpoints accept RFC3339 strings (we parse with `dateutil`).

## Extending
- Add new Gmail/Calendar actions in `*_actions.py`, then expose them via FastAPI (`src/server.py`) and as MCP tools (`src/mcp_bridge.py`).
- Keep scope additions in `.env` and re-auth when adding new APIs.
