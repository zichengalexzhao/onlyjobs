# scripts/gmail_fetch.py

from google.auth import default
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds, _ = default(scopes=SCOPES)
    return build('gmail', 'v1', credentials=creds)

def fetch_emails(since_hours=1):
    service = get_gmail_service()
    
    query = ""
    if since_hours is not None:
        time_threshold = (datetime.now() - timedelta(hours=since_hours)).strftime('%Y/%m/%d')
        query = f"after:{time_threshold}"
    
    all_messages = []
    response = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query, maxResults=500).execute()
    messages = response.get('messages', [])
    all_messages.extend(messages or [])
    
    while 'nextPageToken' in response:
        response = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            q=query,
            pageToken=response['nextPageToken'],
            maxResults=500
        ).execute()
        messages = response.get('messages', [])
        all_messages.extend(messages or [])

    return all_messages

def get_email_snippet(message_id):
    service = get_gmail_service()
    message = service.users().messages().get(userId='me', id=message_id, format='minimal').execute()
    return message.get('snippet', '')

def get_email_content(message_id):
    import base64

    service = get_gmail_service()
    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    payload = message.get('payload', {})
    parts = payload.get('parts', [])
    body = ""
    
    if parts:
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body += part.get('body', {}).get('data', '')
    else:
        body = payload.get('body', {}).get('data', '')

    if body:
        body = base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')
    else:
        body = message.get('snippet', '')

    headers = payload.get('headers', [])
    from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
    internal_date = int(message.get('internalDate', 0)) / 1000
    email_date = datetime.fromtimestamp(internal_date).strftime('%Y-%m-%d') if internal_date else 'Unknown'

    full_content = f"From: {from_header}\nSubject: {subject}\n\n{body}"
    return {"content": full_content[:4000], "date": email_date}