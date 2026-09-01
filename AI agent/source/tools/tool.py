import json
import os

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
    Generate a new file named <chat_id>.json and initialize it.
    """
    file_path = get_file_path(chat_id)
    data = {
        "chat_id": chat_id,
        "sympton": "???",
        "risk_level": "",
        "detail": ""
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

def RequestSignUp(chat_id: str) -> str:
    """
    Called when the AI agent feels it has collected enough information and the risk level is assessed, 
    requesting the user to sign up for further medical assistance.
    """
    return "[ACTION_REQUIRED: SIGNUP]"
