from distro import name
from asyncio import exceptions
import asyncio
import json 
import os
import sys
from typing import List,Dict
from groq import AsyncGroq
import uuid
from excutetool import tools,execute_function
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Import the workflow after loading env variables so that Groq() picks up the key
from workflow import get_medical_advice
# Generate a unique ID for this run
session_id = str(uuid.uuid4())


Model_Name = "openai/gpt-oss-20b"
tools_list = tools
client = AsyncGroq()

async def run_agent(user_message :str ,conversation_history:list , callback:dict)->dict:
    messages = [
        {"role": "system", "content": "You are a medical assistant help"}
    ]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    full_response = ""

    while True:
        current_text = ""
        tool_call_dict = {}
        stream_error = None

        try:
            stream = await client.chat.completions.create(
                model=Model_Name,
                messages=messages,
                tools=tools_list if tools_list else None,
                stream=True
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if delta.content:
                    current_text += delta.content
                    if "on_token" in callback:
                        callback["on_token"](delta.content)
                
                if delta.tool_calls:
                    for tc_chuck in delta.tool_calls:
                        idx = tc_chuck.index
                        if idx not in tool_call_dict:
                            tool_call_dict[idx] = {
                                "id": tc_chuck.id,
                                "name": tc_chuck.function.name,
                                "arguments": ""
                            }

                        if tc_chuck.function.arguments:
                            tool_call_dict[idx]["arguments"] += tc_chuck.function.arguments

        except Exception as e:
            stream_error = e 
            if not current_text:
                raise stream_error

            if stream_error and not current_text:
                fallback = "I apologize, but I wasn't able to generate a response. Could you please try rephrasing your message?"
                full_response = fallback
                if "on_token" in callback:
                    callback["on_token"](fallback)
            break
            
        full_response += current_text

        assistant_message = {"role": "assistant", "content": current_text or None}
    
        if not tool_call_dict:
            messages.append(assistant_message)
            break

        tool_call_list = []
        for idx, tc in tool_call_dict.items():
            tool_call_list.append({
                "id": tc["id"],
                "type": "function",
                "function": {
                    "name": tc["name"],
                    "arguments": tc["arguments"]
                }
            })

        assistant_message["tool_calls"] = tool_call_list
        messages.append(assistant_message)

        for tc in tool_call_list: 
            tool_name = tc["function"]["name"]
            arguments_str = tc["function"]["arguments"]
            try:
                args = json.loads(arguments_str) 
            except json.JSONDecodeError:
                args = {}

            result = execute_function(tool_name, arguments_str)

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "name": tool_name,
                "content": str(result)
            })

    if "on_complete" in callback:
        callback["on_complete"](full_response)

    return messages

    



async def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("Welcome to the AI Agent Test!")
    
    # Optional: maintain a conversation history if using run_agent
    conversation_history = [] 
    
    while True:
        user_input = input("\nUser: ")
        
        if user_input.lower() == "exit":
            break

        callbacks = {
            "on_token": lambda token: print(token, end="", flush=True),
            "on_tool_call_start": lambda name, args: print(f"  [Calling tool: {name}]"),
            "on_tool_call_end": lambda name, result: print(f"  [Tool {name} returned]"),
            "on_complete": lambda _: print(),  # newline after streaming finishes
        }
            
        # Example of awaiting your async function here
        response = await run_agent(user_input, conversation_history, callbacks)
        print(f"\nAI Agent: {response}")

if __name__ == "__main__":
    # Start the async event loop
    asyncio.run(main())
