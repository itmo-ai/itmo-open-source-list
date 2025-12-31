import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PROJECTS_DIR = BASE_DIR / "projects"
LABS_DIR = BASE_DIR / "labs"

REQUIRED_PROJECT_FIELDS = ["id", "title", "description", "github_url", "lab", "area"]
REQUIRED_LAB_FIELDS = ["id", "name", "description"]


def load_json_files(directory):
    """Читает все .json файлы из папки и возвращает словарь {filename: data}."""
    files_data = {}
    read_errors = []

    if not directory.exists():
        return {}, [f"Директория не найдена: {directory}"]

    for file_path in directory.glob("*.json"):
        if file_path.name.startswith("_"):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                files_data[file_path.name] = data
        except Exception as e:
            read_errors.append(f"[{file_path.name}] Ошибка чтения/JSON: {e}")

    return files_data, read_errors


def validate_projects(projects, valid_lab_ids):
    """Проверяет проекты на наличие полей и корректность ссылок на лабы."""
    errors = []

    for filename, data in projects.items():
        missing = [field for field in REQUIRED_PROJECT_FIELDS if field not in data]
        if missing:
            errors.append(f"[{filename}] Отсутствуют обязательные поля: {', '.join(missing)}")

        lab_id = data.get("lab")
        if lab_id and lab_id not in valid_lab_ids:
            errors.append(f"[{filename}] Ссылка на несуществующую лабораторию: '{lab_id}'")

        if data.get("id") != filename.replace(".json", ""):
            errors.append(f"[{filename}] Поле 'id' ({data.get('id')}) не совпадает с именем файла")

    return errors


def validate_labs(labs):
    """Проверяет лабы на наличие полей."""
    errors = []
    for filename, data in labs.items():
        missing = [field for field in REQUIRED_LAB_FIELDS if field not in data]
        if missing:
            errors.append(f"[{filename}] Отсутствуют обязательные поля: {', '.join(missing)}")

        if data.get("id") != filename.replace(".json", ""):
            errors.append(f"[{filename}] Поле 'id' ({data.get('id')}) не совпадает с именем файла")

    return errors


def main():
    print("Запуск валидации данных...")

    labs, labs_read_errors = load_json_files(LABS_DIR)
    projects, projects_read_errors = load_json_files(PROJECTS_DIR)

    if not labs and not labs_read_errors:
        print("Нет файлов лабораторий!")
    if not projects and not projects_read_errors:
        print("Нет файлов проектов!")

    valid_lab_ids = {data["id"] for data in labs.values() if "id" in data}

    lab_logic_errors = validate_labs(labs)
    project_logic_errors = validate_projects(projects, valid_lab_ids)

    all_errors = (
        labs_read_errors +
        projects_read_errors +
        lab_logic_errors +
        project_logic_errors
    )

    if all_errors:
        print(f"\nНайдено {len(all_errors)} ошибок:")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nВсе данные корректны!")
        print(f"   Лабораторий: {len(labs)}")
        print(f"   Проектов: {len(projects)}")


if __name__ == "__main__":
    main()
