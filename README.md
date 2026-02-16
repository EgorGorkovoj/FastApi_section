# SPIMEX Bulletin Async Parser (FastAPI)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-%23F47216.svg?style=for-the-badge&logo=BeautifulSoup&logoColor=white)
![FastAPI](https://img.shields.io/badge/fastapi-%2300C7B7.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/uvicorn-%23007ACC.svg?style=for-the-badge&logo=python&logoColor=white)
![Pydantic](https://img.shields.io/badge/pydantic-%2300A1E0.svg?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23F47216.svg?style=for-the-badge&logo=python&logoColor=white)
![Alembic](https://img.shields.io/badge/alembic-%230071C5.svg?style=for-the-badge&logo=alembic&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![ReDoc](https://img.shields.io/badge/redoc-%23CB3837.svg?style=for-the-badge&logo=redoc&logoColor=white)
![Swagger](https://img.shields.io/badge/swagger-%2385EA2D.svg?style=for-the-badge&logo=swagger&logoColor=black)
![Redis](https://img.shields.io/badge/redis-%23CB3837.svg?style=for-the-badge&logo=redis&logoColor=black)

FastAPI приложение для парсинга бюллетеней Санкт-Петербургской международной товарно-сырьевой биржи (СПбМТСБ).
Проект автоматически скачивает XLS-файлы, извлекает таблицу *«Единица измерения: Метрическая тонна»*, конвертирует данные в структурированный формат и сохраняет их в PostgreSQL.

---

## 📌 Возможности

- REST API на FastAPI для работы с данными СПбМТСБ.
- Асинхронная загрузка бюллетеней с сайта биржи.
- Парсинг XLS (двухуровневых заголовков).
- Сохранение данных в PostgreSQL.

---

## 📦 Требования

- Python 3.12
- PostgreSQL 17 (либо Docker)
- Redis (для кэширования)
- pip / venv


# 🚀 Поднятие контейнера приложения, БД PostgreSQL и REDIS в Docker

## 1. Создать файл .env в корне проекта.

Пример содержания файла .env находится в корне проекта в файле .env.example.

## 2. Из корневой директории проекта выполнить команду:
```bash
docker compose -f docker-compose.yml up -d
```

# Запуск тестов
## 1. Из корневой директории проекта выполнить команду:
```bash
pytest
```

# Логирование

Все события пишутся в:
```
logs/app.log
```
## 👨‍💻 Автор
- [Егор Горьковой](https://github.com/EgorGorkovoj)
