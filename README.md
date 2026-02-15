# FastAPI Todo & Admin Management API

A robust Task Management API built with FastAPI, featuring User Authentication (JWT), Role-Based Access Control (RBAC), and an Admin Dashboard for system-wide oversight.

## 🚀 Features

- **User Authentication**: Secure Login & Registration using OAuth2 and JWT tokens.
- **Role-Based Access**: 
  - **User**: Manage personal tasks (CRUD).
  - **Admin**: Approve new admins, view global statistics, and manage all tasks.
- **Admin Dashboard**: Real-time stats on users and tasks (TODO, IN_PROGRESS, DONE).
- **Task Management**: Full CRUD operations with search filters and pagination.
- **Database**: SQLite with SQLAlchemy ORM.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tioccolo.com/)
- **Database**: SQLite + [SQLAlchemy](https://www.sqlalchemy.org/)
- **Security**: Passlib (bcrypt), PyJWT
- **Validation**: Pydantic
