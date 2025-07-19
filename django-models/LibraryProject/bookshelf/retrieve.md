# RETRIEVE Operation Documentation

## Command: Retrieve and display all attributes of the book you just created

### Python Commands:
```python
# Import the Book model
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
# The book details are displayed showing all attributes
# Output should show:
Book ID: 1
Title: 1984
Author: George Orwell
Publication Year: 1949-06-08
Total books in database: 1
- 1984 by George Orwell
```

### Additional Information:
- `Book.objects.get()` retrieves a single object that matches the criteria
- `Book.objects.all()` retrieves all Book objects from the database
- If no book matches the criteria, `get()` raises a `DoesNotExist` exception
- If multiple books match the criteria, `get()` raises a `MultipleObjectsReturned` exception
- The QuerySet is evaluated when you iterate over it or call methods like `len()`
