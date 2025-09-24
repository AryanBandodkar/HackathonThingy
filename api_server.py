#!/usr/bin/env python3
"""
Simple HTTP API Server for FloatChat using built-in http.server
No external dependencies required
"""

import json
import sys
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

from ai_chatbot import AIChatbot

class FloatChatAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.chatbot = AIChatbot()
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/stats':
            self.handle_stats()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/chat':
            self.handle_chat()
        else:
            self.send_error(404, "Not Found")
    
    def handle_stats(self):
        """Handle stats endpoint"""
        try:
            # Get basic stats
            result = self.chatbot.process_user_input("Show me a summary of the data")
            
            if result['success'] and result['data']:
                data = result['data'][0]
                stats = {
                    'total_profiles': data.get('total_profiles', 0),
                    'unique_locations': data.get('unique_locations', 0),
                    'avg_temp': data.get('avg_temperature', 0),
                    'avg_salinity': data.get('avg_salinity', 0)
                }
                self.send_json_response({'success': True, 'stats': stats})
            else:
                self.send_json_response({'success': False, 'error': 'Could not load stats'})
                
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def handle_chat(self):
        """Handle chat endpoint"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            
            if not message:
                self.send_json_response({'success': False, 'error': 'No message provided'})
                return
            
            result = self.chatbot.process_user_input(message)
            self.send_json_response(result)
            
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        pass

def run_server(port=5000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FloatChatAPIHandler)
    
    print("🌊 FloatChat API Server Starting...")
    print(f"Server running on http://localhost:{port}")
    print("Endpoints available:")
    print(f"  GET  http://localhost:{port}/stats")
    print(f"  POST http://localhost:{port}/chat")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
