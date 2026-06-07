from rest_framework import serializers

# Simple serializer pour validation des données entrantes (optionnel)
class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    role = serializers.CharField()