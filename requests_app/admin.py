from django.contrib import admin

from .models import MaintenanceRequest


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'assigned_to', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    autocomplete_fields = ('created_by', 'assigned_to')
    readonly_fields = ('created_at', 'updated_at')