from rest_framework import serializers
from datetime import datetime
from .models import Author, Book

# Serializer for the Book model.
# Converts Book model instances into JSON format and validates incoming data for creating/updating books.
# Fields:
# - 'title': The name of the book.
# - 'publication_year': The year the book was published (validated so it cannot be in the future).
# - 'author': The ID of the related Author.
class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author', 'author_name']

    def validate_publication_year(self, value):
        """
        Ensure the publication year is not in the future.
        """
        current_year = datetime.now().year
        if value.year > current_year:
            raise serializers.ValidationError("Publication year cannot be in the future.")
        return value


# Serializer for the Author model.
# Includes a nested representation of the related books using BookSerializer.
# This means when retrieving an author, their books are also displayed in JSON format.
# 'books' is read-only, meaning it is only used when retrieving data, not for creating/updating.
# Relationship handling:
# - The 'books' field maps to the related_name='books' in the Book model's ForeignKey.
# - This allows Django REST Framework to automatically retrieve all books for a given author.
class AuthorSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)  # Nested serializer for related books

    class Meta:
        model = Author
        fields = ['id','name', 'books']
