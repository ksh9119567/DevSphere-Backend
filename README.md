# 🚀 DevSphere

> A Scalable Developer Publishing Ecosystem\
> Inspired by Medium, Hashnode & GitHub

DevSphere is a modern backend-driven platform designed to evolve from a
blogging application into a **full Developer Publishing Ecosystem**.\
It demonstrates advanced backend architecture, modular monolith design,
authentication systems, caching, background processing, and
production-ready infrastructure.

------------------------------------------------------------------------

# 🌍 Vision

DevSphere aims to become a **GitHub-lite + Medium-style ecosystem**
where developers can:

-   Publish blogs and technical articles
-   Share projects with versioning
-   Create organizations
-   Follow other developers
-   Discuss ideas
-   Generate API keys for integrations
-   Build on top of a public API

The system is intentionally designed for **future microservice
separation**, scalability, and production readiness.

------------------------------------------------------------------------

# 🏗 Architecture Overview

DevSphere follows a **Modular Domain-Oriented Monolith** architecture.

    app/
    ├── core/              # Security, config, redis, utilities
    ├── db/                # Database engine & session management
    ├── modules/           # Domain-based modules
    │   ├── auth/
    │   ├── users/
    │   ├── blogs/
    │   ├── comments/
    │   ├── tags/
    │   ├── follows/
    │   ├── organizations/
    │   ├── projects/
    │   ├── notifications/
    │   ├── analytics/
    │   └── api_keys/
    │
    ├── services/          # Cross-domain services (email, storage, cache)
    ├── events/            # Event-driven architecture layer (future-ready)
    ├── api/
    │   ├── v1/
    │   │   └── router.py
    │   └── router.py
    └── main.py

### Key Design Principles

-   Domain isolation per module
-   Clean service layer separation
-   Repository pattern ready
-   Versioned API routing (`/api/v1`)
-   Future microservice extraction capability

------------------------------------------------------------------------

# ⚙️ Tech Stack

  Layer                        Technology
  ---------------------------- --------------------------------
  Language                     Python 3.11
  Framework                    FastAPI (Async)
  Database                     PostgreSQL
  ORM                          SQLAlchemy (Async)
  Migrations                   Alembic
  Cache                        Redis
  Auth                         JWT (Access + Refresh Tokens)
  Containerization             Docker & Docker Compose
  Background Tasks (Planned)   Celery / Dramatiq
  Storage (Planned)            MinIO / AWS S3
  Search (Planned)             PostgreSQL FTS / ElasticSearch
  Realtime (Planned)           WebSockets + Redis Pub/Sub

------------------------------------------------------------------------

# 🔐 Authentication & Security

-   JWT-based authentication
-   Access & Refresh token flow
-   Refresh tokens stored in Redis
-   Role-Based Access Control (User & Admin)
-   Scoped API keys (planned)
-   Rate limiting (planned)
-   Production-ready token revocation

------------------------------------------------------------------------

# 🚀 Current Features

-   User registration & management
-   Blog CRUD with ownership protection
-   Admin-only controls
-   JWT login, refresh & logout
-   Dockerized multi-container environment
-   PostgreSQL + Redis integration
-   Alembic migration management

------------------------------------------------------------------------

# 📈 Roadmap

## Release 1.0 -- Core Publishing

-   Blog status (draft/published)
-   Slug system
-   Tags & categories
-   Nested comments
-   Follow system

## Release 1.5 -- Community Layer

-   Developer profiles
-   Likes & bookmarks
-   Personalized feed
-   Basic notifications

## Release 2.0 -- Organizations & Projects

-   Organization accounts
-   Role-based org permissions
-   Project publishing & versioning
-   Markdown documentation

## Release 2.5 -- Public API & API Keys

-   API key generation & rotation
-   Scoped access permissions
-   Rate limiting middleware
-   Public REST API

## Release 3.0 -- Background & Analytics

-   Celery integration
-   Email notifications
-   Engagement analytics
-   Event-driven architecture

## Release 4.0 -- Infrastructure & Scale

-   Redis caching layers
-   Search implementation
-   Object storage (S3 compatible)
-   Nginx reverse proxy
-   Observability (Prometheus + structured logging)

------------------------------------------------------------------------

# 🐳 Running Locally (Docker)

``` bash
docker compose build
docker compose up -d
```

Access API docs: 👉 http://localhost:8000/docs

------------------------------------------------------------------------

# 📦 API Structure

All APIs are versioned:

    /api/v1/auth/
    /api/v1/users/
    /api/v1/blogs/

Future versions (`v2`, `v3`) can coexist without breaking backward
compatibility.

------------------------------------------------------------------------

# 🧠 Engineering Goals

DevSphere is not just a product --- it's a backend engineering
laboratory to demonstrate:

-   Clean architecture
-   Scalable data modeling
-   Event-driven systems
-   Modular monolith design
-   Distributed system readiness
-   Production hardening practices

------------------------------------------------------------------------

# 🤝 Contributing

1.  Fork the repository
2.  Create a feature branch from `develop`
3.  Follow conventional commits
4.  Submit a Pull Request

Branch Strategy: - `main` → Stable releases - `develop` → Active
development

------------------------------------------------------------------------

# 📜 License

MIT License (To be added officially)

------------------------------------------------------------------------

# 👨‍💻 Author

Developed by **Kunal Sharma**\
Backend Engineer \| System Design Enthusiast

------------------------------------------------------------------------

# ⭐ Support

If you find DevSphere valuable, consider starring the repository ⭐
