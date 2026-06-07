from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Avg, F
from django.utils import timezone
from datetime import timedelta
import json

from .models import SearchHistory, SearchResult, UserPreference
from .serializers import (
    SearchHistorySerializer, SearchResultSerializer,
    UserPreferenceSerializer, SearchHistoryCreateSerializer
)
from .permissions import IsOwner


class SearchHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = SearchHistory.objects.filter(user=user)
        
        # Filtres optionnels
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        query = self.request.query_params.get('query')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        if query:
            queryset = queryset.filter(query__icontains=query)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur veut sauvegarder l'historique
        try:
            preferences = UserPreference.objects.get(user=request.user)
            if not preferences.save_search_history:
                return Response(
                    {"message": "Sauvegarde de l'historique désactivée"},
                    status=status.HTTP_200_OK
                )
        except UserPreference.DoesNotExist:
            pass
        
        serializer = SearchHistoryCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        search_history = serializer.save()
        
        # Sauvegarder les résultats si fournis
        results_data = request.data.get('results', [])
        if results_data:
            for result_data in results_data:
                SearchResult.objects.create(
                    search_history=search_history,
                    **result_data
                )
        
        return Response(
            SearchHistorySerializer(search_history).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques sur les recherches"""
        user = request.user
        
        # Statistiques globales
        total_searches = SearchHistory.objects.filter(user=user).count()
        total_clicks = SearchResult.objects.filter(
            search_history__user=user, clicked=True
        ).count()
        
        # Recherches récentes (7 derniers jours)
        week_ago = timezone.now() - timedelta(days=7)
        recent_searches = SearchHistory.objects.filter(
            user=user, created_at__gte=week_ago
        ).count()
        
        # Requêtes les plus fréquentes
        popular_queries = SearchHistory.objects.filter(user=user)\
            .values('query')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:10]
        
        # Documents les plus cliqués
        popular_documents = SearchResult.objects.filter(
            search_history__user=user, clicked=True
        ).values('title')\
         .annotate(clicks=Count('id'))\
         .order_by('-clicks')[:10]
        
        return Response({
            'total_searches': total_searches,
            'total_clicks': total_clicks,
            'recent_searches': recent_searches,
            'popular_queries': list(popular_queries),
            'popular_documents': list(popular_documents),
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Exporter l'historique en JSON"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response = Response(serializer.data)
        response['Content-Disposition'] = 'attachment; filename="search_history.json"'
        response['Content-Type'] = 'application/json'
        
        return response
    
    @action(detail=True, methods=['post'])
    def mark_clicked(self, request, pk=None):
        """Marquer un résultat comme cliqué"""
        search_history = self.get_object()
        document_id = request.data.get('document_id')
        
        if not document_id:
            return Response(
                {"error": "document_id requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = SearchResult.objects.get(
                search_history=search_history,
                document_id=document_id
            )
            result.clicked = True
            result.click_count = F('click_count') + 1
            result.save()
            
            return Response({"message": "Résultat marqué comme cliqué"})
        except SearchResult.DoesNotExist:
            return Response(
                {"error": "Résultat non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )


class UserPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        return UserPreference.objects.get(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        # Une seule préférence par utilisateur
        return Response(
            {"error": "Les préférences existent déjà. Utilisez PUT pour les modifier."},
            status=status.HTTP_400_BAD_REQUEST
        )