
# Medical Helper

Medical Helper is an AI-powered medical assistant application that provides users with an intelligent chat interface to discuss their symptoms. It also includes a comprehensive supervisor dashboard for medical professionals to monitor user sessions, symptoms, and assigned risk levels.

## Features

- **AI Chat Assistant:** A conversational interface powered by an LLM (Groq API) where users can discuss their symptoms. The AI gathers necessary details, assesses risk levels, and guides users.
- **User Registration System:** Once enough information is gathered, the AI prompts users to sign up and save their personal information (Name, Age, Gender, Location).
- **Session Management:** The application manages user sessions and saves chat data locally.
- **Supervisor Dashboard:** A protected area for medical supervisors (Login: `abc` / `abc123`) to view a list of all registered users and drill down into specific session details, including reported symptoms and assessed risk levels.

## Project Structure

- `html/`: Contains the frontend HTML files (`begin.html`, `core.html`, `index.html`, `supervisor_login.html`, `supervisor_dashboard.html`).
- `CSS/` & `js/`: Frontend styles and scripts.
- `server.py`: The main Python backend server handling API requests and data management.
- `dataset/`: Directory where user JSON data is stored.
- `AI agent/`: Contains the logic for the Groq LLM integration and tool executions.

## Prerequisites

- Python 3.x
- [Groq API Key](https://console.groq.com/keys)

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd "Medical helper"
   ```

2. **Set up the Virtual Environment:**
   It is recommended to use a virtual environment.
   ```bash
   python -m venv "AI agent/venv"
   # On Windows:
   "AI agent/venv/Scripts/activate"
   # On macOS/Linux:
   source "AI agent/venv/bin/activate"
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r "AI agent/requirements.txt"
   ```

4. **Environment Variables:**
   Create a `.env` file inside the `AI agent` directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Running the Application

1. **Start the Backend Server:**
   ```bash
   python server.py
   ```
   The server will run on `http://localhost:8000`.

2. **Open the Application:**
   Open `html/begin.html` in your web browser to access the starting page.

## Usage Flow

1. Go to `begin.html` and click **Chat with Assistant**.
2. Discuss symptoms with the AI. Once enough information is gathered, the AI will prompt for a sign-up.
3. The user is redirected to `index.html` to complete their profile.
4. Supervisors can go to `begin.html` and click **Supervisor Account**.
5. Log in using `abc` as the Account ID and `abc123` as the Password.
6. View the dashboard with user statistics and detailed session logs.

## Testing

The project includes an automated test suite using `pytest` located in the `test/` directory.

To run the tests, navigate to the root directory and execute:

```bash
python -m pytest test\ -v
```

Ensure you have installed the testing dependencies (e.g., `pytest`, `httpx`).
