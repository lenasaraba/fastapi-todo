# FastAPI Todo & Admin Management API

A robust Task Management API built with FastAPI, featuring **Service-Layer architecture**, User Authentication (JWT), Role-Based Access Control (RBAC), and an Admin Dashboard for system-wide oversight.

## 🚀 Features

- **User Authentication**: Secure Login & Registration using OAuth2 and JWT tokens.
- **Service Layer Architecture**: Business logic is decoupled from routers into dedicated service classes for better maintainability.
- **Role-Based Access**: 
  - **User**: Manage personal tasks (CRUD).
  - **Admin**: Approve/Archive users, view global statistics, and manage all tasks.
- **Admin Dashboard**: Real-time SQL-aggregated stats on users and tasks (TODO, IN_PROGRESS, DONE).
- **Task Management**: Full CRUD operations with search filters and pagination.
- **Cloud-Ready Config**: Secure environment management using Pydantic Settings and `.env`.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tioccolo.com/)
- **Database**: **PostgreSQL** (Dockerized) + [SQLAlchemy](https://www.sqlalchemy.org/)
- **Security**: Passlib (bcrypt), PyJWT
- **Validation**: Pydantic Settings

## 📂 Project Structure

- `app/services`: Business logic and database transactions.
- `app/routers`: API endpoints.
- `app/models`: SQLAlchemy models.
- `app/core`: Centralized configuration and security settings.
