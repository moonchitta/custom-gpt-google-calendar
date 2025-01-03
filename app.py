import requests
from flask import Flask, request, jsonify
from google.apps import meet_v2
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import json

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# File paths and scopes
REDIRECT_URI = 'https://c6a1-2407-d000-1a-f44b-8cab-70b3-fad9-71c6.ngrok-free.app/handleAuth'  # Path to your client_secret.json file
CLIENT_SECRET_FILE = 'client_secret.json'  # Path to your client_secret.json file
TOKEN_FILE = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/meetings.space.created']

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
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(prompt='consent')
    return jsonify({'auth_url': auth_url}), 200

@app.route('/handleAuth', methods=['GET'])
def handle_auth():
    """
    Handle the OAuth callback and store credentials.
    """
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    flow.redirect_uri = REDIRECT_URI
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

        print(f"Event: {event}")

        # Insert the event into the calendar
        created_event = calendar_service.events().insert(calendarId='primary', body=event).execute()

        return jsonify({'message': 'Event created successfully!', 'event_link': created_event.get('htmlLink')}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/getEvents', methods=['GET'])
def get_events():
    """
    Get a list of events on a specific date.
    """
    date = request.args.get('date')  # Format: YYYY-MM-DD

    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as token_file:
                creds_json = json.load(token_file)
                creds = Credentials.from_authorized_user_info(creds_json)
        else:
            return jsonify({'error': 'User not authenticated. Please authenticate at /startAuth'}), 401

        calendar_service = build('calendar', 'v3', credentials=creds)

        time_min = f"{date}T00:00:00Z"
        time_max = f"{date}T23:59:59Z"

        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        return jsonify({'events': events}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/updateEvent', methods=['PUT'])
def update_event():
    """
    Update an existing Google Calendar event.
    """
    data = request.json
    event_id = data.get('event_id')
    updates = {
        'summary': data.get('title'),
        'location': data.get('location'),
        'description': data.get('description'),
        'start': {'dateTime': data.get('start_time'), 'timeZone': 'UTC'},
        'end': {'dateTime': data.get('end_time'), 'timeZone': 'UTC'}
    }

    if not event_id:
        return jsonify({'error': 'Event ID is required'}), 400

    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as token_file:
                creds_json = json.load(token_file)
                creds = Credentials.from_authorized_user_info(creds_json)
        else:
            return jsonify({'error': 'User not authenticated. Please authenticate at /startAuth'}), 401

        calendar_service = build('calendar', 'v3', credentials=creds)

        # Update the event
        updated_event = calendar_service.events().patch(
            calendarId='primary',
            eventId=event_id,
            body={key: value for key, value in updates.items() if value}
        ).execute()

        return jsonify({'message': 'Event updated successfully!', 'event': updated_event}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/createMeetingWithCalendar', methods=['POST'])
def create_meeting_with_calendar():
    """
    Create a Google Meet space using Meet API, then add it to Google Calendar with a set title, date, and time.
    """
    data = request.json
    meeting_title = data.get('title')
    meeting_date = data.get('date')  # Format: YYYY-MM-DD
    meeting_time = data.get('time')  # Format: HH:MM:SS
    participants = data.get('participants', [])  # Optional list of emails

    if not meeting_title or not meeting_date or not meeting_time:
        return jsonify({'error': 'Title, date, and time are required'}), 400

    try:
        # Load credentials for both APIs
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as token_file:
                creds_json = json.load(token_file)
                creds = Credentials.from_authorized_user_info(creds_json)
        else:
            return jsonify({'error': 'User not authenticated. Please authenticate at /startAuth'}), 401

        # Step 1: Create a meeting space using Google Meet API
        meet_client = meet_v2.SpacesServiceClient(credentials=creds)
        space_request = meet_v2.CreateSpaceRequest()
        meet_response = meet_client.create_space(request=space_request)

        # Get the meeting link
        meet_link = meet_response.meeting_uri

        # Step 2: Insert the meeting link into a Google Calendar event
        calendar_service = build('calendar', 'v3', credentials=creds)

        # Combine date and time for event start and end
        start_time = f"{meeting_date}T{meeting_time}:00Z"  # Adjust time zone as needed
        end_time = f"{meeting_date}T{int(meeting_time.split(':')[0]) + 1}:00:00Z"  # 1-hour duration

        # Define the event
        event = {
            'summary': meeting_title,
            'description': f"Google Meet Link: {meet_link}",
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
            'attendees': [{'email': email} for email in participants],
        }

        # Insert the event into Google Calendar
        created_event = calendar_service.events().insert(calendarId='primary', body=event).execute()

        return jsonify({
            'message': 'Meeting space and calendar event created successfully!',
            'meet_link': meet_link,
            'calendar_event_link': created_event.get('htmlLink')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)