from django.contrib import admin
from .models import *

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_authorized', 'user_account_id', 'created_at', 'updated_at',)
    list_filter = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'is_authorized','state_id', 'scope', 'user_account_id','user_profile',)}),
        ('Token', {'fields': ('access_token', 'refresh_token', 'expires_at',)}),
        ('Date information', {'fields': ('created_at', 'updated_at',)}),
    )
    readonly_fields = ('user', 'is_authorized','state_id', 'access_token', 'refresh_token', 'expires_at', 'scope', 'user_account_id', 'user_profile', 'created_at', 'updated_at',)
    search_fields = ('user', 'is_authorized')
    ordering = ('user', '-created_at',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserProfile, UserProfileAdmin)

class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'last_sync_time', 'created_at', 'updated_at',)
    list_filter = ('user_profile',)
    fieldsets = (
        (None, {'fields': ('user_profile', 'devices', 'last_sync_time',)}),
        ('Date information', {'fields': ('created_at', 'updated_at',)}),
    )
    readonly_fields = ('user_profile', 'devices', 'last_sync_time', 'created_at', 'updated_at',)
    search_fields = ('user_profile',)
    ordering = ('user_profile', '-created_at',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserDevice, UserDeviceAdmin)

class UserStepTimeSeriesAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'date_time', 'steps', 'last_sync_time',)
    list_filter = ('user_profile', 'date_time',)
    fieldsets = (
        (None, {'fields': ('user_profile', 'date_time', 'steps',)}),
        ('Date information', {'fields': ('last_sync_time',)}),
    )
    readonly_fields = ('user_profile', 'date_time', 'steps', 'last_sync_time',)
    search_fields = ('user_profile', 'date_time',)
    ordering = ('user_profile', 'date_time',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserStepTimeSeries, UserStepTimeSeriesAdmin)

class UserHeartRateTimeSeriesAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'date_time', 'resting_heartrate', 'last_sync_time',)
    list_filter = ('user_profile', 'date_time',)
    fieldsets = (
        (None, {'fields': ('user_profile', 'date_time', 'heartrate_zones', 'resting_heartrate',)}),
        ('Date information', {'fields': ('last_sync_time',)}),
    )
    readonly_fields = ('user_profile', 'date_time', 'heartrate_zones', 'resting_heartrate', 'last_sync_time',)
    search_fields = ('user_profile', 'date_time',)
    ordering = ('user_profile', 'date_time',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserHeartRateTimeSeries, UserHeartRateTimeSeriesAdmin)

class UserSleepTimeSeriesAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'date_time', 'duration', 'efficiency', 'last_sync_time', 'start_time', 'end_time', 'minutes_after_wakeup', 'minutes_asleep', 'minutes_awake', 'minutes_to_fall_asleep', 'time_in_bed', 'last_sync_time',)
    list_filter = ('user_profile',)
    fieldsets = (
        (None, {'fields': ('user_profile',)}),
        ('Sleep details', {'fields': ('duration', 'efficiency', 'minutes_after_wakeup', 'minutes_asleep', 'minutes_awake', 'minutes_to_fall_asleep', 'time_in_bed', 'levels', 'summary',)}),
        ('Date information', {'fields': ('date_time', 'start_time', 'end_time', 'last_sync_time',)}),
    )
    readonly_fields = ('user_profile', 'date_time', 'duration', 'efficiency', 'last_sync_time', 'start_time', 'end_time', 'minutes_after_wakeup', 'minutes_asleep', 'minutes_awake', 'minutes_to_fall_asleep', 'time_in_bed', 'levels', 'summary', 'last_sync_time',)
    search_fields = ('user_profile', 'date_time')
    ordering = ('user_profile', 'date_time',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserSleepTimeSeries, UserSleepTimeSeriesAdmin)

class UserStepIntradayDataAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'time_series', 'dataset', 'dataset_interval', 'dataset_type', 'last_sync_time',)
    list_filter = ('user_profile',)
    fieldsets = (
        (None, {'fields': ('user_profile', 'dataset', 'dataset_interval', 'dataset_type',)}),
        ('Date information', {'fields': ('time_series', 'last_sync_time',)}),
    )
    readonly_fields = ('user_profile', 'time_series', 'dataset', 'dataset_interval', 'dataset_type', 'last_sync_time',)
    search_fields = ('user_profile',)
    ordering = ('user_profile', 'time_series',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserStepIntradayData, UserStepIntradayDataAdmin)

class UserHeartRateIntradayDataAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'time_series', 'dataset', 'dataset_interval', 'dataset_type', 'last_sync_time',)
    list_filter = ('user_profile',)
    fieldsets = (
        (None, {'fields': ('user_profile', 'dataset', 'dataset_interval', 'dataset_type',)}),
        ('Date information', {'fields': ('time_series', 'last_sync_time',)}),
    )
    readonly_fields = ('user_profile', 'time_series', 'dataset', 'dataset_interval', 'dataset_type', 'last_sync_time',)
    search_fields = ('user_profile',)
    ordering = ('user_profile', 'time_series',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserHeartRateIntradayData, UserHeartRateIntradayDataAdmin)

class UserSyncStatusAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'date_time', 'step_time_series', 'heartrate_time_series', 'sleep_time_series', 'step_intraday_data', 'heartrate_intraday_data',)
    list_filter = ('user_profile',)
    fieldsets = (
        (None, {'fields': ('user_profile', 'date_time',)}),
        ('Time Series', {'fields': ('step_time_series', 'heartrate_time_series', 'sleep_time_series', 'step_intraday_data', 'heartrate_intraday_data',)}),
    )
    readonly_fields = ('user_profile', 'date_time', 'step_time_series', 'heartrate_time_series', 'sleep_time_series', 'step_intraday_data', 'heartrate_intraday_data',)
    search_fields = ('user_profile', 'date_time',)
    ordering = ('user_profile', 'date_time',)

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(UserSyncStatus, UserSyncStatusAdmin)