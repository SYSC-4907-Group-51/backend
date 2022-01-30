from django.contrib import admin
from .models import *

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'state_id', 'access_token', 'refresh_token', 'expires_at', 'user_profile', 'created_at', 'updated_at',)
    list_filter = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'state_id', 'user_profile',)}),
        ('Token', {'fields': ('access_token', 'refresh_token', 'expires_at',)}),
        ('Date information', {'fields': ('created_at', 'updated_at',)}),
    )
    readonly_fields = ('user', 'state_id', 'access_token', 'refresh_token', 'expires_at', 'user_profile', 'created_at', 'updated_at',)
    search_fields = ('user',)
    ordering = ('user', '-created_at',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserProfile, UserProfileAdmin)

class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'devices', 'last_sync_time', 'created_at', 'updated_at',)
    list_filter = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'devices', 'last_sync_time',)}),
        ('Date information', {'fields': ('created_at', 'updated_at',)}),
    )
    readonly_fields = ('user', 'devices', 'last_sync_time', 'created_at', 'updated_at',)
    search_fields = ('user',)
    ordering = ('user', '-created_at',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserDevice, UserDeviceAdmin)