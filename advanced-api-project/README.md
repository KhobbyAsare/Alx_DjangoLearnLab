
# Book & Author API - Django REST Framework

This project is a simple demonstration of how to build a Django REST Framework (DRF) API to manage `Author` and `Book` objects, from **model definition**, through **serialization**, to **API views** that provide CRUD functionality.

---

## 1. Models

The project contains two models: **Author** and **Book**.

```python
from django.db import models

# Author Model
class Author(models.Model):
    name = models.CharField(max_length=100)  # Author's full name

    def __str__(self):
        return self.name


# Book Model
class Book(models.Model):
    title = models.CharField(max_length=100)  # Book title
    publication_year = models.DateField()    # Date of publication
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,            # Delete books when their author is deleted
        related_name='books'                  # Reverse lookup: author.books.all()
    )

    def __str__(self):
        return self.title



# Book API - Django REST Framework

This API provides CRUD operations for managing books using Django REST Framework's generic views.

## Endpoints Overview

### 1. List All Books
**URL:** `/books/`  
**Method:** GET  
**View:** `BookListAPI` (ListAPIView)  
**Permissions:** `IsAuthenticatedOrReadOnly`  
- Anyone can view all books.
- No write operations here.
- Can be customized via `get_queryset()` to filter books.

---

### 2. Retrieve Single Book
**URL:** `/books/<id>/`  
**Method:** GET  
**View:** `BookDetailAPI` (RetrieveAPIView)  
**Permissions:** `IsAuthenticatedOrReadOnly`  
- Anyone can view a single book by ID.

---

### 3. Create Book
**URL:** `/books/`  
**Method:** POST  
**View:** `BookCreateAPI` (CreateAPIView)  
**Permissions:** `IsAuthenticated`  
- Only authenticated users can add books.
- Can be customized via `perform_create()` to automatically set book owner.

---

### 4. Update Book
**URL:** `/books/<id>/`  
**Methods:** PUT (full update), PATCH (partial update)  
**View:** `BookUpdateAPI` (UpdateAPIView)  
**Permissions:** `IsAuthenticated`  
- Only authenticated users can update.
- Can be customized via `perform_update()` to enforce ownership checks.

---

### 5. Delete Book
**URL:** `/books/<id>/`  
**Method:** DELETE  
**View:** `BookDeleteAPI` (DestroyAPIView)  
**Permissions:** `IsAuthenticated`  
- Only authenticated users can delete.
- Can be customized via `perform_destroy()` to perform soft deletes.

---

## Permissions Used

- **IsAuthenticatedOrReadOnly**
  - GET: Allowed for everyone
  - POST/PUT/PATCH/DELETE: Allowed only for authenticated users

- **IsAuthenticated**
  - All methods allowed only for authenticated users

---

## Hooks & Customization Points

These DRF-provided hooks can be overridden to change behavior:

- **`get_queryset(self)`**
  - Filter or modify the queryset before returning data.
  - Example: Limit books to those created by the logged-in user.

- **`perform_create(self, serializer)`**
  - Add extra save logic when creating a book.
  - Example: Set `serializer.save(owner=self.request.user)`.

- **`perform_update(self, serializer)`**
  - Add logic before/after updating a book.
  - Example: Check if the logged-in user is the book’s owner.

- **`perform_destroy(self, instance)`**
  - Modify deletion behavior.
  - Example: Implement soft deletes instead of removing the record.

---

## Requirements

- Django
- Django REST Framework

## Running the API
```bash
python manage.py runserver
