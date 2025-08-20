# Social Media API

A comprehensive RESTful API built with Django and Django REST Framework for social media functionality, focusing on user authentication and profile management.

## 🚀 Features

- **User Authentication**: Token-based authentication system
- **User Registration**: Create new user accounts with extended profile information
- **User Profile Management**: View and update user profiles
- **Social Features**: Follow/unfollow system with follower counts
- **Admin Interface**: Django admin for user management
- **Profile Pictures**: Image upload functionality for user avatars
- **Comprehensive API Documentation**: Well-documented endpoints

## 🛠️ Tech Stack

- **Backend**: Django 5.2.5
- **API Framework**: Django REST Framework 3.16.0
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Token-based authentication
- **Image Processing**: Pillow
- **Documentation**: Auto-generated API docs

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd social_media_api
```

### 2. Install Dependencies

```bash
pip install django djangorestframework Pillow
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:8000/api/auth/
```

### Authentication
Most endpoints require authentication using Token authentication. Include the token in the Authorization header:
```
Authorization: Token <your_token_here>
```

### Endpoints

#### 🔐 Authentication Endpoints

##### Register a New User
- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "A brief bio about myself",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}
```
- **Response**: `201 Created`
```json
{
    "user": {
        "id": 1,
        "username": "newuser",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "A brief bio about myself",
        "profile_picture": null,
        "follower_count": 0,
        "following_count": 0,
        "followers": [],
        "date_joined": "2025-08-20T22:30:00Z",
        "created_at": "2025-08-20T22:30:00Z",
        "updated_at": "2025-08-20T22:30:00Z"
    },
    "token": "your_authentication_token_here",
    "message": "User registered successfully"
}
```

##### User Login
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:
```json
{
    "username": "newuser",
    "password": "securepassword123"
}
```
- **Response**: `200 OK`
```json
{
    "user": {
        "id": 1,
        "username": "newuser",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "A brief bio about myself",
        "profile_picture": null,
        "follower_count": 0,
        "following_count": 0,
        "followers": [],
        "date_joined": "2025-08-20T22:30:00Z",
        "created_at": "2025-08-20T22:30:00Z",
        "updated_at": "2025-08-20T22:30:00Z"
    },
    "token": "your_authentication_token_here",
    "message": "Login successful"
}
```

##### User Logout
- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Authentication**: Required
- **Response**: `200 OK`
```json
{
    "message": "Successfully logged out"
}
```

#### 👤 Profile Management Endpoints

##### Get Current User Profile
- **URL**: `/api/auth/profile/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: `200 OK`
```json
{
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "A brief bio about myself",
    "profile_picture": null,
    "follower_count": 0,
    "following_count": 0,
    "followers": [],
    "date_joined": "2025-08-20T22:30:00Z",
    "created_at": "2025-08-20T22:30:00Z",
    "updated_at": "2025-08-20T22:30:00Z"
}
```

##### Update Current User Profile
- **URL**: `/api/auth/profile/`
- **Method**: `PUT` or `PATCH`
- **Authentication**: Required
- **Request Body** (PATCH example):
```json
{
    "first_name": "Updated",
    "bio": "My updated bio"
}
```
- **Response**: `200 OK`

#### 👥 Social Features

##### Follow/Unfollow User
- **URL**: `/api/auth/follow/<username>/`
- **Method**: `POST`
- **Authentication**: Required
- **Response**: `200 OK`
```json
{
    "message": "You are now following username",
    "is_following": true
}
```

##### Get User Details
- **URL**: `/api/auth/users/<username>/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: `200 OK`
```json
{
    "id": 1,
    "username": "username",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "User bio",
    "profile_picture": null,
    "follower_count": 5,
    "following_count": 3,
    "followers": ["user1", "user2"],
    "date_joined": "2025-08-20T22:30:00Z",
    "created_at": "2025-08-20T22:30:00Z",
    "updated_at": "2025-08-20T22:30:00Z"
}
```

##### List All Users
- **URL**: `/api/auth/users/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: `200 OK`
```json
[
    {
        "id": 1,
        "username": "user1",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "Bio here",
        "profile_picture": null,
        "follower_count": 2
    },
    {
        "id": 2,
        "username": "user2",
        "first_name": "Jane",
        "last_name": "Smith",
        "bio": "Another bio",
        "profile_picture": "profile_pics/image.jpg",
        "follower_count": 5
    }
]
```

## 🗂️ Project Structure

```
social_media_api/
├── accounts/                  # User accounts app
│   ├── migrations/           # Database migrations
│   ├── __init__.py
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # User model
│   ├── serializers.py       # API serializers
│   ├── urls.py              # App URL patterns
│   └── views.py             # API views
├── social_media_api/         # Main project directory
│   ├── __init__.py
│   ├── asgi.py              # ASGI config
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL config
│   └── wsgi.py              # WSGI config
├── media/                    # Media files (uploads)
├── manage.py                # Django management script
├── test_api.py              # API test script
├── README.md                # This file
└── db.sqlite3               # SQLite database
```

## 🧪 Testing

### Automated Testing

Run the included test script to verify all endpoints:

```bash
python test_api.py
```

This will test:
- User registration
- User login
- Profile retrieval
- Profile updates
- User listing
- User logout

### Manual Testing

You can also test the API manually using tools like:
- **Postman**: Import the endpoints and test them
- **curl**: Use command line to test endpoints
- **Django Browsable API**: Visit endpoints in your browser

Example curl commands:

```bash
# Register a new user
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'

# Get profile (replace TOKEN with actual token)
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## 🔧 Configuration

### Settings Overview

Key settings in `social_media_api/settings.py`:

- **Custom User Model**: Uses `accounts.User` instead of default Django user
- **Token Authentication**: Configured for API access
- **Media Files**: Configured for profile picture uploads
- **Database**: SQLite for development (easily changeable for production)

### Environment Variables

For production, consider using environment variables for:
- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL`
- `ALLOWED_HOSTS`

## 📝 Models

### User Model

The custom User model extends Django's AbstractUser with additional fields:

- `bio`: TextField for user biography (max 500 chars)
- `profile_picture`: ImageField for user avatar
- `followers`: ManyToManyField for follow relationships
- `created_at`: Auto timestamp for creation
- `updated_at`: Auto timestamp for updates

## 🔒 Security Features

- **Token Authentication**: Secure API access
- **Password Validation**: Built-in Django password validators
- **CSRF Protection**: Included in Django middleware
- **Admin Interface**: Secure admin panel for user management
- **Input Validation**: Comprehensive serializer validation

## 🚀 Deployment Considerations

For production deployment:

1. **Environment Variables**: Use environment variables for sensitive settings
2. **Database**: Switch to PostgreSQL or MySQL
3. **Static Files**: Configure static file serving
4. **Media Files**: Use cloud storage (AWS S3, etc.)
5. **HTTPS**: Enable SSL/TLS encryption
6. **Logging**: Configure proper logging
7. **Monitoring**: Add application monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

For questions or issues:
1. Check the documentation
2. Review existing GitHub issues
3. Create a new issue with detailed information

---

**Happy Coding!** 🎉

This Social Media API provides a solid foundation for building social media applications with user authentication and profile management features.
