from django.contrib import admin
from .models import Key
from .utils import generate_key

# Register your models here.
class KeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created_at', 'notes', )
    list_filter = ('user',)
    fieldsets = (
        (None, {'fields': ('key', 'user', 'notes', )}),
        ('Date information', {'fields': ('created_at',)}),
    )
    readonly_fields = ('key', 'created_at',)
    search_fields = ('key', 'user',)
    ordering = ('-created_at',)

    def save_form(self, request, form, change):
        form_entry = super(KeyAdmin, self).save_form(request, form, change)
        if not change:
            form_entry.key = generate_key()
        return form_entry

admin.site.register(Key, KeyAdmin)