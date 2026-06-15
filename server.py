import http.server
import socketserver
import json
import os
import datetime

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/save-eval':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Create directory if it doesn't exist
                eval_dir = os.path.join(os.getcwd(), 'eval_results')
                os.makedirs(eval_dir, exist_ok=True)
                
                # Generate a safe filename
                condition = data.get('condition', 'unknown')
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"eval_{condition}_{timestamp}.json"
                filepath = os.path.join(eval_dir, filename)
                
                # Save data
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Respond
                response = {
                    "status": "success",
                    "message": "Evaluation data saved successfully",
                    "filename": filename,
                    "filepath": filepath
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"[SUCCESS] Evaluation saved to: {filepath}")
                
            except Exception as e:
                response = {
                    "status": "error",
                    "message": str(e)
                }
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"[ERROR] Failed to save evaluation: {e}")
        else:
            super().do_POST()

    def end_headers(self):
        # Ensure we send Access-Control headers for normal GET requests too
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    # Force current working directory to be the directory of server.py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving HTTP on port {PORT} (http://localhost:{PORT}/)...")
        print("CORS is enabled. POST endpoints are ready.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
