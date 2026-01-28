# Personal Productivity Tracker - Learning Guide

## Table of Contents

1. [Prerequisites & Setup](#1-prerequisites--setup)
2. [Flask Fundamentals](#2-flask-fundamentals)
3. [PostgreSQL & SQLAlchemy](#3-postgresql--sqlalchemy)
4. [Project Structure](#4-project-structure)
5. [Phase 1: Authentication](#5-phase-1-authentication)
6. [Phase 2: Daily Survey & Habit Calendar](#6-phase-2-daily-survey--habit-calendar)
7. [Phase 3: Todo List](#7-phase-3-todo-list)
8. [Phase 4: External APIs](#8-phase-4-external-apis)
9. [Phase 5: Productivity Score & Polish](#9-phase-5-productivity-score--polish)
10. [Phase 6: AWS Deployment](#10-phase-6-aws-deployment)
11. [Phase 7: Testing](#11-phase-7-testing)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Prerequisites & Setup

### What you need installed
- **Python 3.10+**: Check with `python3 --version`
- **PostgreSQL**: Install via `brew install postgresql@15` on macOS, then `brew services start postgresql@15`
- **pip**: Comes with Python. Use it to install packages
- **Git**: You already have this

### Create your virtual environment

A virtual environment isolates your project's Python packages from your system Python. This prevents version conflicts between projects.

```bash
cd ~/Documents/Projects/personal_productivity_tracker
python3 -m venv venv
source venv/bin/activate   # Run this every time you open a new terminal
```

You'll know it's active when you see `(venv)` in your terminal prompt.

### Create requirements.txt

This file lists all packages your project depends on. Others (and AWS) use it to install the same packages.

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-JWT-Extended==4.6.0
Flask-Marshmallow==0.15.0
marshmallow-sqlalchemy==0.29.0
Flask-Caching==2.1.0
Flask-Limiter==3.5.0
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
cryptography==41.0.7
bcrypt==4.1.2
gunicorn==21.2.0
pytest==7.4.3
pytest-cov==4.1.0
```

Install them: `pip install -r requirements.txt`

### Create .gitignore

```
venv/
__pycache__/
*.pyc
.env
instance/
*.db
.DS_Store
```

### Create .env file

This stores secrets locally. **Never commit this file.**

```
FLASK_APP=wsgi.py
FLASK_ENV=development
SECRET_KEY=change-this-to-a-random-string
JWT_SECRET_KEY=change-this-too
DATABASE_URL=postgresql://localhost:5432/productivity_tracker
```

### Create your database

```bash
createdb productivity_tracker
```

Verify it exists: `psql -l | grep productivity`

### Where to learn more
- Python venv: https://docs.python.org/3/library/venv.html
- PostgreSQL basics: https://www.postgresqltutorial.com/
- pip & requirements.txt: https://pip.pypa.io/en/stable/user_guide/

---

## 2. Flask Fundamentals

### What is Flask?

Flask is a lightweight web framework. It handles HTTP requests and returns responses. Think of it as the middleman between a client (browser, mobile app, Postman) and your database.

### The simplest Flask app

Create `wsgi.py` to verify Flask works:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello, World!'}

if __name__ == '__main__':
    app.run(debug=True)
```

Run it: `flask run` or `python wsgi.py`
Visit: http://localhost:5000

### Key concepts you'll use

| Concept | What it does | Example |
|---------|-------------|---------|
| **Route** | Maps a URL to a function | `@app.route('/api/todo')` |
| **Blueprint** | Groups related routes into modules | Auth routes, Todo routes, etc. |
| **Request** | Access incoming data | `request.json`, `request.args` |
| **Response** | What you send back | `jsonify({'data': ...}), 200` |
| **App Factory** | A function that creates your app | `create_app()` pattern |

### Where to learn more
- Flask quickstart: https://flask.palletsprojects.com/en/3.0.x/quickstart/
- Flask tutorial (official): https://flask.palletsprojects.com/en/3.0.x/tutorial/
- Flask Mega-Tutorial by Miguel Grinberg: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world (highly recommended, covers most of what you need)

---

## 3. PostgreSQL & SQLAlchemy

### What is SQLAlchemy?

Instead of writing raw SQL like `SELECT * FROM users WHERE id = 1`, SQLAlchemy lets you write Python code:

```python
user = User.query.get(1)
```

It translates Python objects to database tables and back. This is called an **ORM** (Object-Relational Mapper).

### What is Flask-Migrate?

When you change a model (add a column, change a type), Flask-Migrate generates a migration script that updates your database schema without losing data. It uses Alembic under the hood.

```bash
flask db init      # One-time setup, creates migrations/ folder
flask db migrate -m "add user table"   # Generate migration from model changes
flask db upgrade   # Apply migration to database
flask db downgrade # Undo last migration
```

### Defining a model (example)

```python
from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

Each class = a database table. Each attribute = a column.

### Common SQLAlchemy operations

```python
# Create
user = User(email='test@test.com', username='testuser')
db.session.add(user)
db.session.commit()

# Read
user = User.query.filter_by(email='test@test.com').first()
users = User.query.all()

# Update
user.username = 'newname'
db.session.commit()

# Delete
db.session.delete(user)
db.session.commit()

# Filter with multiple conditions
todos = Todo.query.filter_by(user_id=1, status='pending').order_by(Todo.due_date).all()
```

### Where to learn more
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
- SQLAlchemy ORM tutorial: https://docs.sqlalchemy.org/en/20/orm/tutorial.html
- Flask-Migrate: https://flask-migrate.readthedocs.io/
- PostgreSQL with Python: https://www.psycopg.org/docs/

---

## 4. Project Structure

Create this folder structure. Every `__init__.py` can start as an empty file (it just tells Python "this folder is a package").

```
personal_productivity_tracker/
├── app/
│   ├── __init__.py              # App factory (create_app function)
│   ├── config.py                # Configuration classes
│   ├── extensions.py            # Initialize Flask extensions
│   ├── models/
│   │   ├── __init__.py          # Import all models here
│   │   ├── user.py
│   │   ├── daily_survey.py
│   │   ├── todo.py
│   │   ├── calendar_event.py
│   │   ├── github_commit.py
│   │   └── quote_cache.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── survey_schema.py
│   │   └── todo_schema.py
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── survey/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── habit/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── quote/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── productivity/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── planner/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── todo/
│   │       ├── __init__.py
│   │       └── routes.py
│   └── services/
│       ├── __init__.py
│       ├── quote_service.py
│       ├── github_service.py
│       ├── google_calendar_service.py
│       ├── habit_service.py
│       └── productivity_service.py
├── migrations/                   # Created by flask db init
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_auth.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── wsgi.py                      # Local entry point
└── README.md
```

### Why this structure?

- **App factory** (`app/__init__.py`): Lets you create multiple app instances (one for testing, one for production) with different configs
- **Blueprints**: Keep routes organized. Each feature gets its own folder so files stay small
- **Services**: Business logic separate from routes. Routes handle HTTP, services handle logic
- **Models**: One file per database table
- **Schemas**: Handle serialization (converting Python objects to JSON and validating input)

### Key starter files

**app/extensions.py** - Initialize extensions once, import everywhere:
```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
cors = CORS()
```

**app/config.py** - Configuration per environment:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost:5432/productivity_tracker_test'
```

**app/__init__.py** - App factory:
```python
from flask import Flask
from app.config import DevelopmentConfig
from app.extensions import db, migrate, jwt, ma, cors

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app)

    # Register blueprints
    from app.blueprints.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Add more blueprints as you build them

    return app
```

**wsgi.py** - Entry point:
```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

### Where to learn more
- Flask app factory pattern: https://flask.palletsprojects.com/en/3.0.x/patterns/appfactories/
- Flask blueprints: https://flask.palletsprojects.com/en/3.0.x/blueprints/

---

## 5. Phase 1: Authentication

### Goal
Users can register, log in, and receive a JWT token to access protected endpoints.

### What is JWT?

JSON Web Token. When a user logs in, you give them a token (a long encoded string). They send this token in every future request to prove who they are. No sessions, no cookies - the token contains the user's identity.

Flow:
1. User sends `POST /api/auth/login` with email + password
2. Server verifies credentials, returns `{access_token: "eyJ..."}`
3. User includes `Authorization: Bearer eyJ...` header in all future requests
4. Server decodes token to identify the user

### Steps

1. **Create the User model** (`app/models/user.py`)
   - Fields: id, email, username, password_hash, github_username, github_token, timezone, created_at
   - Use `bcrypt` to hash passwords (never store plain text passwords)
   - Add methods: `set_password(password)` and `check_password(password)`

2. **Create the auth blueprint** (`app/blueprints/auth/routes.py`)
   - `POST /register`: Validate input, check for duplicates, create user, return token
   - `POST /login`: Find user by email, verify password, return token
   - `POST /refresh`: Exchange refresh token for new access token
   - Use `@jwt_required()` decorator to protect routes

3. **Run your first migration**
   ```bash
   flask db init       # Creates migrations/ folder (one-time)
   flask db migrate -m "create users table"
   flask db upgrade    # Creates the table in PostgreSQL
   ```

4. **Test with Postman or curl**
   ```bash
   # Register
   curl -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","username":"testuser","password":"password123"}'

   # Login
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","password":"password123"}'
   ```

### Things to figure out
- How does `bcrypt.hashpw()` work? Try hashing a string in a Python shell first
- How does `@jwt_required()` know which user is making the request? Look at `get_jwt_identity()`
- What happens when a token expires? How do refresh tokens solve this?

### Where to learn more
- Flask-JWT-Extended: https://flask-jwt-extended.readthedocs.io/en/stable/
- Password hashing with bcrypt: https://pypi.org/project/bcrypt/
- JWT explained: https://jwt.io/introduction
- Miguel Grinberg's auth tutorial: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins

---

## 6. Phase 2: Daily Survey & Habit Calendar

### Goal
Users submit 1-3 daily wins. Exactly 3 wins = checkmark. Track streaks of consecutive checkmark days.

### Steps

1. **Create DailySurvey model** (`app/models/daily_survey.py`)
   - Fields: id, user_id (foreign key to users), survey_date, wins (JSON), win_count, has_checkmark
   - Add a unique constraint on (user_id, survey_date) so a user can only have one survey per day
   - `has_checkmark` is True when `win_count == 3`

2. **Create survey blueprint** (`app/blueprints/survey/routes.py`)
   - `POST /api/survey`: Accept `{wins: ["win1", "win2", "win3"], date: "2026-01-27"}`
     - Validate: wins must be a list of 1-3 non-empty strings
     - If survey exists for that date, update it. Otherwise create it
     - Set `has_checkmark = len(wins) == 3`
   - `GET /api/survey/today`: Return today's survey or 404
   - `GET /api/survey?start_date=...&end_date=...`: Return survey history

3. **Create habit service** (`app/services/habit_service.py`)
   - Query all dates with `has_checkmark=True` for a user
   - Calculate **current streak**: count consecutive days backward from today
   - Calculate **longest streak**: find the longest consecutive run in the data
   - Tip: Sort dates, iterate, check if each date is exactly 1 day after the previous

4. **Create habit blueprint** (`app/blueprints/habit/routes.py`)
   - `GET /api/habit/calendar?year=2026&month=1`: Return each day of the month with its checkmark status
   - `GET /api/habit/streaks`: Return current_streak and longest_streak

### Things to figure out
- How do JSON columns work in SQLAlchemy? (`db.Column(db.JSON)`)
- How do you add a unique constraint on multiple columns? Look at `__table_args__`
- How do you parse query parameters in Flask? (`request.args.get('year')`)
- How do you handle timezones? The user's date might differ from server time

### Where to learn more
- SQLAlchemy JSON columns: https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.JSON
- Unique constraints: https://docs.sqlalchemy.org/en/20/core/constraints.html
- Flask request object: https://flask.palletsprojects.com/en/3.0.x/api/#flask.Request

---

## 7. Phase 3: Todo List

### Goal
Full CRUD (Create, Read, Update, Delete) for todos with priority, due dates, categories, and tags.

### Steps

1. **Create Todo model** (`app/models/todo.py`)
   - Fields: id, user_id, title, description, priority (enum), status (enum), due_date, category, tags (JSON array), completed_at, created_at, updated_at
   - For enums, you can use `db.Enum('low', 'medium', 'high', 'urgent', name='priority_enum')`

2. **Create todo blueprint** (`app/blueprints/todo/routes.py`)

   **Create**: `POST /api/todo`
   ```json
   {
     "title": "Finish Flask tutorial",
     "priority": "high",
     "due_date": "2026-02-01T17:00:00",
     "category": "learning",
     "tags": ["flask", "python"]
   }
   ```

   **List with filters**: `GET /api/todo?status=pending&category=learning&sort=due_date&page=1&per_page=20`
   - Build the query dynamically based on which filters are provided
   - Add pagination with `.paginate(page=page, per_page=per_page)`

   **Update**: `PUT /api/todo/:id`
   - Only update fields that are provided in the request
   - When status changes to "completed", auto-set `completed_at = datetime.utcnow()`

   **Delete**: `DELETE /api/todo/:id`
   - Verify the todo belongs to the requesting user before deleting

3. **Important: Authorization**
   - Every endpoint must check that the todo belongs to the logged-in user
   - Use `get_jwt_identity()` to get user_id, then filter by it

### Things to figure out
- How to handle pagination in Flask-SQLAlchemy? Look at `.paginate()`
- How to build dynamic queries? (conditionally adding `.filter_by()`)
- How to handle partial updates? (only update fields present in the request body)
- What's the difference between `db.session.delete()` and soft deleting (setting a status)?

### Where to learn more
- Flask-SQLAlchemy pagination: https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/pagination/
- RESTful API design: https://restfulapi.net/
- Marshmallow validation: https://marshmallow.readthedocs.io/en/stable/

---

## 8. Phase 4: External APIs

This is where you learn to work with third-party APIs. Each one teaches different concepts.

### 8a. Daily Quote (ZenQuotes API)

**Simplest integration - start here.**

The ZenQuotes API requires no authentication. You just make a GET request.

```python
import requests

response = requests.get('https://zenquotes.io/api/today')
data = response.json()
# data = [{"q": "The quote text", "a": "Author Name", "h": "HTML"}]
```

**Steps:**
1. Create QuoteCache model (quote_date, quote_text, author)
2. Create quote_service.py:
   - Check if today's quote is in the database
   - If yes, return it (cache hit)
   - If no, fetch from ZenQuotes, save to DB, return it
   - If the API fails, return the most recent cached quote (fallback)
3. Create quote blueprint with `GET /api/quote/daily`

**Key concept: Caching.** You don't want to hit the API on every request. Fetch once per day, store it, serve from your database.

**Where to learn more:**
- Python requests library: https://requests.readthedocs.io/en/latest/
- ZenQuotes API: https://zenquotes.io/

### 8b. GitHub Commits

**Teaches: API authentication with tokens.**

GitHub's API uses a Personal Access Token (PAT) for authentication.

```python
import requests

headers = {'Authorization': f'token {github_token}'}
response = requests.get(
    f'https://api.github.com/users/{username}/events',
    headers=headers
)
events = response.json()
# Filter for PushEvents, count commits
```

**Steps:**
1. Create GitHubCommit model
2. Create github_service.py:
   - Accept user's GitHub username and PAT
   - Fetch events from GitHub API
   - Filter for `PushEvent` type (these contain commits)
   - Extract commit SHAs, dates, repo names
   - Store in GitHubCommit table (avoid duplicates using commit_sha)
3. Add `PUT /api/auth/profile` endpoint for users to save their GitHub token
   - **Encrypt the token** before storing (use `cryptography.fernet`)
4. Create productivity blueprint:
   - `POST /api/productivity/sync`: Trigger a fetch from GitHub
   - `GET /api/productivity/score?date=2026-01-27`: Count commits for that day

**Key concepts:**
- API authentication (Bearer tokens)
- Encrypting sensitive data at rest
- Handling pagination (GitHub returns 30 events per page)
- Rate limiting awareness (5000 requests/hour with token)

**Where to learn more:**
- GitHub REST API: https://docs.github.com/en/rest
- GitHub Events API: https://docs.github.com/en/rest/activity/events
- GitHub PAT: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- Fernet encryption: https://cryptography.io/en/latest/fernet/

### 8c. Google Calendar

**Most complex integration - save for last.**

Google Calendar uses OAuth 2.0, which is a multi-step authentication flow:

1. Your app redirects user to Google's login page
2. User grants permission
3. Google redirects back to your app with a code
4. Your app exchanges the code for access + refresh tokens
5. You use the access token to call Google Calendar API
6. When the access token expires, use the refresh token to get a new one

**Steps:**
1. Set up a Google Cloud project and enable Calendar API
   - Go to https://console.cloud.google.com
   - Create a project, enable Google Calendar API
   - Create OAuth 2.0 credentials (Web application)
   - Set redirect URI to `http://localhost:5000/api/auth/google/callback`

2. Create the OAuth flow in your auth blueprint:
   - `GET /api/auth/google`: Redirect user to Google's consent screen
   - `GET /api/auth/google/callback`: Handle the redirect, exchange code for tokens, store refresh token

3. Create google_calendar_service.py:
   - Use `google-api-python-client` to list events
   - Fetch events for a date range
   - Store in CalendarEvent table

4. Create planner blueprint:
   - `POST /api/planner/sync`: Fetch latest events from Google
   - `GET /api/planner/events?start_date=...&end_date=...`: Return stored events

**Key concepts:**
- OAuth 2.0 flow (authorization code grant)
- Storing and refreshing tokens
- Working with Google's Python client libraries

**Where to learn more:**
- Google Calendar API quickstart: https://developers.google.com/calendar/api/quickstart/python
- OAuth 2.0 explained: https://oauth.net/2/
- Google Auth Python library: https://google-auth.readthedocs.io/

---

## 9. Phase 5: Productivity Score & Polish

### Productivity Score

Start simple: score = number of commits that day. You can get fancier later.

```python
def calculate_daily_score(user_id, date):
    commit_count = GitHubCommit.query.filter_by(
        user_id=user_id,
        commit_date=date
    ).count()
    return {
        'date': date,
        'commit_count': commit_count,
        'score': commit_count  # Simple for now
    }
```

### Error Handling

Create a consistent error response format across your API:

```python
# In app/__init__.py
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

@app.errorhandler(400)
def bad_request(error):
    return {'error': str(error)}, 400

@app.errorhandler(500)
def server_error(error):
    return {'error': 'Internal server error'}, 500
```

### CORS

If a frontend will call your API from a different domain, you need CORS headers. Flask-CORS handles this:

```python
# In app/__init__.py
cors.init_app(app, resources={r"/api/*": {"origins": "*"}})  # Allow all in dev
```

### Rate Limiting

Prevent abuse by limiting how many requests a client can make:

```python
from flask_limiter import Limiter
limiter = Limiter(key_func=get_remote_address)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    ...
```

### Where to learn more
- Flask error handling: https://flask.palletsprojects.com/en/3.0.x/errorhandling/
- Flask-CORS: https://flask-cors.readthedocs.io/
- Flask-Limiter: https://flask-limiter.readthedocs.io/

---

## 10. Phase 6: AWS Deployment

### Overview

**Elastic Beanstalk (EB)** is AWS's managed platform. You upload your code, and it handles servers, load balancing, and scaling. It's the simplest way to deploy Flask to AWS.

**RDS** is AWS's managed PostgreSQL. It handles backups, updates, and availability.

### Prerequisites
- Create an AWS account: https://aws.amazon.com/
- Install AWS CLI: `brew install awscli`
- Install EB CLI: `brew install aws-elasticbeanstalk`
- Configure credentials: `aws configure` (enter your access key ID and secret)

### Step-by-step

1. **Create the EB entry point**

   Elastic Beanstalk looks for `application.py` by default:
   ```python
   # application.py
   from app import create_app
   from app.config import ProductionConfig

   application = create_app(ProductionConfig)

   if __name__ == '__main__':
       application.run()
   ```

   Note: the variable MUST be named `application`, not `app`. EB expects this.

2. **Create EB configuration files**

   ```
   .ebextensions/01_packages.config
   ```
   ```yaml
   packages:
     yum:
       postgresql-devel: []
   ```

   ```
   .platform/hooks/postdeploy/01_migrate.sh
   ```
   ```bash
   #!/bin/bash
   source /var/app/venv/*/bin/activate
   cd /var/app/current
   flask db upgrade
   ```
   Make it executable: `chmod +x .platform/hooks/postdeploy/01_migrate.sh`

3. **Create an RDS PostgreSQL instance**
   - Go to AWS Console > RDS > Create database
   - Choose PostgreSQL, Free tier (db.t3.micro)
   - Set a master username and password
   - Note the endpoint URL after creation

4. **Initialize and deploy**
   ```bash
   eb init -p python-3.11 productivity-tracker   # Initialize EB app
   eb create prod-env                              # Create environment
   ```

5. **Set environment variables**
   ```bash
   eb setenv \
     DATABASE_URL=postgresql://user:pass@your-rds-endpoint:5432/productivity_tracker \
     SECRET_KEY=your-production-secret \
     JWT_SECRET_KEY=your-jwt-secret \
     FLASK_ENV=production
   ```

6. **Deploy updates**
   ```bash
   eb deploy      # Deploy latest code
   eb logs        # View logs if something goes wrong
   eb open        # Open your app in browser
   eb status      # Check health
   ```

### Common pitfalls
- Forgetting to name the variable `application` in application.py
- Not setting environment variables before deploying
- RDS security group not allowing connections from EB instances (they must be in the same VPC or security group)
- Migration script not having execute permissions

### Cost awareness
- **Free tier** (first 12 months): 1 EB instance (t3.micro), 1 RDS instance (db.t3.micro), 20GB storage
- After free tier: ~$15-25/month for minimal usage
- **Set up billing alerts** at https://console.aws.amazon.com/billing/

### Where to learn more
- EB Python deployment: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html
- EB CLI: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html
- RDS PostgreSQL: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.PostgreSQL.html
- AWS Free Tier: https://aws.amazon.com/free/

---

## 11. Phase 7: Testing

### Why test?

Tests catch bugs before they reach production. They also let you refactor confidently - if tests pass, your changes didn't break anything.

### Setup

Create `tests/conftest.py` with shared fixtures:

```python
import pytest
from app import create_app
from app.config import TestingConfig
from app.extensions import db as _db

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
```

### Writing a test

```python
# tests/test_auth.py

def test_register(client):
    response = client.post('/api/auth/register', json={
        'email': 'test@test.com',
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'access_token' in data

def test_register_duplicate_email(client):
    # Register first user
    client.post('/api/auth/register', json={
        'email': 'test@test.com',
        'username': 'user1',
        'password': 'password123'
    })
    # Try duplicate
    response = client.post('/api/auth/register', json={
        'email': 'test@test.com',
        'username': 'user2',
        'password': 'password123'
    })
    assert response.status_code == 409  # Conflict
```

### Running tests

```bash
# Create test database first
createdb productivity_tracker_test

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app

# Run a specific test file
pytest tests/test_auth.py -v
```

### What to test
- **Happy path**: Does the feature work with valid input?
- **Validation**: Does it reject invalid input correctly?
- **Authorization**: Can users only access their own data?
- **Edge cases**: Empty lists, missing fields, duplicate entries
- **External APIs**: Mock them so tests don't depend on external services

### Mocking external APIs

```python
from unittest.mock import patch

def test_daily_quote(client, auth_header):
    mock_response = [{"q": "Test quote", "a": "Author"}]
    with patch('app.services.quote_service.requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200
        response = client.get('/api/quote/daily', headers=auth_header)
        assert response.status_code == 200
```

### Where to learn more
- Pytest: https://docs.pytest.org/en/stable/
- Flask testing: https://flask.palletsprojects.com/en/3.0.x/testing/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html

---

## 12. Troubleshooting

### Common issues and solutions

| Problem | Likely cause | Solution |
|---------|-------------|----------|
| `ModuleNotFoundError` | Virtual env not activated | Run `source venv/bin/activate` |
| `sqlalchemy.exc.OperationalError` | Database doesn't exist or wrong URL | Run `createdb productivity_tracker`, check .env |
| `flask db migrate` produces empty migration | Models not imported in `app/models/__init__.py` | Add `from app.models.user import User` etc. |
| `401 Unauthorized` on protected routes | Missing or expired JWT | Check `Authorization: Bearer <token>` header |
| `psycopg2` install fails | Missing PostgreSQL dev headers | Run `brew install postgresql@15` |
| CORS errors from frontend | Flask-CORS not configured | Add `cors.init_app(app)` in app factory |
| EB deployment fails | Missing application.py or wrong variable name | Must have `application = create_app()` |

### Useful debugging commands

```bash
# Check if Flask can find your app
flask routes                    # List all registered routes

# Check database state
flask shell                     # Open Python shell with app context
>>> from app.models.user import User
>>> User.query.all()

# Check PostgreSQL directly
psql productivity_tracker       # Open psql shell
\dt                             # List tables
\d users                        # Describe users table

# Check if your API is running
curl http://localhost:5000/api/auth/login -v
```

### When you're stuck

1. **Read the error message carefully.** Python tracebacks show the exact file and line number
2. **Check the Flask/library docs** for the specific feature you're using
3. **Search the error message** on Stack Overflow
4. **Use `flask shell`** to test things interactively
5. **Add print statements** or use `app.logger.info()` to trace what's happening
6. **Ask me** - describe what you expected vs what happened, and paste the error

---

## Recommended Learning Order

If this is your first time with these tools, work through them in this order:

1. **Python virtual environments** - 30 min reading
2. **Flask quickstart** - Build the "Hello World", understand routes and responses
3. **PostgreSQL basics** - Create a database, create a table manually, insert/query data
4. **SQLAlchemy tutorial** - Define a model, do CRUD operations in `flask shell`
5. **Flask-Migrate** - Create and run your first migration
6. **Flask blueprints** - Organize routes into modules
7. **JWT authentication** - Understand tokens, implement login
8. **requests library** - Make API calls to ZenQuotes
9. **GitHub API** - Authenticated API calls
10. **Google OAuth** - The most complex auth flow
11. **Testing with pytest** - Write tests for what you've built
12. **AWS Elastic Beanstalk** - Deploy everything

Each step builds on the previous one. Don't skip ahead - understanding the basics makes everything else easier.
