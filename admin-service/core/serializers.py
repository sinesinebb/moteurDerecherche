from rest_framework import serializers
from .models import SystemConfiguration, AuditLog, MetricSnapshot

class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfiguration
        fields = ['key', 'value', 'description', 'updated_at']
        read_only_fields = ['updated_at']

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['timestamp']

class MetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricSnapshot
        fields = '__all__'
        read_only_fields = ['timestamp']