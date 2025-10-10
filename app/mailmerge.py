# app/mailmerge.py
from __future__ import print_function
import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate(creds_filename="credentials-mail-merge.json", token_filename="token.json"):
    """Authenticate user and return Gmail API service"""
    creds = None
    base_dir = os.path.dirname(__file__)
    creds_path = os.path.join(base_dir, creds_filename)
    token_path = os.path.join(base_dir, token_filename)

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    f"Missing credentials file: {creds_path}. Create OAuth client credentials and save as {creds_path}."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    try:
        sent = service.users().messages().send(userId=user_id, body=message).execute()
        return sent
    except Exception as e:
        raise

def send_emails(messages, sender="me"):
    """
    messages: list of dicts { 'to': email, 'subject': subject, 'body': body }
    This function authenticates once and sends all messages.
    """
    service = gmail_authenticate()
    results = []
    for msg in messages:
        raw = create_message(sender, msg['to'], msg['subject'], msg['body'])
        sent = send_message(service, sender, raw)
        results.append(sent)
    return results
