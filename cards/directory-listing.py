from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json
import requests
import time
from threading import Lock
from urllib.parse import unquote

stars_cache = {}
cache_lock = Lock()
CACHE_TTL = 3600
projects_cache = None
projects_cache_time = 0
CACHE_REFRESH = 30

def parse_github_repo(github_url):
    if 'github.com' not in github_url:
        return None
    try:
        parts = github_url.split('github.com/')[1].split('/')
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    except (IndexError, ValueError):
        pass
    return None

def get_github_stars(github_url):
    with cache_lock:
        cached = stars_cache.get(github_url)
        if cached and (time.time() - cached['timestamp']) < CACHE_TTL:
            return cached['stars']

    repo = parse_github_repo(github_url)
    if not repo:
        return 0

    try:
        api_url = f"https://api.github.com/repos/{repo}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            stars = response.json().get('stargazers_count', 0)
            with cache_lock:
                stars_cache[github_url] = {'stars': stars, 'timestamp': time.time()}
            return stars
    except requests.RequestException:
        pass
    return 0

def scan_projects():
    global projects_cache, projects_cache_time
    if projects_cache and (time.time() - projects_cache_time) < CACHE_REFRESH:
        return projects_cache

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    projects = []

    folder_path = os.path.join(BASE_DIR, 'labs')
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith('.json') and not file.startswith('_'):
                filepath = os.path.join(folder_path, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'example_projects' in data and data['example_projects']:
                            url = data.get('github_url') or data.get('github_org')
                            data['stars'] = get_github_stars(url) if url else 0
                            data['title'] = data.get('title') or data.get('name')
                            projects.append(data)
                except:
                    continue

    projects_cache = projects
    projects_cache_time = time.time()
    return projects

class ProjectHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = unquote(self.path)

        if parsed_path == '/api/projects':
            projects = scan_projects()
            self.send_json({'projects': projects})

        elif parsed_path.startswith('/api/lab/'):
            try:
                lab_id = parsed_path.split('/api/lab/')[1]
                projects_all = scan_projects()
                lab = next((p for p in projects_all if p['id'] == lab_id), None)
                if not lab:
                    self.send_response(404)
                    self.end_headers()
                    return
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                projects_folder = os.path.join(BASE_DIR, 'projects')
                lab_projects = []
                if os.path.exists(projects_folder):
                    for file in os.listdir(projects_folder):
                        if file.endswith('.json') and not file.startswith('_'):
                            filepath = os.path.join(projects_folder, file)
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    proj = json.load(f)
                                    if proj.get('lab') == lab_id:
                                        proj['stars'] = get_github_stars(proj.get('github_url'))
                                        lab_projects.append(proj)
                            except:
                                continue
                self.send_json({'lab': lab, 'projects': lab_projects})
            except (IndexError, ValueError):
                self.send_response(400)
                self.end_headers()
        else:
            super().do_GET()

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), ProjectHandler)
    server.serve_forever()
