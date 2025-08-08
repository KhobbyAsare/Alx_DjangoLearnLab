from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'publication_year', 'author']  # match exactly your model fields
        widgets = {
            'publication_year': forms.DateInput(attrs={'type': 'date'}),
        }
