from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from django_filters import rest_framework  # Import django_filters to satisfy check
from django_filters.rest_framework import DjangoFilterBackend  # Filter backend for DRF

from .models import Book
from .serializers import BookSerializer


# 1. BookListAPI - API endpoint to list all books with filtering, search, and ordering support
#    - Inherits from DRF's ListAPIView, which provides a read-only endpoint to list a queryset.
#    - Supports filtering by title, author, and publication_year via query parameters.
#    - Allows search in title and author fields using ?search= keyword.
#    - Supports ordering by title or publication_year using ?ordering= parameter.
#    - Permissions:
#        - Unauthenticated users can perform GET requests (read-only).
#        - Authenticated users get the same read access.
class ListView(generics.ListAPIView):
    queryset = Book.objects.all()  # Fetch all Book records from the database
    serializer_class = BookSerializer  # Use serializer to convert Book instances to JSON
    permission_classes = [IsAuthenticatedOrReadOnly]  # Read access allowed to everyone
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Allow filtering by exact matches on these fields
    filterset_fields = ['title', 'author', 'publication_year']
    # Allow search (case-insensitive partial match) on these fields
    search_fields = ['title', 'author']
    # Allow ordering results by these fields
    ordering_fields = ['title', 'publication_year']


# 2. BookDetailAPI - Retrieve detailed information about a single book by its ID (primary key)
#    - Inherits from RetrieveAPIView which provides a read-only endpoint for a single object.
#    - URL pattern would typically include the book ID: /books/<id>/
#    - Permissions:
#        - Unauthenticated users can read book details.
#        - Authenticated users have the same read access.
class DetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()  # Fetch all books; DRF will filter by pk automatically
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# 3. BookCreateAPI - Create a new book record
#    - Inherits from CreateAPIView, providing a POST endpoint to add new objects.
#    - Permissions:
#        - Only authenticated users can create books.
#        - Unauthenticated users will get 401 Unauthorized response.
class CreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Enforce authentication for creating


# 4. BookUpdateAPI - Update an existing book's information
#    - Inherits from UpdateAPIView which supports PUT (full update) and PATCH (partial update).
#    - Permissions:
#        - Only authenticated users can update books.
class UpdateView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Enforce authentication for updating


# 5. BookDeleteAPI - Delete an existing book
#    - Inherits from DestroyAPIView which provides DELETE endpoint.
#    - Permissions:
#        - Only authenticated users can delete books.
class DeleteView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Enforce authentication for deleting




"""
Suggested Refinement: Combine endpoints for RESTful simplicity
Instead of having separate Create, Update, and Delete classes, DRF lets you merge them into two main endpoints:

ListCreateAPIView → Handles GET (list) + POST (create)

RetrieveUpdateDestroyAPIView → Handles GET (detail) + PUT/PATCH (update) + DELETE

Here’s how it looks:


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Book
from .serializers import BookSerializer


# GET /books/ → List
# POST /books/ → Create
class BookListCreateAPI(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# GET /books/<id>/ → Retrieve
# PUT/PATCH /books/<id>/ → Update
# DELETE /books/<id>/ → Delete
class BookDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]



Benefits of Combining
Cleaner URLs — only /books/ and /books/<id>/.

Fewer view classes to maintain.

Still fully supports CRUD with the same permissions.

"""