# Google Calendar Integration API

This Flask application integrates with the Google Calendar API, allowing users to authenticate via Google OAuth and create events in their Google Calendar.

---

## Features

- **Google OAuth 2.0 Integration**: Securely authenticate with Google.
- **Create Google Calendar Events**: Add events to your Google Calendar using the API.
- **Privacy Policy Endpoint**: View the app's privacy policy.

---

## Requirements

- Python 3.8 or above
- Google Cloud Project with Calendar API enabled
- `client_secret.json` file downloaded from the Google Cloud Console

---

## Setup and Installation

### 1. Enable the Google Calendar API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **APIs & Services > Library**.
4. Search for **Google Calendar API** and click **Enable**.
5. Go to **APIs & Services > Credentials**.
6. Create OAuth 2.0 credentials:
   - Choose **Web Application** as the application type.
   - Add the following redirect URI:
     ```
     https://<your-ngrok-domain>/handleAuth
     ```
7. Download the `client_secret.json` file and save it in the project directory.

---

### 2. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

---

### 3. Install Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

---

### 4. Run the Application Locally

1. Start the Flask application:
   ```bash
   python custom-gpt-google-calendar.py
   ```
2. Use [ngrok](https://ngrok.com/) to expose your local server:
   ```bash
   ngrok http 8080
   ```
3. Copy the provided `ngrok` public URL (e.g., `https://<your-ngrok-domain>`) for use with the API.

---

## API Endpoints

### 1. Privacy Policy

- **Endpoint**: `GET /privacy`
- **Description**: Displays the privacy policy of the application.
- **Response**: Returns an HTML page.

---

### 2. Start Google OAuth

- **Endpoint**: `GET /startAuth`
- **Description**: Initiates the OAuth 2.0 flow to authenticate the user for Google Calendar access.
- **Response Example**:

```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth..."
}
```

---

### 3. Handle OAuth Callback

- **Endpoint**: `GET /handleAuth`
- **Description**: Handles the OAuth callback and stores the user’s credentials.
- **Response Example**:

```json
{
  "message": "Authentication successful!"
}
```

---

### 4. Create a Google Calendar Event

- **Endpoint**: `POST /createEvent`
- **Description**: Creates a new event in the user’s Google Calendar.
- **Request Body Example**:

```json
{
  "title": "Team Meeting",
  "start_time": "2024-12-01T10:00:00",
  "end_time": "2024-12-01T11:00:00",
  "location": "Conference Room",
  "description": "Discussing project goals."
}
```

- **Response Example**:

```json
{
  "message": "Event created successfully!",
  "event_link": "https://www.google.com/calendar/event?eid=abc123xyz"
}
```

---

## Deployment

### Deploying with ngrok

1. Start the Flask application:
   ```bash
   python custom-gpt-google-calendar.py
   ```
2. Start ngrok to expose your application:
   ```bash
   ngrok http 8080
   ```
3. Use the `ngrok` public URL (e.g., `https://<your-ngrok-domain>`) as the server URL.

---

### Deploying on a Cloud Platform

#### Google Cloud Run

1. Create a Dockerfile for the application:
   ```dockerfile
   # Dockerfile
   FROM python:3.8-slim
   WORKDIR /app
   COPY . /app
   RUN pip install -r requirements.txt
   CMD ["python", "custom-gpt-google-calendar.py"]
   ```
2. Build and push the Docker image:
   ```bash
   docker build -t gcal-api .
   docker tag gcal-api gcr.io/<project-id>/gcal-api
   docker push gcr.io/<project-id>/gcal-api
   ```
3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy gcal-api --image gcr.io/<project-id>/gcal-api --platform managed --allow-unauthenticated
   ```

---

## Environment Variables

Set the following environment variables in your deployment environment:

- `OAUTHLIB_INSECURE_TRANSPORT=1` (for development)
- `CLIENT_SECRET_FILE=client_secret.json`
- `TOKEN_FILE=token.json`

---

## Testing

1. Use tools like **Postman** or **curl** to test the API.
2. Test each endpoint:
   - `GET /privacy`
   - `GET /startAuth`
   - `GET /handleAuth`
   - `POST /createEvent`

---

## Troubleshooting

### Common Issues:

1. **Invalid Redirect URI**:
   - Ensure the redirect URI in the Google Cloud Console matches your `ngrok` URL.

2. **Authentication Fails**:
   - Regenerate the `client_secret.json` file and verify the credentials.

---

## License

This project is licensed under the MIT License.

---

## Contact

If you have any questions, please contact hammad@thexsol.com.

---

### Improvements Over Previous Version
1. Fixed Markdown formatting issues (e.g., missing backticks and indentation).
2. Organized deployment steps more clearly.
3. Added structured headers and examples for all API endpoints.
4. Updated for better readability with properly formatted sections.

Let me know if you need further customization!