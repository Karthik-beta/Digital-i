# General Backend Documentation

This document provides an in-depth technical overview of the Digital-i backend, complementing the specific documentation for modules like [Attendance](attendance.md), [ManDays](mandays.md), and [Scheduler](scheduler.md). It focuses on the architectural design, core components, and operational aspects of the Django-based backend system.

## Project Structure

The backend is a monolithic Django project located in the `backend/` directory, adhering to standard Django conventions while incorporating project-specific structuring.

- `backend/`: Root directory for the Django project.
  - `backend/`: Main Django project configuration directory. This directory contains global configurations for the Django project.
    - `__init__.py`: Marks this directory as a Python package.
    - `settings.py`: Central Django settings file. It's dynamically configured to load sensitive data (e.g., `SECRET_KEY`, database credentials, API keys) from environment variables, promoting security and Twelve-Factor App principles. It defines `INSTALLED_APPS`, `MIDDLEWARE`, `DATABASES`, `TEMPLATES`, `STATIC_URL`, `MEDIA_URL`, logging configurations, and Django REST Framework settings.
    - `urls.py`: Root URLconf for the project. It includes URL patterns from various installed apps, directing incoming HTTP requests to the appropriate views.
    - `wsgi.py`: Entry point for WSGI-compatible web servers (e.g., Gunicorn, uWSGI) for synchronous request handling. It configures the Django application object.
    - `asgi.py`: Entry point for ASGI-compatible web servers (e.g., Daphne, Uvicorn) for asynchronous request handling. This allows for features like WebSockets or long-polling if implemented.
  - `config/`: A dedicated Django app for managing application-wide configurations that are typically stored in the database and managed via the Django admin interface.
    - `models.py`: Defines data models for configurable entities like `Shift`, `HolidayList`, and `BiometricDeviceConfiguration`. These models often include fields for parameters, thresholds, and operational settings.
    - `admin.py`: Registers the `config` app's models with the Django admin site for easy CRUD operations.
    - `apps.py`: App-specific configuration.
  - `resource/`: The primary Django app containing the core business logic, main data models (e.g., `Employee`, `AllLogs`, `Attendance`), data processing modules, and API endpoints.
    - `models.py`: Defines the core data schema, including models like `Employee`, `AllLogs`, `Attendance`, `ProcessedLogs`, `ManualLogs`, `ExternalDatabaseCredential`. These models utilize Django's ORM features like field types, relationships (ForeignKey, ManyToManyField, OneToOneField), model methods, and meta options (e.g., indexing, ordering).
    - `views.py` / `viewsets.py`: Contains Django views or Django REST Framework ViewSets that handle API request-response logic.
    - `serializers.py`: Defines DRF serializers for converting complex data types (e.g., Django model instances, querysets) to native Python datatypes that can then be easily rendered into JSON, XML, or other content types, and vice-versa for deserialization and validation of input data.
    - `urls.py`: App-specific URL configurations, typically included in the root `urls.py`.
    - `attendance.py`: Implements the detailed attendance processing logic (see [attendance.md](attendance.md)).
    - `mandays.py`: Implements the ManDays attendance processing logic (see [mandays.md](mandays.md)).
    - `scheduler.py`: Contains the APScheduler setup and job definitions for background tasks (see [scheduler.md](scheduler.md)).
    - `apps.py`: Application configuration for the `resource` app, notably including the initialization logic for the background scheduler.
    - `management/commands/`: Houses custom Django management commands. Each command is a Python module inheriting from `django.core.management.base.BaseCommand` and implements a `handle` method containing the command's logic.
  - `digitalenv/`: Python virtual environment directory, isolating project dependencies. This is typically not version-controlled.
  - `media/`: Default directory for storing user-uploaded files (e.g., profile pictures, documents), managed by Django's media file handling. Configured via `MEDIA_ROOT` and `MEDIA_URL` in `settings.py`.
  - `static/`: Directory (often at the app level, or a project-level `STATICFILES_DIRS`) for static assets like CSS, JavaScript, and images used by the application's templates. `STATIC_ROOT` is used for collecting static files for deployment.
  - `manage.py`: Django's command-line utility for administrative tasks such as running the development server, creating database migrations, running tests, and executing custom management commands.
  - `requirements.txt`: A pip-freeze generated file listing all Python package dependencies and their versions, ensuring reproducible environments.
  - `Dockerfile`: A text document that contains all the commands a user could call on the command line to assemble an image. Used by Docker to build the backend container image.
  - `entrypoint.sh`: A shell script executed as the default command when the Docker container starts. It typically handles pre-flight checks, database migrations (`python manage.py migrate --noinput`), static file collection (`python manage.py collectstatic --noinput`), and starting the application server (e.g., Gunicorn).
  - `.env.development`: File for storing environment variables during local development. This file is typically listed in `.gitignore` to prevent committing sensitive credentials.
  - `value_config.py`: A Python module containing application-specific constant values, enumerations, or simple configurations that are not dynamic enough to warrant database storage (e.g., `WEEK_OFF_CONFIG`).
  - `db.sqlite3`: Default SQLite database file, primarily used for local development and testing due to its simplicity.
  - `.dockerignore`: Specifies intentionally untracked files and directories that Docker should ignore when building the image, optimizing build times and image size.

## Core Models (`resource/models.py` and `config/models.py`)

The data persistence layer is built upon Django's Object-Relational Mapper (ORM).

### Employee & Configuration Models
- **`Employee`** (`resource.models.Employee`): Central entity representing employees. Key fields include `employee_id` (unique identifier, indexed), `user` (ForeignKey to `django.contrib.auth.models.User`, optional), `shift` (ForeignKey to `config.Shift`), `department`, `designation`, `date_of_joining`, `date_of_leaving`. Custom model methods might exist for deriving employee status or related information.
- **`Shift`** (`config.models.Shift`): Defines operational parameters for work shifts. Includes fields like `name`, `start_time`, `end_time`, `grace_period_late_in`, `grace_period_early_out`, `min_half_day_hours`, `max_work_hours_for_half_day`, `overtime_threshold_before_shift`, `overtime_threshold_after_shift`, `deduct_lunch_break` (Boolean), `lunch_break_duration`.
- **`HolidayList`** (`config.models.HolidayList`): Stores holiday information. Fields: `holiday_date` (DateField, unique), `holiday_name`, `holiday_type` (e.g., 'Public', 'Festival'). Indexed on `holiday_date` for efficient lookups.
- **`BiometricDeviceConfiguration`** (`config.models.BiometricDeviceConfiguration`): Configures biometric devices. Fields: `device_no`, `serial_number`, `ip_address`, `port`, `device_type`, `status`. Unique constraints might exist on `(device_no, serial_number)`.

### Log Ingestion and Management Models
- **`AllLogs`** (`resource.models.AllLogs`): Raw log data staging table. Fields: `employeeid`, `log_datetime`, `direction` ('IN'/'OUT'/'BOTH'), `device_id`, `source` (e.g., 'biometric', 'manual', 'external_db'). Timestamps (`created_at`, `updated_at`) are likely present.
- **`ProcessedLogs`** (`resource.models.ProcessedLogs`): Tracks the processing status of logs from `AllLogs`. Typically a OneToOneField or ForeignKey to `AllLogs` and a status field.
- **`Logs`** (`resource.models.Logs`): Used by `ManDaysAttendanceProcessor`. Fields: `employeeid`, `log_datetime`, `direction`. May include an `id` (primary key from external source) and `log_id` (internal primary key).
- **`ManualLogs`** (`resource.models.ManualLogs`): Stores manually entered attendance punches. Fields: `employeeid` (CharField, indexed), `log_datetime` (DateTimeField, indexed), `direction` (CharField), `reason`, `approved_by` (ForeignKey to User).
- **`ExternalDatabaseCredential`** (`resource.models.ExternalDatabaseCredential`): Securely stores connection parameters for external log databases. Fields: `name`, `database_type` ('MS_SQL', 'POSTGRESQL'), `host`, `port`, `user`, `password` (encrypted or using Django's secret management), `table_name`, `id_field`, `employeeid_field`, `direction_field`, `shortname_field`, `serialno_field`, `log_datetime_field`, `last_synced_id`.

### Attendance Data Models
- **`Attendance`** (`resource.models.Attendance`): Stores daily processed attendance records. Fields: `employee` (ForeignKey to `Employee`), `date` (DateField), `status` (e.g., 'P', 'A', 'HD', 'WO', 'PH'), `in_time`, `out_time`, `total_work_time`, `overtime`, `late_by`, `early_exit_by`. Unique constraint on `(employee, date)`.
- **`ManDaysAttendance`** (`resource.models.ManDaysAttendance`): Stores multi-slot daily attendance. Fields: `employee` (ForeignKey to `Employee`), `date` (DateField), `in_1`, `out_1`, ... `in_10`, `out_10`, `total_hours_slot_1`, ... `total_hours_slot_10`, `grand_total_hours`. Unique constraint on `(employee, date)`.

## API Design (Django REST Framework)

The backend exposes a RESTful API built using Django REST Framework (DRF).
- **Serializers (`serializers.py`)**: Mediate between Django models/querysets and Python native data types for JSON/XML rendering. They handle data validation, object creation/updates, and field-level modifications. `ModelSerializer` is commonly used for direct model mapping.
- **ViewSets (`views.py` or `viewsets.py`)**: Group related views for a particular model or resource. `ModelViewSet` provides default CRUD operations (list, create, retrieve, update, partial_update, destroy). Custom actions can be added using the `@action` decorator.
- **Routers (`urls.py`)**: Automatically generate URL patterns for ViewSets, simplifying URL configuration (e.g., `DefaultRouter`, `SimpleRouter`).
- **Pagination**: DRF provides pagination classes (e.g., `PageNumberPagination`, `LimitOffsetPagination`) to manage large datasets by returning them in chunks.
- **Filtering & Ordering**: Libraries like `django-filter` integrate with DRF for advanced filtering capabilities based on query parameters. Ordering is supported via `OrderingFilter`.
- **Content Negotiation**: DRF supports serving responses in different formats (e.g., JSON, browsable API) based on the `Accept` header or format suffixes.

## Configuration Management

- **Environment Variables**: Leveraged extensively via libraries like `python-dotenv` (for local development) and OS-level environment variables in production. `os.getenv()` or `decouple.config()` are used in `settings.py`.
- **`backend/backend/settings.py`**: Contains base settings and imports environment-specific configurations if necessary. Defines `INSTALLED_APPS`, `MIDDLEWARE`, `DATABASES` (configured to use environment variables for credentials), `TEMPLATES`, `AUTH_USER_MODEL`, `REST_FRAMEWORK` (for DRF global settings like default authentication, permission classes, pagination).
- **`value_config.py`**: Stores non-sensitive, application-wide constants that rarely change, improving code readability and maintainability.

## Database

- **ORM**: Django's ORM abstracts database interactions, allowing developers to work with Python objects. It supports complex queries, transactions (`django.db.transaction.atomic`), and database schema migrations.
- **Migrations**: Schema changes are managed through `python manage.py makemigrations` (generates migration files) and `python manage.py migrate` (applies migrations). Migrations are designed to be atomic.
- **Connection Pooling**: In production, database connection pooling (e.g., using PgBouncer for PostgreSQL) is often configured at the infrastructure level or via Django packages to improve performance and resource utilization.
- **Production Database**: PostgreSQL is typically favored for its robustness, ACID compliance, and advanced features.

## Deployment

- **Docker & Docker Compose**: Containerization is achieved using Docker, with `Dockerfile` defining the image build process. Docker Compose is likely used for orchestrating multi-container setups (backend, database, frontend, Redis) in development and potentially production.
- **`entrypoint.sh`**: Handles container startup tasks:
    1.  Wait for database availability (if separate container).
    2.  Apply database migrations: `python manage.py migrate --noinput`.
    3.  Collect static files: `python manage.py collectstatic --noinput`.
    4.  Start the WSGI/ASGI server: e.g., `gunicorn backend.wsgi:application --bind 0.0.0.0:8000`.
- **Application Server**: Gunicorn (for WSGI) or Uvicorn/Daphne (for ASGI) are common choices for serving the Django application in production, managing worker processes and handling concurrent requests.
- **Reverse Proxy**: Nginx or Apache is typically deployed in front of the application server to handle SSL termination, load balancing, serving static/media files directly, request buffering, and security headers.

## Authentication and Authorization

- **Django Admin**: Uses `django.contrib.auth` with session-based authentication.
- **API Authentication (DRF)**:
    -   `TokenAuthentication`: For stateless APIs using simple tokens.
    -   `JWT (JSON Web Token) Authentication`: Common for stateless, secure APIs, often via packages like `djangorestframework-simplejwt`.
    -   `SessionAuthentication`: Can be used if the API is consumed by a tightly coupled frontend on the same domain.
    Configured in `REST_FRAMEWORK` settings.
- **Permissions (DRF)**: Control access to API endpoints.
    -   Built-in: `IsAuthenticated`, `IsAdminUser`, `AllowAny`.
    -   Custom permission classes inheriting from `BasePermission` for fine-grained access control based on user roles or object-level permissions.

## Logging

- **Python `logging` module**: Configured in `settings.py` via the `LOGGING` dictionary.
- **Handlers**: `ConsoleHandler` (for development, Docker logs), `FileHandler` (for persistent logs), `MailHandler` (for critical errors).
- **Formatters**: Define log message structure, including timestamp, log level, module name, and message.
- **Log Levels**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` are used appropriately throughout the codebase.
- **Structured Logging**: Libraries like `python-json-logger` can be used for outputting logs in JSON format, facilitating easier parsing and analysis by log management systems (e.g., ELK stack, Splunk).

## Management Commands

Located in `resource/management/commands/`, these scripts automate backend tasks:
- **Structure**: Inherit from `django.core.management.base.BaseCommand`. Implement `add_arguments(self, parser)` for command-line arguments and `handle(self, *args, **options)` for the core logic.
- **Key Commands (as per scheduler context)**:
    - `sync_logs`: Fetches logs from external sources (biometric devices, databases via `ExternalDatabaseCredential`).
    - `sync_all_logs`: A comprehensive version of `sync_logs`.
    - `absentees`: Calculates and flags absent employees based on processed attendance.
    - `task`: Generic placeholder for various scheduled tasks.
    - `mandays`: Invokes the `ManDaysAttendanceProcessor`.
    - `correct_a_wo_a_pattern`, `revert_awo_corrections`: Data integrity and correction tasks.
Executed via `python manage.py <command_name> [arguments]`.

## Middleware (`settings.py` - `MIDDLEWARE`)

Django middleware is a framework of hooks into Django's request/response processing. Each middleware component is a class that processes requests before they reach the view and responses before they are sent to the client.
Common middleware includes:
- `SecurityMiddleware`: Enhances security (XSS protection, HSTS, etc.).
- `SessionMiddleware`: Enables session management.
- `AuthenticationMiddleware`: Adds the `user` object to requests.
- `CommonMiddleware`: Handles common tasks like ETags and URL rewriting.
Custom middleware can be written for specific cross-cutting concerns.

## Static and Media Files

- **Static Files**: CSS, JavaScript, images integral to the application's presentation.
    - `STATIC_URL`: URL prefix for static files (e.g., `/static/`).
    - `STATICFILES_DIRS`: List of directories where Django will look for static files in addition to app `static/` subdirectories.
    - `STATIC_ROOT`: Absolute path to the directory where `collectstatic` will gather all static files for deployment. Served by Nginx in production.
- **Media Files**: User-uploaded content.
    - `MEDIA_URL`: URL prefix for media files (e.g., `/media/`).
    - `MEDIA_ROOT`: Absolute path to the directory where media files are stored.
    Permissions and storage backends (e.g., Amazon S3) can be configured for media files.

---
This expanded general documentation provides a more granular and technical insight into the backend architecture and its various components.