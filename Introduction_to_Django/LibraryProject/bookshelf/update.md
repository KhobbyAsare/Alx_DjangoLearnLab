# UPDATE Operation Documentation

## Command: Update the title of "1984" to "Nineteen Eighty-Four" and save the changes

### Python Commands:
```python
# Import the Book model
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

# Alternative: Update using update() method (more efficient for multiple records)
# Book.objects.filter(title="1984").update(title="Nineteen Eighty-Four")
```

### Expected Output:
```
# The book title is successfully updated
# Output should show:
Current title: 1984
Updated title: Nineteen Eighty-Four
```

### Additional Information:
- First retrieve the object using `get()` or `filter()`
- Modify the desired attributes directly
- Call `save()` to persist the changes to the database
- The `update()` method can be used for bulk updates but doesn't trigger model events
- After updating, the object in memory reflects the new values
- The database record is updated with the new title
