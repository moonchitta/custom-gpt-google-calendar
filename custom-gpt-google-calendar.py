from flask import Flask, request, jsonify
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import json

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# File paths and scopes
CLIENT_SECRET_FILE = 'client_secret.json'  # Path to your client_secret.json file
TOKEN_FILE = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

@app.route('/privacy', methods=['GET'])
def privacy():
    """
    Returns the privacy policy text as an HTML page.
    """
    privacy_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Privacy Policy</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>Privacy Policy</h1>
        <p>
            This application uses Google APIs to perform its operations. The app accesses user data
            only as necessary to fulfill its functionality, such as creating Google Calendar events. No user data
            is shared or stored beyond what is required to execute the requested functionality.
        </p>
        <p>
            The app complies with Google's User Data Policy, including the Limited Use requirements.
        </p>
        <p>
            If you have any questions or concerns about your data privacy, please contact us.
        </p>
    </body>
    </html>
    """
    return privacy_html

# Authentication flow
@app.route('/startAuth', methods=['GET'])
def start_auth():
    """
    Start the OAuth authentication flow.
    """
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    flow.redirect_uri = 'https://0feb-110-93-246-223.ngrok-free.app/handleAuth'
    auth_url, _ = flow.authorization_url(prompt='consent')
    return jsonify({'auth_url': auth_url}), 200

@app.route('/handleAuth', methods=['GET'])
def handle_auth():
    """
    Handle the OAuth callback and store credentials.
    """
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    flow.redirect_uri = 'https://0feb-110-93-246-223.ngrok-free.app/handleAuth'
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials
    with open(TOKEN_FILE, 'w') as token_file:
        token_file.write(creds.to_json())

    return jsonify({'message': 'Authentication successful!'}), 200

# Create a Google Calendar Event
@app.route('/createEvent', methods=['POST'])
def create_event():
    """
    Create a new event on Google Calendar.
    """
    data = request.json
    event_title = data.get('title')
    event_start = data.get('start_time')  # Format: YYYY-MM-DDTHH:MM:SS
    event_end = data.get('end_time')  # Format: YYYY-MM-DDTHH:MM:SS
    event_location = data.get('location', '')
    event_description = data.get('description', '')

    if not event_title or not event_start or not event_end:
        return jsonify({'error': 'Title, start_time, and end_time are required'}), 400

    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as token_file:
                creds_json = json.load(token_file)
                creds = Credentials.from_authorized_user_info(creds_json)
        else:
            return jsonify({'error': 'User not authenticated. Please authenticate at /startAuth'}), 401

        calendar_service = build('calendar', 'v3', credentials=creds)

        # Define the event
        event = {
            'summary': event_title,
            'location': event_location,
            'description': event_description,
            'start': {
                'dateTime': event_start,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': event_end,
                'timeZone': 'UTC',
            }
        }

        # Insert the event into the calendar
        created_event = calendar_service.events().insert(calendarId='primary', body=event).execute()

        return jsonify({'message': 'Event created successfully!', 'event_link': created_event.get('htmlLink')}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)