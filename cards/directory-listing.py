from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json


class ProjectHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/projects':
            projects = []
            for folder in ['../projects', '../labs']:
                if os.path.exists(folder):
                    for file in os.listdir(folder):
                        if file.endswith('.json'):
                            filepath = os.path.join(folder, file)
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    if data.get('id') and data.get('title'):
                                        projects.append(data)
                            except:
                                pass

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'projects': projects}, ensure_ascii=False).encode('utf-8'))
        else:
            super().do_GET()


if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), ProjectHandler)
    server.serve_forever()
