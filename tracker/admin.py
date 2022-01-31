from django.contrib import admin
from .models import *

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'state_id', 'access_token', 'refresh_token', 'expires_at', 'scope', 'user_account_id', 'user_profile', 'created_at', 'updated_at',)
    list_filter = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'state_id', 'scope', 'user_account_id','user_profile',)}),
        ('Token', {'fields': ('access_token', 'refresh_token', 'expires_at',)}),
        ('Date information', {'fields': ('created_at', 'updated_at',)}),
    )
    readonly_fields = ('user', 'state_id', 'access_token', 'refresh_token', 'expires_at', 'scope', 'user_account_id', 'user_profile', 'created_at', 'updated_at',)
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

class UserStepTimeSeriesAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_time', 'steps', 'last_sync_time',)
    list_filter = ('user', 'date_time',)
    fieldsets = (
        (None, {'fields': ('user', 'date_time', 'steps',)}),
        ('Date information', {'fields': ('last_sync_time',)}),
    )
    readonly_fields = ('user', 'date_time', 'steps', 'last_sync_time',)
    search_fields = ('user', 'date_time',)
    ordering = ('user', 'date_time',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserStepTimeSeries, UserStepTimeSeriesAdmin)

class UserHeartRateTimeSeriesAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_time', 'resting_heart_rate', 'heart_rate_zones', 'last_sync_time',)
    list_filter = ('user', 'date_time',)
    fieldsets = (
        (None, {'fields': ('user', 'date_time', 'heart_rate_zones', 'resting_heart_rate',)}),
        ('Date information', {'fields': ('last_sync_time',)}),
    )
    readonly_fields = ('user', 'date_time', 'heart_rate_zones', 'resting_heart_rate', 'last_sync_time',)
    search_fields = ('user', 'date_time',)
    ordering = ('user', 'date_time',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserHeartRateTimeSeries, UserHeartRateTimeSeriesAdmin)

class UserSleepTimeSeriesAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_time', 'duration', 'efficiency', 'last_sync_time', 'start_time', 'end_time', 'minutes_after_wakeup', 'minutes_asleep', 'minutes_awake', 'minutes_to_fall_asleep', 'time_in_bed', 'levels', 'summary', 'last_sync_time',)
    list_filter = ('user',)
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Sleep details', {'fields': ('duration', 'efficiency', 'minutes_after_wakeup', 'minutes_asleep', 'minutes_awake', 'minutes_to_fall_asleep', 'time_in_bed', 'levels', 'summary',)}),
        ('Date information', {'fields': ('date_time', 'start_time', 'end_time', 'last_sync_time',)}),
    )
    readonly_fields = ('user', 'date_time', 'duration', 'efficiency', 'last_sync_time', 'start_time', 'end_time', 'minutes_after_wakeup', 'minutes_asleep', 'minutes_awake', 'minutes_to_fall_asleep', 'time_in_bed', 'levels', 'summary', 'last_sync_time',)
    search_fields = ('user', 'date_time')
    ordering = ('user', 'date_time',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserSleepTimeSeries, UserSleepTimeSeriesAdmin)

class UserStepIntradayDataAdmin(admin.ModelAdmin):
    list_display = ('time_series', 'dataset', 'dataset_interval', 'dataset_type', 'last_sync_time',)
    list_filter = ('time_series',)
    fieldsets = (
        (None, {'fields': ('dataset', 'dataset_interval', 'dataset_type',)}),
        ('Date information', {'fields': ('time_series', 'last_sync_time',)}),
    )
    readonly_fields = ('time_series', 'dataset', 'dataset_interval', 'dataset_type', 'last_sync_time',)
    search_fields = ('time_series',)
    ordering = ('time_series',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserStepIntradayData, UserStepIntradayDataAdmin)

class UserHeartRateIntradayDataAdmin(admin.ModelAdmin):
    list_display = ('time_series', 'dataset', 'dataset_interval', 'dataset_type', 'last_sync_time',)
    list_filter = ('time_series',)
    fieldsets = (
        (None, {'fields': ('dataset', 'dataset_interval', 'dataset_type',)}),
        ('Date information', {'fields': ('time_series', 'last_sync_time',)}),
    )
    readonly_fields = ('time_series', 'dataset', 'dataset_interval', 'dataset_type', 'last_sync_time',)
    search_fields = ('time_series',)
    ordering = ('time_series',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserHeartRateIntradayData, UserHeartRateIntradayDataAdmin)