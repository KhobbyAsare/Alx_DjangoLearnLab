# CREATE Operation Documentation

## Command: Create a Book instance with the title "1984", author "George Orwell", and publication year 1949

### Python Commands:
```python
# Import the Book model
from bookshelf.models import Book

# Create a Book instance with the specified attributes
book = Book(title="1984", author="George Orwell", publication_year="1949-06-08")

# Save the book to the database
book.save()

# Verify the creation
print(f"Book created: {book.title} by {book.author}")
print(f"Book ID: {book.id}")
```

### Expected Output:
```
# The book instance is created successfully and saved to the database
# Output should show:
Book created: 1984 by George Orwell
Book ID: 1
```

### Additional Information:
- The `publication_year` field is a DateField, so we need to provide a date value
- The `save()` method commits the object to the database
- After saving, Django automatically assigns an ID to the object
- The book is now persisted in the database and can be retrieved later
