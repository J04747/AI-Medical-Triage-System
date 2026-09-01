import json
import os

# Directory to store session files
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), 'sessions')
os.makedirs(SESSIONS_DIR, exist_ok=True)

def get_file_path(chat_id: str) -> str:
    """Helper to get the full file path for a given chat_id."""
    return os.path.join(SESSIONS_DIR, f"{chat_id}.json")

def CreateFile(chat_id: str) -> str:
    """
    Generate a new file named <chat_id>.json and initialize it.
    """
    file_path = get_file_path(chat_id)
    data = {
        "chat_id": chat_id,
        "sympton": "???",
        "risk_level": ""
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return f"Created {chat_id}.json successfully."

def ReadFile(chat_id: str) -> str:
    """
    Locate <chat_id>.json, parse the JSON, and return the current sympton and risk_level.
    """
    file_path = get_file_path(chat_id)
    if not os.path.exists(file_path):
        return f"Error: Session file for {chat_id} does not exist."
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Return as a formatted string so the AI can easily read it
    return f"Symptom: {data.get('sympton')}, Risk Level: {data.get('risk_level')}"

def WriteFile(chat_id: str, new_symptom: str, new_risk_level: str) -> str:
    """
    Update the sympton string and set risk_level ('high', 'medium', or 'low').
    """
    file_path = get_file_path(chat_id)
    if not os.path.exists(file_path):
        return f"Error: Session file for {chat_id} does not exist."
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    data["sympton"] = new_symptom
    data["risk_level"] = new_risk_level
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    return f"Updated {chat_id}.json with symptom: '{new_symptom}' and risk level: '{new_risk_level}'."

def DeleteFile(chat_id: str) -> str:
    """
    Delete the <chat_id>.json file to close the session.
    """
    file_path = get_file_path(chat_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"Session {chat_id} closed and file deleted."
    return f"Error: Session file for {chat_id} does not exist."
