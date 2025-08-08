from django.db import models

# The Author model represents a book author.
# Each author has a name, which is stored as a character field.
# This is the parent in the Author-Book relationship.
class Author(models.Model):
    name = models.CharField(max_length=100)  # Author's full name

    def __str__(self):
        return self.name


# The Book model represents a book written by an author.
# - 'title' stores the name of the book.
# - 'publication_year' stores the year the book was published.
# - 'author' is a ForeignKey to the Author model, meaning each book is linked to exactly one author.
# The relationship is one-to-many: one author can have multiple books, but each book belongs to one author.



# class Book(models.Model):
#     title = models.CharField(max_length=100)  # Book title
#     publication_year = models.DateField()  # Year of publication (DateField for flexibility if needed)
#     author = models.ForeignKey(
#         Author, 
#         on_delete=models.CASCADE,  # If the author is deleted, all their books are also deleted
#         related_name='books'  # Allows reverse lookup from Author to their books (e.g., author.books.all())
#     )

#     def __str__(self):
#         return self.title


class Book(models.Model):
    title = models.CharField(max_length=100)
    publication_year = models.DateField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
