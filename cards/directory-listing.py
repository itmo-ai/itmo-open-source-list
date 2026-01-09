from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json
import requests
import time
from threading import Lock

stars_cache = {}
cache_lock = Lock()
CACHE_TTL = 3600


def get_github_stars(github_url):
    with cache_lock:
        cached = stars_cache.get(github_url)
        if cached and (time.time() - cached['timestamp']) < CACHE_TTL:
            return cached['stars']

    try:
        if 'github.com' in github_url:
            parts = github_url.split('github.com/')[1].split('/')
            repo = f"{parts[0]}/{parts[1]}"
            api_url = f"https://api.github.com/repos/{repo}"
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                stars = response.json().get('stargazers_count', 0)
                with cache_lock:
                    stars_cache[github_url] = {'stars': stars, 'timestamp': time.time()}
                return stars
    except:
        pass
    return 0


class ProjectHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/projects':
            projects = []
            for folder in ['projects', 'labs']:
                folder_path = os.path.join(os.getcwd(), folder)
                if os.path.exists(folder_path):
                    for file in os.listdir(folder_path):
                        if file.endswith('.json'):
                            filepath = os.path.join(folder_path, file)
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    if data.get('id') and (data.get('title') or data.get('name')):
                                        url = data.get('github_url') or data.get('github_org')
                                        data['stars'] = get_github_stars(url) if url else 0
                                        data['title'] = data.get('title') or data.get('name')
                                        if not data.get('github_url') and data.get('github_org'):
                                            data['github_url'] = data['github_org']
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
