from django.test import TestCase

# Create your tests here.



# core/serializers.py
class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['preferred_language', 'safe_search', 'results_per_page']