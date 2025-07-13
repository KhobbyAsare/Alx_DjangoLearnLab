# LibraryProject

A Django-based library management system developed as part of the ALX Backend Pathway program.

## Complete Setup Guide: From Python Installation to Django Project

### Step 1: Install Python

1. **Download Python:**
   - Go to https://python.org/downloads/
   - Download the latest Python version (3.11+ recommended)
   - Make sure to check "Add Python to PATH" during installation

2. **Verify Python installation:**
   ```powershell
   python --version
   pip --version
   ```

### Step 2: Create Project Directory

```powershell
# Navigate to your desired location
cd "C:\Users\samue\OneDrive\Documents\ALX PROGRAM\Backend Pathway\Github\Introduction_to_Django"

# Create project directory
mkdir LibraryProject
cd LibraryProject
```

### Step 3: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Alternative method if above doesn't work
python -m venv library_env
```

### Step 4: Activate Virtual Environment

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\Activate.ps1
```

### Step 5: Install Django

```powershell
# Make sure virtual environment is activated (you should see (venv) in prompt)
pip install django

# Verify Django installation
django-admin --version
```

### Step 6: Create Django Project

```powershell
# Create Django project
django-admin startproject library_management .

# Or create in a subdirectory
django-admin startproject library_management
```

### Step 7: Navigate to Project and Create App

```powershell
# If you created project in subdirectory
cd library_management

# Create a Django app
python manage.py startapp books
```

### Step 8: Initial Setup

```powershell
# Run initial migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 9: Run Development Server

```powershell
# Start the development server
python manage.py runserver

# Server will run at http://127.0.0.1:8000/
```

### Step 10: Create Requirements File

```powershell
# Generate requirements.txt
pip freeze > requirements.txt
```

## Additional Files to Create

### Create .gitignore file:
```powershell
# Create .gitignore
New-Item -ItemType File -Name ".gitignore"
```

### Create environment variables file:
```powershell
# Create .env file for environment variables
New-Item -ItemType File -Name ".env"
```

## Summary of Commands in Order:

```powershell
# 1. Check Python
python --version

# 2. Create and navigate to project
mkdir LibraryProject
cd LibraryProject

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 5. Install Django
pip install django

# 6. Create Django project
django-admin startproject library_management .

# 7. Create app
python manage.py startapp books

# 8. Run migrations
python manage.py migrate

# 9. Create superuser
python manage.py createsuperuser

# 10. Start server
python manage.py runserver

# 11. Create requirements file
pip freeze > requirements.txt
```

## Project Structure After Setup:
```
LibraryProject/
├── venv/
├── library_management/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── books/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── manage.py
├── requirements.txt
└── .gitignore
```

## Features (To Be Implemented)

- Library book management
- User authentication
- Book borrowing system
- Book search and filtering
- Admin interface for library management

## Development

### Prerequisites

- Python 3.x
- Django
- pip

### Installation

1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

Navigate to `http://localhost:8000` in your web browser to access the application.

## Contributing

This is a learning project for the ALX Backend Pathway program.

## License

This project is for educational purposes as part of the ALX Backend Pathway program.
