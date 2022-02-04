from django.contrib import admin
from .models import *
from .utils import generate_key

# Register your models here.
class KeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'is_available','created_at',)
    list_filter = ('user','is_available',)
    fieldsets = (
        (None, {'fields': ('key', 'user', 'notes', 'is_available',)}),
        ('Date information', {'fields': ('created_at',)}),
        ('Permissions', {'fields': ('allow_step_time_series', 'allow_heartrate_time_series', 'allow_sleep_time_series', 'allow_step_intraday_data', 'allow_heartrate_intraday_data', )}),
    )
    readonly_fields = ('key', 'user', 'notes', 'is_available','created_at', 'allow_step_time_series', 'allow_heartrate_time_series', 'allow_sleep_time_series', 'allow_step_intraday_data', 'allow_heartrate_intraday_data',)
    search_fields = ('user','is_available',)
    ordering = ('-created_at',)

    def save_form(self, request, form, change):
        form_entry = super(KeyAdmin, self).save_form(request, form, change)
        if not change:
            form_entry.key = generate_key()
        return form_entry

admin.site.register(Key, KeyAdmin)

class AuthorizationKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'authorization_key', 'created_at',)
    fieldsets = (
        (None, {'fields': ('key', 'authorization_key', )}),
        ('Date information', {'fields': ('created_at',)}),
    )
    readonly_fields = ('key', 'authorization_key', 'created_at',)
    search_fields = ('key',)
    ordering = ('key', '-created_at',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(AuthorizationKey, AuthorizationKeyAdmin)