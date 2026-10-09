import json
import os
import webbrowser

# Directory to store session files
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), 'sessions')
os.makedirs(SESSIONS_DIR, exist_ok=True)

DATASET_FILE = os.path.join(os.path.dirname(__file__), 'dataset.json')

def load_dataset() -> dict:
    if not os.path.exists(DATASET_FILE):
        return {}
    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_dataset(data: dict):
    with open(DATASET_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def get_file_path(chat_id: str) -> str:
    """Helper to get the full file path for a given chat_id."""
    return os.path.join(SESSIONS_DIR, f"{chat_id}.json")

def CreateFile(chat_id: str) -> str:
    """
    Generate a new file named <chat_id>.json and initialize it, preserving any existing context.
    """
    file_path = get_file_path(chat_id)
    
    existing_context = None
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
                existing_context = existing_data.get('context')
            except json.JSONDecodeError:
                pass
                
    data = {
        "chat_id": chat_id,
        "sympton": "???",
        "risk_level": "",
        "detail": ""
    }
    
    if existing_context:
        data["context"] = existing_context
        
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
    return f"Symptom: {data.get('sympton')}, Risk Level: {data.get('risk_level')}, Detail: {data.get('detail')}"

def WriteFile(chat_id: str, new_symptom: str, new_risk_level: str, new_detail: str) -> str:
    """
    Update the sympton string, set risk_level ('high', 'medium', or 'low'), and add detail.
    """
    file_path = get_file_path(chat_id)
    if not os.path.exists(file_path):
        return f"Error: Session file for {chat_id} does not exist."
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    old_symptom = data.get("sympton", "???")
    data["sympton"] = new_symptom
    data["risk_level"] = new_risk_level
    data["detail"] = new_detail
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    # Update dataset
    if new_symptom != "???" and new_symptom != old_symptom:
        dataset = load_dataset()
        if new_symptom not in dataset:
            dataset[new_symptom] = {"case_count": 0, "recent_cases": []}
        
        dataset[new_symptom]["case_count"] += 1
        if chat_id not in dataset[new_symptom]["recent_cases"]:
            dataset[new_symptom]["recent_cases"].append(chat_id)
            
        save_dataset(dataset)
        
    return f"Updated {chat_id}.json with symptom: '{new_symptom}', risk level: '{new_risk_level}', and detail: '{new_detail}'."

def DeleteFile(chat_id: str) -> str:
    """
    Delete the <chat_id>.json file to close the session.
    """
    file_path = get_file_path(chat_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"Session {chat_id} closed and file deleted."
    return f"Error: Session file for {chat_id} does not exist."

def SearchCases(symptom: str) -> str:
    """
    Search the dataset for a specific symptom to get case counts and recent case IDs.
    """
    dataset = load_dataset()
    symptom_lower = symptom.lower().strip()
    
    # Try case-insensitive and partial matching
    for key, info in dataset.items():
        if key.lower() == symptom_lower or symptom_lower in key.lower() or key.lower() in symptom_lower:
            count = info.get("case_count", 0)
            recent = info.get("recent_cases", [])
            return f"Found {count} case(s) for '{key}'. Recent cases: {', '.join(recent)}"

    return f"No cases found for symptom '{symptom}'."

def ProcessSignUp(chat_id: str, user_id: str = None) -> str:
    """
    Handles the entire sign-up and linking process. 
    If the user wants to create an account, it opens the sign-up page and requests action.
    If the user already has an account and provides a user_id, it links the account.
    """
    result = ""
    # 1. Open signup page if no user_id is provided
    if not user_id:
        from pathlib import Path
        import webbrowser
        html_path = Path(__file__).resolve().parent.parent.parent.parent / 'html' / 'index.html'
        url = f"{html_path.as_uri()}?chatid={chat_id}"
        webbrowser.open(url)
        result += f"[ACTION_REQUIRED: SIGNUP]\nRedirected user to signup page with chat_id {chat_id}."
    
    # 2. Link account if user_id is provided
    if user_id:
        import urllib.request
        import json
        url = "http://localhost:8000/api/link_chat"
        data = {"userid": user_id, "chatid": chat_id}
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                link_msg = f"Successfully linked chat {chat_id} to user {user_id}. Total chats linked: {len(res.get('chat_ids', []))}"
                result += f"\n{link_msg}" if result else link_msg
        except Exception as e:
            err_msg = f"Error linking account: {str(e)}"
            result += f"\n{err_msg}" if result else err_msg
            
    return result
