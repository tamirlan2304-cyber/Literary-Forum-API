# 📚 Literary Forum API

Pet-проект — REST API для литературного форума. Пользователи регистрируются, пишут посты о книгах и авторах, обсуждают их в комментариях, ставят лайки и ищут контент.

Проект строится как учебный — с акцентом на современный production-ready стек и правильную архитектуру.

## Стек

| | |
|---|---|
| **FastAPI** | async веб-фреймворк, автодокументация через Swagger |
| **PostgreSQL 16** | основная БД |
| **SQLAlchemy 2.0** | асинхронный ORM с typed `Mapped[]` columns |
| **Alembic** | версионирование схемы БД через миграции |
| **Redis 7** | JWT blacklist при logout |
| **Pydantic v2** | валидация входящих данных и сериализация ответов |
| **python-jose + passlib** | JWT токены и bcrypt хэширование паролей |
| **Docker Compose** | изолированное окружение: app, db, redis, pgadmin |

## Архитектура

Проект разбит на слои — каждый отвечает только за своё:

```
models/      → описание таблиц БД (SQLAlchemy ORM)
schemas/     → форматы данных на входе и выходе API (Pydantic)
crud/        → вся логика запросов к БД
api/         → HTTP эндпоинты, валидация прав, формирование ответа
core/        → конфиг, JWT, зависимости (get_db, get_current_user)
```

Слои изолированы: эндпоинты не знают про SQL, crud не знает про HTTP.

## Модели и связи

```
User      ──< Post        (один пользователь — много постов)
Post      ──< Comment     (один пост — много комментариев)
User      ──< Comment     (один пользователь — много комментариев)
Post      >──< Tag        (многие ко многим через таблицу post_tags)
```

Все первичные ключи — UUID. Каскадное удаление: удаляешь пост — его комментарии удаляются тоже.

## Аутентификация

Используется JWT (Bearer токен). При логине выдаётся `access_token` с TTL 30 минут. При logout токен кладётся в Redis blacklist с тем же TTL — сервер больше его не принимает. Все защищённые эндпоинты проверяют токен через dependency `get_current_user`.

## Структура проекта

```
literary_forum/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/      # auth, posts, comments, search
│   │   └── router.py
│   ├── core/
│   │   ├── config.py       # настройки через pydantic-settings + .env
│   │   ├── security.py     # JWT encode/decode, bcrypt
│   │   └── dependencies.py # get_db, get_redis, get_current_user
│   ├── db/
│   │   ├── base.py         # DeclarativeBase + импорт всех моделей
│   │   └── session.py      # async engine, sessionmaker
│   ├── models/             # SQLAlchemy модели
│   ├── schemas/            # Pydantic схемы
│   ├── crud/               # логика работы с БД
│   └── main.py
├── alembic/                # миграции
├── .env.example
├── docker-compose.yml
└── Dockerfile
```

## Статус разработки

- [x] Регистрация и авторизация (JWT + Redis blacklist)
- [x] Посты — CRUD, лайки, теги
- [x] Комментарии — CRUD
- [x] Поиск — ILIKE по заголовкам/тегам + PostgreSQL Full-text search
- [x] Пагинация
- [x] Docker Compose окружение
- [x] Миграции (Alembic)
- [ ] Тесты (pytest + pytest-asyncio)
- [ ] Кэширование списков через Redis
- [ ] Rate limiting