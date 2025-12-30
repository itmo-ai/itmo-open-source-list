# 🚀 ITMO Open Source List

![ITMO University](https://img.shields.io/badge/ITMO-University-1946BA?style=for-the-badge)
![Open Source](https://img.shields.io/badge/Open_Source-Love-EC0B43?style=for-the-badge&logo=opensource-initiatives&logoColor=white)
![Projects](https://img.shields.io/badge/Projects-Growing-00C853?style=for-the-badge)
![License](https://img.shields.io/github/license/itmo-ai/itmo-open-source-list?style=for-the-badge)

**Единый реестр открытых проектов лабораторий и команд Университета ИТМО.**

---

Здесь собирается информация обо всех Open Source разработках нашего университета. Данные из этого репозитория автоматически агрегируются и отображаются на портале [opensource.itmo.ru](https://opensource.itmo.ru).

## 🚀 Как добавить свой проект

1. Сделайте **Fork** этого репозитория.
2. Скопируйте шаблон `projects/_template.json` и назовите файл именем вашего проекта (например, `projects/my-cool-lib.json`).
3. Заполните поля в JSON-файле:
   - См. описание полей в [schema/project_schema.md](schema/project_schema.md).
   - **Важно:** `description.ru` обязательно, `lab` должен совпадать с ID из папки `labs/`.
4. Сделайте **Pull Request** в ветку `main`.
