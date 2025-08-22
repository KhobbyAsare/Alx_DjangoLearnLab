#!/usr/bin/env python
"""
Deployment script for Social Media API
Handles various deployment tasks and environment setup.
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key for Django."""
    return secrets.token_urlsafe(50)

def run_command(command):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error output: {e.stderr}")
        return None

def setup_environment():
    """Set up environment for deployment."""
    print("Setting up deployment environment...")
    
    # Create necessary directories
    directories = ['logs', 'staticfiles', 'media']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Generate secret key if not exists
    if not os.environ.get('SECRET_KEY'):
        secret_key = generate_secret_key()
        print(f"Generated SECRET_KEY: {secret_key}")
        print("Please set this as an environment variable in your production environment")
    
    print("Environment setup complete!")

def collect_static():
    """Collect static files for production."""
    print("Collecting static files...")
    result = run_command("python manage.py collectstatic --noinput")
    if result is not None:
        print("Static files collected successfully!")
    else:
        print("Failed to collect static files!")

def run_migrations():
    """Run database migrations."""
    print("Running database migrations...")
    result = run_command("python manage.py migrate")
    if result is not None:
        print("Migrations completed successfully!")
    else:
        print("Failed to run migrations!")

def create_superuser():
    """Create a superuser account."""
    print("Creating superuser account...")
    result = run_command("python manage.py createsuperuser --noinput")
    if result is not None:
        print("Superuser created successfully!")
    else:
        print("Superuser creation skipped or failed")

def check_deployment():
    """Run Django's deployment check."""
    print("Running deployment checks...")
    result = run_command("python manage.py check --deploy")
    if result is not None:
        print("Deployment checks completed!")
        print(result)
    else:
        print("Deployment checks failed!")

def main():
    """Main deployment function."""
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [setup|migrate|static|check|full]")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        setup_environment()
    elif command == "migrate":
        run_migrations()
    elif command == "static":
        collect_static()
    elif command == "check":
        check_deployment()
    elif command == "full":
        setup_environment()
        run_migrations()
        collect_static()
        check_deployment()
    else:
        print("Invalid command. Use: setup, migrate, static, check, or full")

if __name__ == "__main__":
    main()
