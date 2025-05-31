## Overview
Digital-i is a full-stack web application built with Angular frontend and Django backend, containerized using Docker for easy deployment and scalability.

## Architecture

### Frontend
- **Framework**: Angular v17 with PrimeNG v17
- **Theme**: PrimeNG v17 themes with Sakai Angular template
- **Location**: sakai-ng
- **Port**: 8080 (containerized), 4200 (development)

### Backend
- **Framework**: Django with Django REST Framework
- **Database**: PostgreSQL
- **Location**: backend
- **Port**: 8000

### Database
- **Type**: PostgreSQL 
- **Port**: 5432
- **Credentials**: postgres/password123

## Project Structure

```
Digital-i/
├── frontend/sakai-ng/          # Angular application
├── backend/                    # Django application
├── deployment/                 # Docker deployment configs
├── docker/                     # Docker-related files
├── Documents/                  # Project documentation & backups
└── scripts/                    # Utility scripts
```

## Development Setup

### Prerequisites
- Node.js & npm
- Python 3.x
- Docker & Docker Compose
- Angular CLI

### Frontend Development
```bash
cd frontend/sakai-ng
npm install
ng serve
```
Access at: `http://localhost:4200`

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```
Access at: `http://localhost:8000`

## Docker Deployment

### Quick Update Command
```bash
docker compose pull django && docker compose down && docker compose up -d
```

### Individual Container Management

#### Frontend
```bash
# Build & Push
docker build -t frontend_digitali:1 . && \
docker tag frontend_digitali:1 karth1k/frontend_digitali && \
docker push karth1k/frontend_digitali

# Run
docker run -d -p 8080:80 --name frontend --restart always karth1k/frontend_digital:latest
```

#### Backend
```bash
# Build & Push
docker build -t backend_digitali:1 . && \
docker tag backend_digitali:1 karth1k/backend_digitali && \
docker push karth1k/backend_digitali

# Run
docker run -d -p 8000:8000 --name backend --restart always karth1k/backend_digital:latest
```

#### Database
```bash
docker run -d \
    --name database_digital \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=password123 \
    -p 5432:5432 \
    --restart always \
    postgres:alpine3.19
```

## Key Features

- **Responsive UI**: PrimeNG v17 components with Sakai template structure
- **Authentication**: Django-based user management
- **Real-time Updates**: Celery task queue with Redis
- **Database**: PostgreSQL with advanced features
- **Containerized**: Full Docker support for production deployment
- **Documentation**: Built-in Django admin docs

## Configuration Files

- `package.json` - Frontend dependencies
- `requirements.txt` - Backend dependencies  
- docker-compose.yml - Container orchestration
- `value_config.py` - Backend configuration

## Useful Commands

```bash
# Container shell access
docker exec -it backend /bin/bash

# Docker Compose operations
docker compose build
docker compose up -d
docker compose down

# Development servers
ng serve                    # Frontend dev server
python manage.py runserver  # Backend dev server
```

## Ports Reference
- **Frontend**: 4200 (prod), 4200 (dev)
- **Backend**: 8000
- **Database**: 5432
- **Redis**: 6379 (internal)

## Tracing the Execution Flow

When diagnosing issues or understanding how a particular feature or API endpoint works, a common and effective approach is **tracing the execution flow**. This involves starting from an entry point—such as a URL pattern, function call, or user action—and systematically following the references, function calls, or imports through the codebase to locate the relevant logic or implementation. This method is fundamental for debugging, code comprehension, and extending system functionality.

## Additional Documentation

- **Frontend Documentation**: See [Documents/frontend-docs](Documents/frontend-docs) for detailed guides and references related to the Angular/PrimeNG frontend.
- **Backend Documentation**: See [Documents/backend-docs](Documents/backend-docs) for Django backend API, models, and configuration details.