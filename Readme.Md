# TaskPilot: Task Management System

TaskPilot is a Django-based task management system designed to organize users, projects, and tasks efficiently. It features role-based access, notifications, image handling via Cloudinary, and asynchronous processing with Celery and Redis.

## Features

- **Role-based CRUD:**
  - Admin: Full CRUD for users, projects, and tasks
  - Manager: Create/edit projects and tasks
  - Employee: Read-only access to tasks
- **Notifications & Reminders:** Sent via email using Mailtrap
- **Image Handling:** Cloudinary integration for profile and project images
- **Asynchronous Tasks:** Celery and Redis for background processing
- **PostgreSQL Database:** Robust and scalable data storage
- **Modern Admin Dashboard:** Built with AdminLTE

## Technologies Used

- Django 5.2.4
- PostgreSQL
- Celery & Redis
- Cloudinary (image storage)
- Mailtrap (email testing)
- Python Decouple (.env management)
- AdminLTE (UI)

## Project Structure

```
project/
├── .env                  # Environment variables (not tracked)
├── .gitignore            # Git ignore rules
├── Readme.Md             # Project documentation
├── celerybeat-schedule   # Celery beat schedule file
├── env/                  # Python virtual environment
├── manage.py             # Django management script
├── media/
│   └── profile_images/   # Uploaded user images
├── projects/             # Project app
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   └── ...
├── requirements.txt      # Python dependencies
├── static/
│   └── adminlte/         # AdminLTE static files
├── taskpilot/            # Main Django project
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── tasks/                # Task app
│   ├── migrations/
│   ├── models.py
│   ├── tasks.py
│   ├── views.py
│   └── ...
├── templates/
│   ├── dashboard/
│   ├── layout/
│   ├── users/
│   └── utils/
└── users/                # User app
    ├── migrations/
    ├── models.py
    ├── views.py
    ├── context_processors.py
    ├── middleware.py
    └── ...
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShubhamShanker510/taskpilot.git
   cd taskpilot
   ```
2. **Create and activate a virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # Or manually:
   pip install django psycopg2-binary python-decouple cloudinary django-cloudinary-storage celery redis
   ```
4. **Configure environment variables**
   - Create a `.env` file in the project root with:
     ```
     DB_NAME=your_db_name
     DB_USER=your_db_user
     DB_PASSWORD=your_db_password
     DB_HOST=localhost
     DB_PORT=5432
     EMAIL_HOST=smtp.mailtrap.io
     EMAIL_HOST_USER=your_mailtrap_user
     EMAIL_HOST_PASSWORD=your_mailtrap_password
     EMAIL_PORT=2525
     EMAIL_USE_TLS=True
     DEFAULT_FROM_EMAIL=your@email.com
     CLOUDINARY_CLOUD_NAME=your_cloud_name
     CLOUDINARY_API_KEY=your_api_key
     CLOUDINARY_API_SECRET=your_api_secret
     ```
5. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```
6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```
7. **Start Redis server**
   ```bash
   redis-server
   ```
8. **Start Celery worker and beat (in a new terminal)**
   ```bash
   celery -A taskpilot worker --loglevel=info
   ```
   ```bash
   celery -A taskpilot beat --loglevel=info
   ```
9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Access the Application

- **Dashboard:** http://127.0.0.1:8000/dashboard/home
- **Login:** http://127.0.0.1:8000/users/login/
  - USERNAME: admin
  - PASSWORD: admin

---

For any issues, please check your `.env` configuration and ensure all services (Redis, Celery) are running.
