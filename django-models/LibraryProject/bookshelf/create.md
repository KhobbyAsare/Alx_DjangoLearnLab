# CREATE Operation Documentation

## Command: Create a Book instance with the title "1984", author "George Orwell", and publication year 1949

### Python Commands:
```python
# Import the Book model
from bookshelf.models import Book

# Method 1: Create using Book.objects.create (direct creation and save)
book = Book.objects.create(title="1984", author="George Orwell", publication_year="1949-06-08")

# Verify the creation
print(f"Book created: {book.title} by {book.author}")
print(f"Book ID: {book.id}")

# Method 2: Create instance and save separately
# book = Book(title="1984", author="George Orwell", publication_year="1949-06-08")
# book.save()
```

### Expected Output:
```
# The book instance is created successfully and saved to the database
# Output should show:
Book created: 1984 by George Orwell
Book ID: 1
```

### Additional Information:
- The `Book.objects.create()` method creates and saves the object in one step
- The `publication_year` field is a DateField, so we need to provide a date value
- After creation, Django automatically assigns an ID to the object
- The book is now persisted in the database and can be retrieved later
- `Book.objects.create()` is more efficient than creating an instance and calling save() separately
