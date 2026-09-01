import os
import sys
import uuid
from dotenv import load_dotenv
from groq import Groq
from excutetool import tools, execute_function

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client
client = Groq()

# Generate a unique ID for this run
session_id = str(uuid.uuid4())

system_prompt = f"You are a session-management AI agent. The current chat_id for this session is '{session_id}'. Your job is to track user symptoms and risk levels by managing local JSON files. At the start of a conversation, use CreateFile to initialize a session record. As the chat progresses, use ReadFile to check current data and WriteFile to update the symptoms and risk level. When the conversation concludes, use DeleteFile to clean up the session."

def get_medical_advice(prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]
    try:
        # Step 1: Initial call with tools
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="openai/gpt-oss-20b", # Updated to a model that excels at tool calling
            temperature=0.0, # 0.0 is best for reliable tool execution
            max_tokens=1024,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls
        
        # If no tools were called, return the text message
        if not tool_calls:
            return response_message.content

        messages.append(response_message)
        
        # Step 2: Loop to handle consecutive tool calls (Chaining)
        while tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = tool_call.function.arguments
                print(f"\n[System] -> AI calling tool: {function_name}({arguments})")
                
                # Execute the actual Python tool
                function_response = execute_function(function_name, arguments)
                print(f"[System] -> Tool returned: {function_response}")
                
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
            
            # Send the tool responses back to the AI so it can continue
            second_response = client.chat.completions.create(
                messages=messages,
                model="openai/gpt-oss-120b",
                temperature=0.0,
                max_tokens=1024,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = second_response.choices[0].message
            messages.append(response_message)
            tool_calls = response_message.tool_calls
            
            if not tool_calls:
                return response_message.content

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    print("Welcome to the AI Agent Test!")
    
    while True:
        user_input = input("\nUser: ")
        
        if user_input.lower() == "exit":
            break
            
        response = get_medical_advice(user_input)
        print(f"\nAI Agent: {response}")
