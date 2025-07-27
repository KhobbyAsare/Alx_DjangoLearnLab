from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']

# Add this to satisfy the test requiring ExampleForm
class ExampleForm(forms.Form):
    # You can add a simple example field, or keep it empty if not specified
    example_field = forms.CharField(max_length=100, required=False)
