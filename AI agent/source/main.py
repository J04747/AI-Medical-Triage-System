import os
import sys
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Import the workflow after loading env variables so that Groq() picks up the key
from workflow import get_medical_advice


# Generate a unique ID for this run
session_id = str(uuid.uuid4())

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    print("Welcome to the AI Agent Test!")
    while True:
        user_input = input("\nUser: ")
        
        if user_input.lower() == "exit":
            break
            
        response = get_medical_advice(user_input, session_id)
        print(f"\nAI Agent: {response}")
