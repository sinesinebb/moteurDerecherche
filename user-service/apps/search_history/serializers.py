# from django.utils import timezone
from rest_framework import serializers
from .models import SearchHistory, SearchResult, UserPreference


class SearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchResult
        fields = [
            'id', 'document_id', 'title', 'url', 'snippet',
            'relevance_score', 'pagerank_score', 'final_score',
            'position', 'clicked', 'click_count'
        ]
        read_only_fields = fields


class SearchHistorySerializer(serializers.ModelSerializer):
    results = SearchResultSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = SearchHistory
        fields = [
            'id', 'user', 'query', 'created_at', 'results'
        ]
        read_only_fields = fields
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Heure local
        representation['created_at'] = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return representation
        # local_time = timezone.localtime(instance.created_at)
        # representation['created_at'] = local_time.strftime('%Y-%m-%d %H:%M:%S')


class SearchHistoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['query']   

    def create(self, validated_data):
        user = self.context['request'].user
        return SearchHistory.objects.create(user=user, **validated_data)


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            'theme', 'language', 'results_per_page',
            'enable_notifications', 'save_search_history',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_results_per_page(self, value):
        if value < 5 or value > 100:
            raise serializers.ValidationError(
                "Le nombre de résultats par page doit être entre 5 et 100"
            )
        return value


class SearchAnalyticsSerializer(serializers.Serializer):
    period = serializers.CharField(max_length=20)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin"
            )
        return data


class ExportSearchHistorySerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=['json', 'csv'])
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    include_results = serializers.BooleanField(default=False)