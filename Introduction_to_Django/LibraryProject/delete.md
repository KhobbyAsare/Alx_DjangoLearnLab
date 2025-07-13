# DELETE Operation Documentation

## Command: Delete the book you created and confirm the deletion by trying to retrieve all books again

### Python Commands:
```python
# Import the Book model
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

# Alternative: Delete using filter and delete (more efficient for multiple records)
# Book.objects.filter(title="Nineteen Eighty-Four").delete()
```

### Expected Output:
```
# The book is successfully deleted from the database
# Output should show:
Books before deletion:
- Nineteen Eighty-Four by George Orwell

Books after deletion:
No books found in the database.
```

### Additional Information:
- The `delete()` method permanently removes the object from the database
- After deletion, the object can no longer be retrieved
- The `delete()` method returns a tuple: (number_of_objects_deleted, {model_name: count})
- You can also use `Book.objects.filter().delete()` for bulk deletions
- Once deleted, attempting to access the object will raise a `DoesNotExist` exception
- The deletion is immediate and cannot be undone without recreating the object
