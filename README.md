# Django Custom Authentication and Authorization API

[![Django CI](https://github.com/USERNAME/REPOSITORY/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/REPOSITORY/actions/workflows/ci.yml)

This project is a custom authentication and authorization (RBAC) API built with Django and Django Rest Framework. It provides a flexible, role-based access control system at the database level, designed to be modular and secure.

*(Этот проект был подготовлен в качестве демонстрации. Вся документация на английском, но комментарии в коде на русском языке для лучшего понимания внутренней логики.)*

## Access Control Architecture

The access control system is based on a Role-Based Access Control (RBAC) model. This design was chosen for its flexibility and scalability, allowing for granular control over permissions.

The schema consists of five core models:
- **`Resource`**: Represents an entity being accessed (e.g., "SecretDocument", "UserProfile").
- **`Action`**: Represents an operation that can be performed (e.g., "read", "write", "delete").
- **`Permission`**: A combination of a `Resource` and an `Action` (e.g., the permission to "read SecretDocument").
- **`Role`**: A collection of `Permission`s that defines a set of capabilities (e.g., "Admin", "DocumentViewer").
- **`CustomUser`**: The user model, which can be assigned one or more `Role`s, thereby inheriting their permissions.

A user's ability to perform an action is determined by checking if any of their assigned roles contain the required permission. Superusers are granted all permissions implicitly.

## Getting Started

The application is fully containerized using Docker and Docker Compose for easy setup and deployment.

**Prerequisites:**
- Docker
- Docker Compose

### 1. Clone the Repository
First, clone the project to your local machine. Remember to replace `USERNAME/REPOSITORY` with your actual GitHub username and repository name to make the CI badge work.

### 2. Create Environment File
The project uses a `.env` file for configuration. Create one by copying the example file:
```bash
cp .env.example .env
```
The default values in `.env.example` are suitable for local development. You should change `SECRET_KEY` for a production environment.

### 3. Build and Run
Execute the following command from the project root directory:
```bash
docker-compose up --build -d
```
This command will:
- Build the Docker images for the Django application and PostgreSQL.
- Start the services in detached mode.
- Automatically apply database migrations.
- Seed the database with initial data (roles, permissions, and an admin user) via the `seed_db` management command.

The API will then be available at `http://localhost:8000`.

### Initial Admin User
The database seeding process creates a superuser with the following credentials:
- **Email**: `admin@example.com`
- **Password**: `adminpassword`

## API Documentation
The API is self-documented using `drf-yasg`, which provides Swagger and ReDoc interfaces.
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`

## Running Tests
The project includes a comprehensive test suite. To run the tests, execute the following command:
```bash
docker-compose exec web python src/manage.py test core
```
This runs the tests inside the running `web` container, ensuring the test environment is identical to the application's runtime. The CI pipeline configured in `.github/workflows/ci.yml` also runs these tests automatically on every push and pull request to the `main` branch.

## API Usage Examples
The following `cURL` commands demonstrate how to interact with the API.

#### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/register/ \
-H "Content-Type: application/json" \
-d '{"email": "newuser@example.com", "password": "strongpassword", "password2": "strongpassword"}'
```

#### 2. Log In
Returns `access` and `refresh` tokens.
```bash
curl -X POST http://localhost:8000/api/login/ \
-H "Content-Type: application/json" \
-d '{"email": "newuser@example.com", "password": "strongpassword"}'
```

#### 3. Access a Protected Resource
Use the `access` token from the login response.
```bash
ACCESS_TOKEN="your_access_token_here"
curl -X GET http://localhost:8000/api/secret/ \
-H "Authorization: Bearer $ACCESS_TOKEN"
```

#### 4. Log Out
This blacklists the refresh token. The request must be authenticated.
```bash
ACCESS_TOKEN="your_access_token_here"
REFRESH_TOKEN="your_refresh_token_here"
curl -X POST http://localhost:8000/api/logout/ \
-H "Authorization: Bearer $ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{"refresh": "'$REFRESH_TOKEN'"}'
```

#### 5. Manage Roles (Admin Only)
Log in with the pre-seeded admin user to get an admin access token.
```bash
ADMIN_ACCESS_TOKEN="your_admin_access_token_here"
curl -X GET http://localhost:8000/api/admin/roles/ \
-H "Authorization: Bearer $ADMIN_ACCESS_TOKEN"
```
