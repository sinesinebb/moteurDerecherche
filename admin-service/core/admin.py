from django.contrib import admin
from .models import SystemConfiguration, AuditLog, MetricSnapshot

@admin.register(SystemConfiguration)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'updated_at')
    search_fields = ('key',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user_id', 'timestamp')
    list_filter = ('action',)
    readonly_fields = ('timestamp',)

@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'timestamp')
    list_filter = ('name',)