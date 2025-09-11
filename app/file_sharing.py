import http.server
import socketserver
import threading
import socket
import os
import urllib.parse
from app.file_manager import load_decrypted_file
from app.models import SessionLocal, FileRecord

class FileShareHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, file_data=None, filename=None, **kwargs):
        self.file_data = file_data
        self.filename = filename
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/download':
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{self.filename}"')
            self.end_headers()
            self.wfile.write(self.file_data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')

def start_file_server(file_data, filename, port=0):
    """Start a local HTTP server to share the file. Returns the server URL."""
    handler = lambda *args, **kwargs: FileShareHandler(*args, file_data=file_data, filename=filename, **kwargs)
    with socketserver.TCPServer(("", port), handler) as httpd:
        ip = get_local_ip()
        url = f"http://{ip}:{httpd.server_address[1]}/download"
        print(f"Sharing file at: {url}")
        httpd.serve_forever()

def get_local_ip():
    """Get the local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def share_file(file_id, username):
    """Share a file by starting a local server."""
    db = SessionLocal()
    try:
        rec = db.query(FileRecord).filter(FileRecord.id == file_id, FileRecord.owner == username).first()
        if not rec:
            return None, "File not found"
        file_data = load_decrypted_file(rec.storage_name)
        if not file_data:
            return None, "Failed to load file"
        # Start server in a separate thread
        server_thread = threading.Thread(target=start_file_server, args=(file_data, rec.filename))
        server_thread.daemon = True
        server_thread.start()
        return f"File '{rec.filename}' is being shared. Check console for URL.", None
    except Exception as e:
        return None, str(e)
    finally:
        db.close()
