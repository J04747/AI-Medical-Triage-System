import json
from tools.tool import CreateFile, ReadFile, WriteFile, DeleteFile

# Define the tools (JSON Schema) for the Groq API
tools = [
    {
        "type": "function",
        "function": {
            "name": "CreateFile",
            "description": "Initialize a session record by creating a new file named <chat_id>.json. Use this tool immediately when a new user begins chatting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "The unique identifier for the chat session, e.g., 'a001'."
                    }
                },
                "required": ["chat_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ReadFile",
            "description": "Locate <chat_id>.json, parse the JSON, and return the current sympton and risk_level strings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "The unique identifier for the chat session."
                    }
                },
                "required": ["chat_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "WriteFile",
            "description": "Update the sympton string with the latest medical context, and set risk_level strictly to 'high', 'medium', or 'low'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "The unique identifier for the chat session."
                    },
                    "new_symptom": {
                        "type": "string",
                        "description": "The symptom described by the user."
                    },
                    "new_risk_level": {
                        "type": "string",
                        "description": "The risk level: 'high', 'medium', or 'low'."
                    }
                },
                "required": ["chat_id", "new_symptom", "new_risk_level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "DeleteFile",
            "description": "Close the session by deleting the <chat_id>.json file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "The unique identifier for the chat session."
                    }
                },
                "required": ["chat_id"]
            }
        }
    }
]

# Helper to execute the function called by the AI
def execute_function(function_name, arguments):
    args = json.loads(arguments)
    if function_name == "CreateFile":
        return CreateFile(args["chat_id"])
    elif function_name == "ReadFile":
        return ReadFile(args["chat_id"])
    elif function_name == "WriteFile":
        return WriteFile(args["chat_id"], args["new_symptom"], args["new_risk_level"])
    elif function_name == "DeleteFile":
        return DeleteFile(args["chat_id"])
    return "Function not found."
