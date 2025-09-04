import base64
import logging
from typing import Optional, List, Dict, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

# --- Helper: Build Gmail service ---

def _get_gmail_service(credentials: Credentials):
    try:
        service = build('gmail', 'v1', credentials=credentials)
        logger.debug("Gmail service client created successfully.")
        return service
    except Exception as e:
        logger.error(f"Failed to build Gmail service: {e}", exc_info=True)
        raise

# --- Actions ---

def list_messages(credentials: Credentials, user_id: str = 'me', query: Optional[str] = None, max_results: int = 50, label_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    service = _get_gmail_service(credentials)
    try:
        kwargs: Dict[str, Any] = {"userId": user_id, "maxResults": max_results}
        if query:
            kwargs["q"] = query
        if label_ids:
            kwargs["labelIds"] = label_ids
        resp = service.users().messages().list(**kwargs).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (list_messages): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in list_messages: {e}", exc_info=True)
        return None


def get_message(credentials: Credentials, message_id: str, user_id: str = 'me', format: str = 'full') -> Optional[Dict[str, Any]]:
    service = _get_gmail_service(credentials)
    try:
        resp = service.users().messages().get(userId=user_id, id=message_id, format=format).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (get_message): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_message: {e}", exc_info=True)
        return None


def send_message_raw(credentials: Credentials, raw_message_base64url: str, user_id: str = 'me') -> Optional[Dict[str, Any]]:
    """
    Send a message using a base64url-encoded raw RFC 2822 message.
    Caller is responsible for composing and encoding the raw message.
    """
    service = _get_gmail_service(credentials)
    try:
        body = {"raw": raw_message_base64url}
        resp = service.users().messages().send(userId=user_id, body=body).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (send_message_raw): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in send_message_raw: {e}", exc_info=True)
        return None


def list_labels(credentials: Credentials, user_id: str = 'me') -> Optional[Dict[str, Any]]:
    service = _get_gmail_service(credentials)
    try:
        resp = service.users().labels().list(userId=user_id).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (list_labels): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in list_labels: {e}", exc_info=True)
        return None


def build_raw_message(from_addr: str, to_addrs: List[str], subject: str, body_text: str) -> str:
    """
    Helper to compose a simple text email and return base64url-encoded raw string suitable for send_message_raw.
    """
    from email.mime.text import MIMEText

    mime = MIMEText(body_text)
    mime['to'] = ', '.join(to_addrs)
    mime['from'] = from_addr
    mime['subject'] = subject
    raw_bytes = base64.urlsafe_b64encode(mime.as_bytes())
    return raw_bytes.decode('utf-8')


def modify_message_labels(credentials: Credentials, message_id: str, add_labels: Optional[List[str]] = None, remove_labels: Optional[List[str]] = None, user_id: str = 'me') -> Optional[Dict[str, Any]]:
    """Adds and/or removes labels from a Gmail message.

    Args:
        credentials: OAuth2 credentials
        message_id: Gmail message ID
        add_labels: List of label IDs to add (e.g., ['INBOX','UNREAD'] or custom Label_XXXX)
        remove_labels: List of label IDs to remove
        user_id: Gmail user, default 'me'
    """
    service = _get_gmail_service(credentials)
    try:
        body: Dict[str, Any] = {}
        if add_labels:
            body['addLabelIds'] = add_labels
        if remove_labels:
            body['removeLabelIds'] = remove_labels
        resp = service.users().messages().modify(userId=user_id, id=message_id, body=body).execute()
        return resp
    except HttpError as e:
        logger.error(f"Gmail API error (modify_message_labels): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in modify_message_labels: {e}", exc_info=True)
        return None
