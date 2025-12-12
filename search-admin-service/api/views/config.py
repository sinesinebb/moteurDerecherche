from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from app.models.config import RankingConfig, ContentModeration, CrawlConfig

class RankingConfigView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        configs = RankingConfig.objects.filter(is_active=True).values(
            'name', 'config_type', 'value', 'description'
        )
        return Response({'configs': list(configs)})
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        name = request.data.get('name')
        value = request.data.get('value')
        
        try:
            config = RankingConfig.objects.get(name=name)
            old_value = config.value
            config.value = value
            config.modified_by = request.user.username
            config.save()
            
            return Response({
                'status': 'success',
                'message': f'Config {name} modifiée: {old_value} → {value}'
            })
        except RankingConfig.DoesNotExist:
            return Response(
                {'error': 'Configuration non trouvée'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class ContentModerationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        moderations = ContentModeration.objects.filter(is_active=True).values(
            'moderation_type', 'target', 'reason', 'created_at'
        )
        return Response({'moderations': list(moderations)})
    
    def post(self, request):
        moderation_type = request.data.get('type')
        target = request.data.get('target')
        reason = request.data.get('reason')
        
        moderation, created = ContentModeration.objects.get_or_create(
            moderation_type=moderation_type,
            target=target,
            defaults={
                'reason': reason,
                'created_by': request.user.username
            }
        )
        
        if not created:
            moderation.is_active = True
            moderation.reason = reason
            moderation.save()
        
        return Response({'status': 'success', 'action': 'added' if created else 'updated'})