from groq import AsyncGroq
from excutetool import tools, execute_function
import httpx
import json

# Initialize the Groq client
client = AsyncGroq()

sessions_memory = {}
phi_sessions = {}

PHI_PROXY_URL = "http://localhost:8081/api/v1"

async def rehydrate_text(text: str, phi_session_id: str) -> str:
    if not text or not phi_session_id:
        return text
    try:
        async with httpx.AsyncClient() as http_client:
            resp = await http_client.post(f"{PHI_PROXY_URL}/rehydrate", json={
                "text": text,
                "session_id": phi_session_id
            }, timeout=10.0)
            resp.raise_for_status()
            return resp.json().get("text", text)
    except Exception as e:
        print(f"Failed to rehydrate text: {e}")
        return text

async def redact_text(text: str, phi_session_id: str) -> str:
    if not text or not phi_session_id:
        return text
    try:
        async with httpx.AsyncClient() as http_client:
            resp = await http_client.post(f"{PHI_PROXY_URL}/redact", json={
                "text": text,
                "session_id": phi_session_id
            }, timeout=10.0)
            resp.raise_for_status()
            return resp.json().get("redacted_text", text)
    except Exception as e:
        print(f"Failed to redact text: {e}")
        return text

async def get_medical_advice(prompt: str, session_id: str, callback: dict = None) -> str:
    if callback is None:
        callback = {}

    # 1. Redact user prompt
    redact_payload = {"text": prompt}
    if session_id in phi_sessions:
        redact_payload["session_id"] = phi_sessions[session_id]
        
    try:
        async with httpx.AsyncClient() as http_client:
            resp = await http_client.post(f"{PHI_PROXY_URL}/redact", json=redact_payload, timeout=10.0)
            resp.raise_for_status()
            redact_result = resp.json()
            redacted_prompt = redact_result["redacted_text"]
            phi_sessions[session_id] = redact_result["session_id"]
    except Exception as e:
        print(f"Failed to redact prompt: {e}")
        redacted_prompt = prompt  # Fallback if proxy is down

    if session_id not in sessions_memory:
        system_prompt = f"You are a session-management AI assistant for the medical clinic, not a doctor. If asked, clarify your identity honestly. Inform the user that a human doctor, nurse, or medical staff from the clinic will get involved if needed or for real medical advice. The current chat_id for this session is '{session_id}'. Your job is to track user symptoms, risk levels, and additional details by managing local JSON files. At the start of a conversation, use CreateFile to initialize a session record. When a user inputs a symptom, ask follow-up questions to gather more information (like duration, severity, etc.) and store this as 'detail'. As the chat progresses, use ReadFile to check current data and WriteFile to update the symptoms, risk level, and detail. When the user asks about the number of similar cases or historical data, use SearchCases. When you have gathered enough symptom information and assessed the risk level, or when the user wants to sign up, use ProcessSignUp to handle the sign-up flow and account linking. When the conversation concludes, use DeleteFile to clean up the session."
        sessions_memory[session_id] = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

    messages = sessions_memory[session_id]
    messages.append({
        "role": "user",
        "content": redacted_prompt,
    })
    
    full_response = ""

    while True:
        current_text = ""
        tool_call_dict = {}
        stream_error = None

        try:
            stream = await client.chat.completions.create(
                messages=messages,
                model="openai/gpt-oss-120b",
                temperature=0.0,
                max_tokens=1024,
                tools=tools,
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
                    for tc_chunk in delta.tool_calls:
                        idx = tc_chunk.index
                        if idx not in tool_call_dict:
                            tool_call_dict[idx] = {
                                "id": tc_chunk.id,
                                "name": tc_chunk.function.name,
                                "arguments": ""
                            }

                        if tc_chunk.function.arguments:
                            tool_call_dict[idx]["arguments"] += tc_chunk.function.arguments

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
            rehydrated_full_response = await rehydrate_text(full_response, phi_sessions.get(session_id))
            if "on_complete" in callback:
                callback["on_complete"](rehydrated_full_response)
            return rehydrated_full_response

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
            
            if "on_tool_call_start" in callback:
                callback["on_tool_call_start"](tool_name, arguments_str)
                
            try:
                args = json.loads(arguments_str) 
            except json.JSONDecodeError:
                args = {}

            # Rehydrate arguments before local execution so real data is saved
            real_arguments = await rehydrate_text(arguments_str, phi_sessions.get(session_id))
            print(f"\n[System] -> AI calling tool: {tool_name}({real_arguments})")
            
            # Execute the actual Python tool with real arguments
            function_response = execute_function(tool_name, real_arguments)
            print(f"[System] -> Tool returned: {function_response}")
            
            if "on_tool_call_end" in callback:
                callback["on_tool_call_end"](tool_name, function_response)
            
            # Redact tool response before giving it to LLM
            redacted_function_response = await redact_text(str(function_response), phi_sessions.get(session_id))
            
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "name": tool_name,
                "content": redacted_function_response
            })
