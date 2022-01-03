from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from .models import User, Log

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name','is_superuser', 'is_active')

    def clean_password_confirm(self):
        # Check that the two password entries match
        password = self.cleaned_data.get("password1")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords don't match")
        return password_confirm

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name','is_superuser', 'is_active')

    def clean_password(self):
        return self.initial["password"]

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'username', 'first_name', 'last_name','is_superuser', 'is_active', 'created_at', 'updated_at',)
    list_filter = ('last_name','is_superuser', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username','email', 'password','is_superuser', 'is_active', 'created_at', 'updated_at',)}),
        ('Personal info', {'fields': ('first_name', 'last_name',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email', 'password', 'password_confirm', 'first_name', 'last_name','is_superuser', 'is_active',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at',)
    search_fields = ('username', 'email', 'first_name', 'last_name','is_superuser', 'is_active')
    ordering = ('last_name','first_name',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)

class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action','level','created_at', )
    list_filter = ('action',)
    fieldsets = (
        (None, {'fields': ('user', 'action', 'level', 'created_at',)}),
    )
    readonly_fields = ('user', 'action', 'level', 'created_at', )
    search_fields = ('user', 'action','level',)
    ordering = ('-created_at',)
    filter_horizontal = ()

admin.site.register(Log, LogAdmin)