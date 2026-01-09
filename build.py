import datetime
import json
import requests
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com"
PROJECTS_DIR = 'projects'
LABS_DIR = 'labs'
OUTPUT_FILE = 'build/data.json'

class RepositoryBuilder:

    def __init__(self):
        """
        Инициализация с GitHub Token
        """
        git_token = TOKEN
        self.git_token = git_token
        self.headers = {}
        if git_token:
            self.headers["Authorization"] = "token " + git_token
        self.headers["Accept"] = "application/vnd.github.v3+json"

    def read_json_files(self, directory):
        """
        Читает все JSON файлы из директории
        """
        items = []
        if not Path(directory).exists():
            print(f'Директория {directory} не найдена')
            return []
        json_files = list(Path(directory).glob("*.json"))
        if not json_files:
            print('Файлы не найдены')
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    items.extend(data)
                else:
                    items.append(data)
            except json.JSONDecodeError as e:
                print(f'Ошибка парсинга {json_file}: {e}')
            except Exception as e:
                print(f'Ошибка чтения файла: {e}')
        return items

    def fetch_repo_data(self, owner, repo):
        """
        Получает данные репозитория из GitHub API
        """
        URL = f'{GITHUB_API_URL}/repos/{owner}/{repo}'
        try:
            response = requests.get(URL, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "updated_at": data.get("updated_at"),
                "license": data.get("license", {}).get("name") if data.get("license") else None,
                "language": data.get("language"),
                "description": data.get("description"),
                "url": data.get("html_url"),
                "fork": data.get("fork", False),
                "topics": data.get("topics", []),
            }
        except requests.exceptions.HTTPError as e:
            print(f'HTTP ошибка {e.response.status_code}')
            return {}
        except requests.exceptions.Timeout:
            print(f'Timeout')
            return {}
        except Exception as e:
            print(e)
            return {}

    def build(self):
        """Читает JSON файлы, извлекает owner/repo из github_url, запрашивает
        данные о репозиториях и сохраняет результат в data.json."""
        all_data = {
            "generated_at": datetime.datetime.now().isoformat(),
            "projects": [],
            "labs": [],
        }
        projects = self.read_json_files(PROJECTS_DIR)
        labs = self.read_json_files(LABS_DIR)
        print(len(projects))
        print(len(labs))
        for i, item in enumerate(projects, 1):
            if "github_url" in item:
                try:
                    github_url = item["github_url"]
                    path = github_url.replace("https://github.com/", '')
                    print(path)
                    owner, repo = path.split("/", 1)
                    github_data = self.fetch_repo_data(owner, repo)
                    if github_data:
                        item.update(github_data)
                    else:
                        print(f"Не удалось получить данные из GitHub")
                except Exception as e:
                    print(e)
            else:
                print(f"Нет поля 'github_url ' в файле")
            all_data["projects"].append(item)

        for i, item in enumerate(labs, 1):
            all_data["labs"].append(item)
        try:
            Path("build").mkdir(exist_ok=True)

            with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

if __name__ == "__main__":
    token = TOKEN
    if token:
        builder = RepositoryBuilder()
        builder.build()

