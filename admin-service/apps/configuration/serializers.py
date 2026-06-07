from rest_framework import serializers
from core.models import SystemConfiguration

class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfiguration
        fields = ['key', 'value', 'description', 'updated_at']
        read_only_fields = ['updated_at']