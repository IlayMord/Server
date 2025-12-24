import http.server
import socketserver

PORT = 80
FILE_PATH = "/home/ubuntu/Server/ip.txt"

class SingleFileHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            with open(FILE_PATH, "rb") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        except FileNotFoundError:
            self.send_error(404, "File not found")

with socketserver.TCPServer(("", PORT), SingleFileHandler) as httpd:
    print(f"Serving {FILE_PATH} on port {PORT}")
    httpd.serve_forever()
