import json
import logging
import asyncio
import jwt
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

logger = logging.getLogger(__name__)

class UserEventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Récupérer le token
        query_string = self.scope.get('query_string', b'').decode()
        token = None
        if 'token=' in query_string:
            token = query_string.split('token=')[-1].split('&')[0]

        if not token:
            await self.close(code=4001)
            return

        # Valider le token JWT
        try:
            payload = jwt.decode(
                token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']],
                SIGNING_KEY = settings.SIMPLE_JWT['SIGNING_KEY'],
                ALGORITHM = settings.SIMPLE_JWT['ALGORITHM']
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            await self.close(code=4001)
            return

        # Vérifier que l'utilisateur est admin
        if not payload.get('is_superuser'):
            await self.close(code=4003)
            return

        self.scope['user'] = payload
        self.room_group_name = "admin_users"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info("✅ WebSocket connecté (admin)")

        # Démarrer les tâches d'arrière-plan
        self.keepalive_task = asyncio.create_task(self.send_keepalive())
        self.redis_task = asyncio.create_task(self.listen_redis())

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        for task_name in ('keepalive_task', 'redis_task'):
            task = getattr(self, task_name, None)
            if task:
                task.cancel()
        logger.info("WebSocket déconnecté")

    async def send_keepalive(self):
        while True:
            await asyncio.sleep(30)
            try:
                await self.send(text_data=json.dumps({"type": "ping"}))
            except Exception:
                break

    async def listen_redis(self):
        try:
            r = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            pubsub = r.pubsub()
            await pubsub.subscribe("user_events")
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {'type': 'user_event', 'event': data}
                    )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Erreur Redis: {e}")

    async def user_event(self, event):
        await self.send(text_data=json.dumps(event['event']))