# CRUD Operations Documentation

This document contains all the CRUD (Create, Read, Update, Delete) operations performed on the Book model in the Django shell, along with their actual commands and outputs.

## Prerequisites

Before running these operations, ensure you have:
1. Created the Book model in `bookshelf/models.py`
2. Added the 'bookshelf' app to `INSTALLED_APPS` in `settings.py`
3. Run `python manage.py makemigrations bookshelf`
4. Run `python manage.py migrate`

## Model Definition

```python
# bookshelf/models.py
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_year = models.DateField()
```

## Django Shell Commands

To start the Django shell, run:
```bash
python manage.py shell
```

---

## 1. CREATE Operation

### Command:
```python
from bookshelf.models import Book

# Create a Book instance with the title "1984", author "George Orwell", and publication year 1949
book = Book(title="1984", author="George Orwell", publication_year="1949-06-08")
book.save()

# Verify the creation
print(f"Book created: {book.title} by {book.author}")
print(f"Book ID: {book.id}")
```

### Expected Output:
```
Book created: 1984 by George Orwell
Book ID: 1
```

---

## 2. RETRIEVE Operation

### Command:
```python
from bookshelf.models import Book

# Retrieve the book by title
book = Book.objects.get(title="1984")

# Display all attributes of the book
print(f"Book ID: {book.id}")
print(f"Title: {book.title}")
print(f"Author: {book.author}")
print(f"Publication Year: {book.publication_year}")

# Alternative: Retrieve all books
all_books = Book.objects.all()
print(f"Total books in database: {len(all_books)}")
for book in all_books:
    print(f"- {book.title} by {book.author}")
```

### Expected Output:
```
Book ID: 1
Title: 1984
Author: George Orwell
Publication Year: 1949-06-08
Total books in database: 1
- 1984 by George Orwell
```

---

## 3. UPDATE Operation

### Command:
```python
from bookshelf.models import Book

# Retrieve the book to update
book = Book.objects.get(title="1984")

# Display the current title
print(f"Current title: {book.title}")

# Update the title
book.title = "Nineteen Eighty-Four"

# Save the changes to the database
book.save()

# Verify the update
print(f"Updated title: {book.title}")
```

### Expected Output:
```
Current title: 1984
Updated title: Nineteen Eighty-Four
```

---

## 4. DELETE Operation

### Command:
```python
from bookshelf.models import Book

# First, show all books before deletion
print("Books before deletion:")
all_books = Book.objects.all()
for book in all_books:
    print(f"- {book.title} by {book.author}")

# Retrieve the book to delete
book = Book.objects.get(title="Nineteen Eighty-Four")

# Delete the book
book.delete()

# Confirm the deletion by retrieving all books again
print("\nBooks after deletion:")
all_books = Book.objects.all()
if all_books:
    for book in all_books:
        print(f"- {book.title} by {book.author}")
else:
    print("No books found in the database.")
```

### Expected Output:
```
Books before deletion:
- Nineteen Eighty-Four by George Orwell

Books after deletion:
No books found in the database.
```

---

## Alternative Methods

### Create using create() method:
```python
book = Book.objects.create(title="1984", author="George Orwell", publication_year="1949-06-08")
```

### Update using update() method:
```python
Book.objects.filter(title="1984").update(title="Nineteen Eighty-Four")
```

### Delete using filter and delete:
```python
Book.objects.filter(title="Nineteen Eighty-Four").delete()
```

---

## Notes

1. **DateField**: The `publication_year` field is a DateField, so it requires a date value (YYYY-MM-DD format).
2. **Primary Key**: Django automatically creates an `id` field as the primary key.
3. **Error Handling**: Always handle `DoesNotExist` exceptions when using `get()`.
4. **Bulk Operations**: Use `filter()` with `update()` or `delete()` for bulk operations.
5. **Save Method**: Remember to call `save()` after modifying an object to persist changes.
