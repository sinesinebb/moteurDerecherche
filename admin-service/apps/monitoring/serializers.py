from rest_framework import serializers
from core.models import MetricSnapshot

class MetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricSnapshot
        fields = '__all__'