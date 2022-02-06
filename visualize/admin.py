from django.contrib import admin
from .models import *
from .utils import generate_key

# Register your models here.
class KeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created_at',)
    list_filter = ('user',)
    fieldsets = (
        (None, {'fields': ('key', 'user', 'notes', )}),
        ('Date information', {'fields': ('created_at',)}),
        ('Permissions', {'fields': ('allow_step_time_series', 'allow_heartrate_time_series', 'allow_sleep_time_series', 'allow_step_intraday_data', 'allow_heartrate_intraday_data', )}),
    )
    readonly_fields = ('key', 'user', 'notes', 'created_at', 'allow_step_time_series', 'allow_heartrate_time_series', 'allow_sleep_time_series', 'allow_step_intraday_data', 'allow_heartrate_intraday_data',)
    search_fields = ('user',)
    ordering = ('-created_at',)

    def save_form(self, request, form, change):
        form_entry = super(KeyAdmin, self).save_form(request, form, change)
        if not change:
            form_entry.key = generate_key()
        return form_entry

admin.site.register(Key, KeyAdmin)
