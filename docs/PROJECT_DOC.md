# Personal Productivity Tracker — Project Documentation

---

## Expected Product

- Backend REST API that unifies personal productivity data into a single system
- Flask-based API server with the following features:
    - **Authentication System**
        - User registration and login with JWT tokens
        - Password hashing with bcrypt
        - OAuth 2.0 integration for Google Calendar
    - **Daily Survey & Habit Calendar**
        - Submit 1–3 daily wins
        - Track checkmark streaks (3 wins = checkmark)
        - Monthly calendar view and streak statistics
    - **Todo List Management**
        - Full CRUD with priority, status, categories, and tags
        - Filtering, sorting, and pagination
        - Auto-completion tracking
    - **External API Integrations**
        - Daily motivational quote (ZenQuotes API)
        - GitHub commit tracking (GitHub REST API)
        - Google Calendar event sync (Google Calendar API)
    - **Productivity Score**
        - Aggregate daily activity into a score
- Deployed to AWS with:
    - Elastic Beanstalk (application server)
    - RDS PostgreSQL (managed database)
- Test suite with pytest and code coverage

**Dataset / Data Sources:**
- ZenQuotes API (https://zenquotes.io/) — unauthenticated, daily quote
- GitHub REST API (https://docs.github.com/en/rest) — authenticated via Personal Access Token
- Google Calendar API (https://developers.google.com/calendar) — authenticated via OAuth 2.0

---

## 1. System Architecture

### A. Data Ingestion

Define how external data enters the system.

- **What data is pulled?**
    - GitHub: push events, commit SHAs, dates, repository names
    - Google Calendar: event summaries, start/end times
    - ZenQuotes: daily quote text and author
- **How is data fetched?**
    - On-demand: user triggers sync via `POST /api/productivity/sync` or `POST /api/planner/sync`
    - Cached: daily quote fetched once per day, served from database on subsequent requests
- **How are API failures handled?**
    - ZenQuotes: fallback to most recent cached quote
    - GitHub: rate limit awareness (5,000 requests/hour with token), duplicate prevention via commit SHA
    - Google Calendar: token refresh on expiry using stored refresh token

### B. Data Storage

Define what data is stored and how it is structured.

- **Database:** PostgreSQL 15 (local in development, AWS RDS in production)
- **ORM:** Flask-SQLAlchemy
- **Migrations:** Flask-Migrate (Alembic)
- **Persisted data:**
    - User accounts and encrypted credentials
    - Daily survey entries with wins and checkmark status
    - Todo items with metadata (priority, status, category, tags, timestamps)
    - GitHub commits (SHA, date, repo, message)
    - Google Calendar events (event ID, summary, start, end)
    - Cached daily quotes
- **Computed dynamically:**
    - Streak calculations (current and longest)
    - Productivity scores
    - Calendar views

**Data Models:**

| Model | Key Fields |
|-------|-----------|
| User | email, username, password_hash, github_username, github_token (encrypted), google_credentials |
| DailySurvey | user_id, survey_date, wins (JSON), win_count, has_checkmark |
| Todo | user_id, title, description, priority (enum), status (enum), due_date, category, tags (JSON), completed_at |
| GitHubCommit | user_id, commit_sha (unique), message, repo_name, commit_date |
| CalendarEvent | user_id, google_event_id, summary, start_time, end_time |
| QuoteCache | quote_date, quote_text, author |

### C. Application Layer

Define how business logic is organized.

- **Architecture pattern:** Layered (Routes → Services → Models)
- **Blueprints (HTTP routing):** Auth, Survey, Habit, Todo, Quote, Productivity, Planner
- **Services (business logic):**
    - HabitService — streak calculation, calendar generation
    - QuoteService — fetch, cache, and fallback logic
    - GitHubService — authenticated API calls, commit extraction, token encryption
    - GoogleCalendarService — OAuth 2.0 flow, token refresh, event sync
    - ProductivityService — score aggregation
- **Schemas (validation & serialization):** Marshmallow schemas for User, Survey, Todo

Services are independent modules that access shared data through SQLAlchemy models. Each blueprint handles HTTP concerns only and delegates logic to its corresponding service.

### D. Backend Interface

Define how the system is exposed to consumers.

- **Interface type:** REST API (JSON over HTTP)
- **Authentication:** JWT tokens (access + refresh)
- **Protected routes:** `@jwt_required()` decorator on all endpoints except register, login, and daily quote

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | User registration |
| POST | /api/auth/login | User login, returns JWT |
| POST | /api/auth/refresh | Refresh access token |
| PUT | /api/auth/profile | Save GitHub/Google credentials |
| GET | /api/auth/google | Initiate Google OAuth |
| GET | /api/auth/google/callback | OAuth callback handler |
| POST | /api/survey | Submit daily wins |
| GET | /api/survey/today | Get today's survey |
| GET | /api/survey | Survey history (with date filters) |
| GET | /api/habit/calendar | Monthly calendar view |
| GET | /api/habit/streaks | Current and longest streaks |
| POST | /api/todo | Create todo |
| GET | /api/todo | List todos (with filters, pagination, sorting) |
| PUT | /api/todo/:id | Update todo |
| DELETE | /api/todo/:id | Delete todo |
| GET | /api/quote/daily | Get daily motivational quote |
| POST | /api/productivity/sync | Sync GitHub commits |
| GET | /api/productivity/score | Get daily productivity score |
| POST | /api/planner/sync | Sync Google Calendar events |
| GET | /api/planner/events | List calendar events (with date filters) |

- **Cross-cutting concerns:**
    - CORS enabled for all `/api/*` routes (Flask-CORS)
    - Rate limiting on sensitive endpoints like login (Flask-Limiter)
    - Caching for repeated queries (Flask-Caching)

### E. Deployment & Updates

Define how the system runs in production.

- **Platform:** AWS Elastic Beanstalk (manages EC2, load balancing, scaling)
- **Database:** AWS RDS PostgreSQL (managed backups, availability)
- **WSGI server:** Gunicorn
- **Migrations:** Automated via post-deploy hook (`.platform/hooks/postdeploy/01_migrate.sh`)
- **Secrets management:** Environment variables set via `eb setenv` (DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY)
- **Local development:** Flask dev server with `.env` file (python-dotenv)
- **Configuration:** App factory pattern with separate config classes (Development, Production, Testing)

---

## 2. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | Flask 3.0.0 | HTTP routing, request handling |
| ORM | Flask-SQLAlchemy 3.1.1 | Database abstraction |
| Migrations | Flask-Migrate 4.0.5 | Schema versioning |
| Auth | Flask-JWT-Extended 4.6.0 | Token-based authentication |
| Serialization | Flask-Marshmallow 0.15.0 | Input validation, JSON serialization |
| Database | PostgreSQL 15 | Relational data storage |
| DB Adapter | psycopg2-binary 2.9.10 | Python-PostgreSQL connection |
| Password Hashing | bcrypt 4.1.2 | Secure password storage |
| Encryption | cryptography 41.0.7 | Encrypt API tokens at rest (Fernet) |
| HTTP Client | requests 2.31.0 | External API calls |
| CORS | Flask-CORS 4.0.0 | Cross-origin request support |
| Rate Limiting | Flask-Limiter 3.5.0 | Abuse prevention |
| Caching | Flask-Caching 2.1.0 | Response caching |
| Env Config | python-dotenv 1.0.0 | Load .env variables |
| WSGI Server | Gunicorn 21.2.0 | Production server |
| Testing | pytest 7.4.3, pytest-cov 4.1.0 | Unit tests, coverage |
| Deployment | AWS Elastic Beanstalk + RDS | Managed hosting |

---

## 3. Development Phases

| Phase | Feature | Key Concepts |
|-------|---------|-------------|
| 1 | Authentication | JWT, bcrypt, password hashing, protected routes |
| 2 | Daily Survey & Habit Calendar | JSON columns, unique constraints, streak algorithms |
| 3 | Todo List | CRUD, pagination, dynamic filtering, enums |
| 4a | Daily Quote (ZenQuotes) | Basic API calls, caching strategy, fallback logic |
| 4b | GitHub Commits | Bearer token auth, Fernet encryption, pagination |
| 4c | Google Calendar | OAuth 2.0 authorization code flow, token refresh |
| 5 | Productivity Score & Polish | Score aggregation, error handling, CORS, rate limiting |
| 6 | AWS Deployment | Elastic Beanstalk, RDS, environment variables, migration hooks |
| 7 | Testing | pytest fixtures, test isolation, mocking external APIs |

---

## Reference Material

- Flask Documentation: https://flask.palletsprojects.com/en/3.0.x/
- Flask Mega-Tutorial: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
- Flask-JWT-Extended: https://flask-jwt-extended.readthedocs.io/
- Flask-Migrate: https://flask-migrate.readthedocs.io/
- Marshmallow: https://marshmallow.readthedocs.io/
- PostgreSQL Tutorial: https://www.postgresqltutorial.com/
- GitHub REST API: https://docs.github.com/en/rest
- Google Calendar API: https://developers.google.com/calendar/api/quickstart/python
- OAuth 2.0: https://oauth.net/2/
- ZenQuotes API: https://zenquotes.io/
- Fernet Encryption: https://cryptography.io/en/latest/fernet/
- AWS Elastic Beanstalk (Python): https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html
- AWS Free Tier: https://aws.amazon.com/free/
- pytest: https://docs.pytest.org/en/stable/
