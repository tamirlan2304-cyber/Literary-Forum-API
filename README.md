# 📚 Literary Forum API

Pet-проект — REST API для литературного форума. Пользователи регистрируются, пишут посты о книгах и авторах, обсуждают их в комментариях, ставят лайки и ищут контент.

Проект строится как учебный — с акцентом на современный production-ready стек и правильную архитектуру.

> ⚠️ **Статус:** в активной разработке. Часть функциональности уже работает, часть лежит на уровне моделей/CRUD и ждёт обвязки эндпоинтами. Подробности — в разделе [Статус разработки](#статус-разработки).

## Стек

| | |
|---|---|
| **FastAPI** 0.135 | async веб-фреймворк, автодокументация через Swagger |
| **PostgreSQL 16** | основная БД |
| **SQLAlchemy 2.0** | асинхронный ORM с typed `Mapped[]` columns |
| **asyncpg** | асинхронный драйвер Postgres |
| **Alembic** | версионирование схемы БД через миграции |
| **Redis 7** | JWT blacklist при logout |
| **Pydantic v2** | валидация входящих данных и сериализация ответов |
| **python-jose + bcrypt** | JWT токены и хэширование паролей |
| **Docker Compose** | изолированное окружение: app, db, redis, pgadmin |
| **Python 3.13** | целевая версия в Dockerfile |

## Архитектура

Проект разбит на слои — каждый отвечает только за своё:

```
models/      → описание таблиц БД (SQLAlchemy ORM)
schemas/     → форматы данных на входе и выходе API (Pydantic)
crud/        → вся логика запросов к БД
api/         → HTTP эндпоинты, валидация прав, формирование ответа
core/        → конфиг, JWT, зависимости (get_db, get_redis, get_current_user)
db/          → DeclarativeBase, async engine, sessionmaker
```

Слои изолированы: эндпоинты не знают про SQL, crud не знает про HTTP.

## Модели и связи

```
User      ──< Post        (один пользователь — много постов)
Post      ──< Comment     (один пост — много комментариев)
User      ──< Comment     (один пользователь — много комментариев)
Post      >──< Tag        (многие ко многим через таблицу post_tags)
```

Все первичные ключи у `User`, `Post`, `Comment` — UUID; у `Tag` — обычный автоинкрементный `int`.
Каскадное удаление: удаляешь пост — его комментарии и связи с тегами удаляются тоже.

## Аутентификация

Используется JWT (Bearer токен). При логине выдаётся `access_token` с TTL 30 минут (`ACCESS_TOKEN_EXPIRE_MINUTES`). При logout токен кладётся в Redis blacklist с тем же TTL — сервер больше его не принимает. Все защищённые эндпоинты проверяют токен через dependency `get_current_user`, которая:

1. Достаёт Bearer токен из заголовка.
2. Проверяет, что токена нет в blacklist Redis.
3. Декодирует JWT, достаёт `sub` (user id).
4. Загружает пользователя из БД и отдаёт его в эндпоинт.

## Структура проекта

```
For_fastAPI/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py        # register, login, logout
│   │   │   └── posts.py       # list, get, create (в работе)
│   │   └── router.py
│   ├── core/
│   │   ├── config.py          # настройки через pydantic-settings + .env
│   │   ├── security.py        # JWT encode/decode, bcrypt
│   │   └── dependencies.py    # get_db, get_redis, get_current_user
│   ├── db/
│   │   ├── base.py            # DeclarativeBase + импорт всех моделей
│   │   └── session.py         # async engine, sessionmaker
│   ├── models/                # SQLAlchemy модели (User, Post, Comment, Tag)
│   ├── schemas/               # Pydantic схемы
│   ├── crud/                  # логика работы с БД (user, post, comment)
│   └── main.py
├── alembic/                   # миграции
├── .env                       # локальные секреты (не в git)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Быстрый старт

### Через Docker Compose (рекомендуется)

```bash
# 1. Создать .env по образцу:
#    POSTGRES_USER=...
#    POSTGRES_PASSWORD=...
#    POSTGRES_DB=...
#    DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/dbname
#    DATABASE_URL_LOCAL=postgresql+asyncpg://user:pass@localhost:5432/dbname
#    REDIS_URL=redis://redis:6379
#    SECRET_KEY=<любая длинная строка>

# 2. Поднять окружение
docker compose up --build

# 3. Применить миграции (в отдельном терминале)
docker compose exec app alembic upgrade head
```

После запуска доступно:

- **API** — http://localhost:8000
- **Swagger UI** — http://localhost:8000/docs
- **Health-check** — http://localhost:8000/health
- **pgAdmin** — http://localhost:5050 (`admin@admin.com` / `admin`)

### Локально (без Docker)

```bash
python -m venv .venv
source .venv/Scripts/activate     # Windows bash
pip install -r requirements.txt

# нужны запущенные локально Postgres и Redis
alembic upgrade head
uvicorn app.main:app --reload
```

## Эндпоинты (текущий срез)

Все маршруты префиксованы `/app/v1` (см. [app/main.py](app/main.py)).

### `/auth` — реализовано

| Метод | Путь | Описание |
|---|---|---|
| POST | `/auth/register` | регистрация по `username` + `email` + `password` |
| POST | `/auth/login` | выдача `access_token` |
| POST | `/auth/logout` | помещение токена в Redis blacklist |

### `/posts` — частично

CRUD-слой ([app/crud/post.py](app/crud/post.py)) уже умеет: получить пост, листинг с пагинацией и фильтром по тегу, создать пост (с автосозданием тегов), обновить, удалить, лайкнуть. На уровне эндпоинтов пока есть только `GET /posts`, `GET /posts/{id}`, `POST /posts`, и роутер ещё не подключён к `api_router`. Нужно: дописать update/delete/like, исправить опечатку `HTTPExeption`, подключить в [app/api/v1/router.py](app/api/v1/router.py).

### `/comments`, `/search` — не реализовано

Модель и CRUD комментариев готовы ([app/crud/comment.py](app/crud/comment.py)), эндпоинтов пока нет. Поиск (ILIKE / Postgres FTS) — впереди.

## Статус разработки

Реализовано:

- [x] Регистрация, логин, logout (JWT + Redis blacklist)
- [x] Модели User / Post / Comment / Tag со связями и каскадами
- [x] CRUD-слой для User, Post, Comment
- [x] Pydantic-схемы для входа/выхода
- [x] Alembic-миграции
- [x] Docker Compose: app + Postgres 16 + Redis 7 + pgAdmin
- [x] CORS middleware, health-check
- [x] Пагинация и фильтр по тегу в `crud.get_posts`

В работе:

- [ ] Эндпоинты `/posts`: подключить роутер, дописать update/delete/like, починить `HTTPExeption` → `HTTPException`
- [ ] Эндпоинты `/comments`: list по посту, create, update, delete, like
- [ ] Проверка прав (автор поста / комментария может редактировать только своё)
- [ ] Унификация `PostListResponse` (поле сейчас называется `posts`, эндпоинт ожидает `items`)

Дальше по дорожной карте:

- [ ] Поиск: ILIKE по заголовкам/тегам + PostgreSQL Full-text search
- [ ] Кэширование горячих списков через Redis
- [ ] Rate limiting
- [ ] Тесты (pytest + pytest-asyncio + httpx.AsyncClient)
- [ ] CI (GitHub Actions: lint + миграции + тесты)
- [ ] Refresh-токены (`REFRESH_TOKEN_EXPIRE_DAYS` уже зарезервирован в конфиге)
