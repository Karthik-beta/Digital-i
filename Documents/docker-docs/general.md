# Digital-i Docker Deployment Documentation

This document provides a comprehensive guide for deploying the Digital-i application stack using Docker and Docker Compose. It covers building, tagging, pushing, and running Docker images for the frontend, backend, and database services, as well as important configuration notes for production deployments.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Docker Images](#docker-images)
    - [Frontend](#frontend)
    - [Backend](#backend)
    - [Database](#database)
    - [Redis](#redis)
4. [Docker Compose Deployment](#docker-compose-deployment)
5. [Configuration Notes](#configuration-notes)
6. [Container Management](#container-management)
7. [Updating Services](#updating-services)
8. [Troubleshooting](#troubleshooting)

---

## Overview

Digital-i is deployed as a multi-container application using Docker Compose. The stack consists of:

- **Frontend**: Angular application served via Nginx.
- **Backend**: Django REST API.
- **Database**: PostgreSQL.
- **Redis**: For caching and Celery task queue.

---

## Prerequisites

- Docker Engine (v20+ recommended)
- Docker Compose (v2+ recommended)
- Access to the required Docker images (see below)
- Network access to the backend and database IPs

---

## Docker Images

### Frontend

**Build:**
```sh
docker build -t frontend_digitali:1 ./frontend