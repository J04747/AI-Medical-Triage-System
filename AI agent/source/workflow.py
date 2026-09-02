from groq import Groq
from excutetool import tools, execute_function

# Initialize the Groq client
client = Groq()

sessions_memory = {}

def get_medical_advice(prompt: str, session_id: str) -> str:
    if session_id not in sessions_memory:
        system_prompt = f"You are a session-management AI agent. The current chat_id for this session is '{session_id}'. Your job is to track user symptoms, risk levels, and additional details by managing local JSON files. At the start of a conversation, use CreateFile to initialize a session record. When a user inputs a symptom, ask follow-up questions to gather more information (like duration, severity, etc.) and store this as 'detail'. As the chat progresses, use ReadFile to check current data and WriteFile to update the symptoms, risk level, and detail. When the user asks about the number of similar cases or historical data, use SearchCases. When you have gathered enough symptom information and assessed the risk level, or when the user wants to sign up, use ProcessSignUp to handle the sign-up flow and account linking. When the conversation concludes, use DeleteFile to clean up the session."
        sessions_memory[session_id] = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

    messages = sessions_memory[session_id]
    messages.append({
        "role": "user",
        "content": prompt,
    })
    try:
        # Step 1: Initial call with tools
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="openai/gpt-oss-120b", # Updated to a valid Groq model for tool calling
            temperature=0.0, # 0.0 is best for reliable tool execution
            max_tokens=1024,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls
        
        # If no tools were called, return the text message
        if not tool_calls:
            messages.append(response_message)
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
        import traceback
        traceback.print_exc()
        return f"An error occurred: {e}"
