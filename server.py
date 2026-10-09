from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import json
import os
import uuid
import sys
import subprocess
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file for Groq API
env_path = os.path.join(os.path.dirname(__file__), 'AI agent', '.env')
load_dotenv(dotenv_path=env_path)

# Add AI agent source to sys.path to import workflow
ai_agent_path = os.path.join(os.path.dirname(__file__), 'AI agent', 'source')
if ai_agent_path not in sys.path:
    sys.path.append(ai_agent_path)
from workflow import get_medical_advice

# Define the directory to save the JSON files
DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset')
os.makedirs(DATASET_DIR, exist_ok=True)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread to prevent blocking."""
    daemon_threads = True

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/users':
            try:
                users = []
                if os.path.exists(DATASET_DIR):
                    for filename in os.listdir(DATASET_DIR):
                        if filename.endswith('.json'):
                            file_path = os.path.join(DATASET_DIR, filename)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                users.append(json.load(f))
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "users": users}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_OPTIONS(self):
        # Handle preflight CORS request
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/save_user':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                user_id = data.get('userid')
                if not user_id:
                    user_id = str(uuid.uuid4())
                    data['userid'] = user_id
                
                # Ensure dataset directory exists (in case it was deleted while server was running)
                os.makedirs(DATASET_DIR, exist_ok=True)
                
                file_path = os.path.join(DATASET_DIR, f"{user_id}.json")
                
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                else:
                    existing_data = {}
                
                chat_ids = existing_data.get('chat_ids', [])
                if 'chatid' in data:
                    chat_id = data.pop('chatid')
                    if chat_id and chat_id not in chat_ids:
                        chat_ids.append(chat_id)
                
                existing_data.update(data)
                existing_data['chat_ids'] = chat_ids
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=4, ensure_ascii=False)
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "userid": user_id}).encode('utf-8'))
                print(f"Successfully saved user data to {file_path}")
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                print(f"Error saving data: {str(e)}")
        elif self.path == '/api/link_chat':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                user_id = data.get('userid')
                chat_id = data.get('chatid')
                
                if not user_id or not chat_id:
                    raise ValueError("userid and chatid are required")
                
                os.makedirs(DATASET_DIR, exist_ok=True)
                file_path = os.path.join(DATASET_DIR, f"{user_id}.json")
                
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        user_data = json.load(f)
                else:
                    user_data = {"userid": user_id}
                    
                chat_ids = user_data.get("chat_ids", [])
                if chat_id not in chat_ids:
                    chat_ids.append(chat_id)
                user_data["chat_ids"] = chat_ids
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, indent=4, ensure_ascii=False)
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "userid": user_id, "chat_ids": chat_ids}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif self.path == '/api/chat':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                message = data.get('message')
                session_id = data.get('session_id')
                context = data.get('context')
                
                if not message or not session_id:
                    raise ValueError("message and session_id are required")
                
                # Save context if provided
                sessions_dir = os.path.join(os.path.dirname(__file__), 'AI agent', 'source', 'tools', 'sessions')
                os.makedirs(sessions_dir, exist_ok=True)
                file_path = os.path.join(sessions_dir, f"{session_id}.json")
                if context:
                    existing_data = {}
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            try:
                                existing_data = json.load(f)
                            except json.JSONDecodeError:
                                pass
                    existing_data["context"] = context
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, indent=4)
                
                # Call the AI Agent (now asynchronous)
                response = asyncio.run(get_medical_advice(message, session_id))
                
                # Extract metadata (risk_level, etc)
                metadata = {}
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            session_data = json.load(f)
                            risk_level = session_data.get('risk_level')
                            if risk_level:
                                metadata['risk_level'] = risk_level
                                if risk_level.lower() == 'high':
                                    metadata['escalation_required'] = True
                        except json.JSONDecodeError:
                            pass
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"reply": response, "metadata": metadata}).encode('utf-8'))
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
                print(f"Client disconnected before the response could be sent ({type(e).__name__}).")
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif self.path == '/api/sessions':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                chat_ids = data.get('chat_ids', [])
                sessions_dir = os.path.join(os.path.dirname(__file__), 'AI agent', 'source', 'tools', 'sessions')
                sessions = []
                
                if os.path.exists(sessions_dir):
                    for chat_id in chat_ids:
                        file_path = os.path.join(sessions_dir, f"{chat_id}.json")
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                sessions.append(json.load(f))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "sessions": sessions}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = 8000
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, RequestHandler)
    print(f"Server is running on http://localhost:{port} (threaded)")
    print(f"Data will be saved to {DATASET_DIR}")
    
    # Start the phi-redactor proxy as a subprocess
    phi_proxy_process = None
    try:
        phi_executable = os.path.join(os.path.dirname(__file__), 'AI agent', 'venv', 'Scripts', 'phi-redactor.exe')
        
        # Set environment variable for phi-redactor plugins
        env = os.environ.copy()
        env['PHI_REDACTOR_PLUGINS_DIR'] = os.path.join(os.path.dirname(__file__), 'AI agent', 'plugins')
        
        phi_proxy_process = subprocess.Popen([phi_executable, "serve", "--port", "8081"], env=env)
        print("Started phi-redactor proxy on port 8081")
    except Exception as e:
        print(f"Failed to start phi-redactor proxy: {e}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()
        if phi_proxy_process:
            print("Terminating phi-redactor proxy...")
            phi_proxy_process.terminate()
            phi_proxy_process.wait()
