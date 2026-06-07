import re
import requests
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class UserListProxy(APIView):
    permission_classes = [IsAuthenticated]

    def _forward(self, method, request, url, data=None):
        auth = request.headers.get('Authorization')
        if not auth:
            return Response({'error': 'Token manquant'}, status=401)

        headers = {'Authorization': auth}
        try:
            resp = requests.request(method, url, json=data, headers=headers, timeout=5)
            if resp.status_code == 204:
                return Response(status=204)
            try:
                return Response(resp.json(), status=resp.status_code)
            except:
                return Response({'error': 'Invalid response'}, status=502)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Proxy {method} failed")
            return Response({'error': str(e)}, status=503)

    def get(self, request):
        url = f"{settings.USER_SERVICE_URL}/api/users/"
        return self._forward('get', request, url)

    def post(self, request):
        url = f"{settings.USER_SERVICE_URL}/api/users/"
        return self._forward('post', request, url, data=request.data)

class UserDetailProxy(APIView):
    permission_classes = [IsAuthenticated]

    def _forward(self, method, request, url, data=None):
        auth = request.headers.get('Authorization')
        if not auth:
            return Response({'error': 'Token manquant'}, status=401)

        headers = {'Authorization': auth}
        try:
            resp = requests.request(method, url, json=data, headers=headers, timeout=5)
            if resp.status_code == 204:
                return Response(status=204)
            try:
                return Response(resp.json(), status=resp.status_code)
            except:
                return Response({'error': 'Invalid response'}, status=502)
        except requests.exceptions.RequestException as e:
            logger.exception(f"Proxy {method} failed")
            return Response({'error': str(e)}, status=503)

    def get(self, request, pk):
        url = f"{settings.USER_SERVICE_URL}/api/users/{pk}/"
        return self._forward('get', request, url)

    def put(self, request, pk):
        url = f"{settings.USER_SERVICE_URL}/api/users/{pk}/"
        return self._forward('put', request, url, data=request.data)

    def delete(self, request, pk):
        url = f"{settings.USER_SERVICE_URL}/api/users/{pk}/"
        return self._forward('delete', request, url)