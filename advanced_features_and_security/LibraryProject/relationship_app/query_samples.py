import os
import sys
import django

# Add project base directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibraryProject.settings")
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

def get_books_by_author(author_name):
    print(f"\n📚 Books by author: {author_name}")
    try:
        author = Author.objects.get(name=author_name)
        # Use related_name if you defined it (e.g., related_name='books' in Book model)
        books = author.books.all() if hasattr(author, 'books') else Book.objects.filter(author=author)
        for book in books:
            print(f"- {book.title}")
    except Author.DoesNotExist:
        print("Author not found.")

def list_books_in_library(library_name):
    print(f"\n🏛️ Books in library: {library_name}")
    try:
        library = Library.objects.get(name=library_name)
        books = library.books.all() if hasattr(library, 'books') else Book.objects.filter(library=library)
        for book in books:
            print(f"- {book.title} by {book.author.name}")
    except Library.DoesNotExist:
        print("Library not found.")

def get_librarian_for_library(library_name):
    print(f"\n👩‍💼 Librarian for library: {library_name}")
    try:
        library = Library.objects.get(name=library_name)
        librarian = Librarian.objects.get(library=library)
        print(f"Librarian: {librarian.name}")
    except Library.DoesNotExist:
        print("Library not found.")
    except Librarian.DoesNotExist:
        print("Librarian not assigned to this library.")

# Example usage
if __name__ == "__main__":
    get_books_by_author("Jane Austen")
    list_books_in_library("Central Library")
    get_librarian_for_library("Central Library")
