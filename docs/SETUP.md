# 🛠️ Devsphere - Setup Guide (Windows, Linux, macOS)

This guide explains how to set up and run **Devsphere** on any operating system.

---

## ✅ Prerequisites

Ensure the following are installed:

| Requirement | Version | Docs |
|--------------|----------|----------------|
| Python | 3.11+ | https://www.python.org/downloads/ |
| Docker | latest | https://docs.docker.com/get-docker/ |
| Docker Compose | latest | Included with Docker Desktop |
| Git | latest | https://git-scm.com/downloads |

---

## 📂 Clone the Repository

```bash
git clone <REPO_URL>
cd devsphere
```

> Replace `<REPO_URL>` with your repository link

---

## 🧰 Environment Setup

Create a `.env` file in the project root with required variables:

```
DATABASE_URL=postgresql+asyncpg://devsphere_user:devsphere1234@db:5432/devsphere_db
POSTGRES_USER=devsphere_user
POSTGRES_PASSWORD=devsphere1234
POSTGRES_DB=devsphere_db

REDIS_URL=redis://redis:6379/0

SECRET_KEY=BLOG_APP_SECRET_KEY
REFRESH_SECRET_KEY=BLOG_APP_REFRESH_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email OTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
OTP_EXPIRY_MINUTES=10

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

---

## 🐳 Run with Docker (Recommended for all OS)

### Build and start containers

```bash
docker compose build --no-cache
docker compose up -d
```

### Check container status

```bash
docker ps
```

### Stop containers

```bash
docker compose down
```

> To remove volumes too: `docker compose down -v`

---

## 💻 Local Setup (without Docker)

> Only recommended for development or debugging

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate        # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start PostgreSQL & Redis manually

- Install PostgreSQL & Redis based on your OS
- Update `.env` with local host credentials

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the backend

```bash
uvicorn app.main:app --reload
```

---

## 🔍 Useful Docker Commands

| Task | Command |
|--------|------------|
| View logs | `docker logs -f devsphere_app` |
| Enter container shell | `docker exec -it devsphere_app bash` |
| Access PostgreSQL | `docker exec -it devsphere_postgres psql -U devsphere_user -d devsphere_db` |
| Access Redis | `docker exec -it devsphere_redis redis-cli` |
| View Celery logs | `docker logs -f devsphere_celery` |
| Inspect Redis tokens | `docker exec -it devsphere_app python scripts/inspect_redis_data.py` |
| Delete all tokens | `docker exec -it devsphere_app python scripts/inspect_redis_data.py delete` |

---

## 🎯 Next Steps

- Read `docs/FEATURES.md` for comprehensive feature documentation
- Read `docs/AUTHENTICATION_FLOW.md` for JWT and email OTP authentication
- Read `docs/REDIS_TOKEN_INSPECTION.md` for token inspection and debugging
- Read `docs/REDIS_CACHING.md` for caching layer documentation
- Read `docs/ACTIVITY_TRACKING.md` for activity logging
- Set up development branches
- Start implementing Version 1.0 features

---

Happy coding! 🚀
