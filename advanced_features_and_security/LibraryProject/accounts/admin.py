from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.forms import TextInput, Textarea
from django import forms


class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'date_of_birth', 'profile_photo')

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('date_of_birth', 'profile_photo')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('date_of_birth', 'profile_photo')}),
    )

    list_display = ['username', 'email', 'date_of_birth', 'is_staff']
    search_fields = ['username', 'email']


admin.site.register(CustomUser, CustomUserAdmin)
