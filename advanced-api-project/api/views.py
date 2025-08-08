from rest_framework import generics
from .models import Book
from .serializers import BookSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# 1. BookListAPI - Retrieve all books
# - Inherits from ListAPIView (read-only endpoint for listing objects)
# - GET /books/ will return a JSON list of all Book objects.
# - Uses IsAuthenticatedOrReadOnly permission:
#     → Unauthenticated users can read data (GET requests allowed).
#     → Only authenticated users can make write requests (POST, PUT, DELETE not allowed here).
class ListView(generics.ListAPIView):
    queryset = Book.objects.all()  # Fetch all books from the database
    serializer_class = BookSerializer  # Use the BookSerializer for JSON conversion
    permission_classes = [IsAuthenticatedOrReadOnly]  # Read allowed for everyone, write only if logged in
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'author', 'publication_year']
    search_fields = ['title', 'author']
    ordering_fields = ['title', 'publication_year']


# 2. BookDetailAPI - Retrieve a single book by ID
# - Inherits from RetrieveAPIView (read-only endpoint for a single object).
# - GET /books/<id>/ will return details of a specific book.
# - Same IsAuthenticatedOrReadOnly permission logic as the list view.
class DetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()  # Fetch all books (DRF will filter by pk automatically)
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# 3. BookCreateAPI - Add a new book
# - Inherits from CreateAPIView (endpoint for creating objects).
# - POST /books/ will create a new Book object.
# - Uses IsAuthenticated permission:
#     → Only logged-in users can add a new book.
class CreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can create


# 4. BookUpdateAPI - Modify an existing book
# - Inherits from UpdateAPIView (endpoint for updating objects).
# - PUT /books/<id>/ will completely update a book.
# - PATCH /books/<id>/ will partially update a book.
# - Uses IsAuthenticated permission:
#     → Only logged-in users can update books.
class UpdateView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can update


# 5. BookDeleteAPI - Remove a book
# - Inherits from DestroyAPIView (endpoint for deleting objects).
# - DELETE /books/<id>/ will remove a specific book from the database.
# - Uses IsAuthenticated permission:
#     → Only logged-in users can delete books.
class DeleteView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can delete





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