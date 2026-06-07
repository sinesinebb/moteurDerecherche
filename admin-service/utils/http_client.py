import requests
from django.conf import settings

class InternalAPIClient:
    """Client HTTP simplifié pour appels internes entre services."""
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # Ajouter un header d'authentification interne si nécessaire
        self.session.headers.update({'X-Internal-Token': settings.INTERNAL_API_TOKEN})

    def get(self, path, params=None):
        url = f"{self.base_url}{path}"
        return self.session.get(url, params=params, timeout=5)

    def post(self, path, json=None):
        url = f"{self.base_url}{path}"
        return self.session.post(url, json=json, timeout=5)

    def put(self, path, json=None):
        url = f"{self.base_url}{path}"
        return self.session.put(url, json=json, timeout=5)

    def delete(self, path):
        url = f"{self.base_url}{path}"
        return self.session.delete(url, timeout=5)