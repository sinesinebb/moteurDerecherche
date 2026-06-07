from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPass123!'
        }
    
    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='AdminPass123!'
        )
        
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_user_str_method(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), f"{user.email} ({user.username})")
    
    def test_user_get_full_name(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), 'Test User')
    
    def test_user_status_choices(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.status, 'actif')
        
        user.status = User.Status.INACTIVE
        user.save()
        self.assertEqual(user.status, 'inactif')


class UserAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='TestPass123!'
        )
        
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='AdminPass123!'
        )
    
    def test_user_registration(self):
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['email'], data['email'])
    
    def test_user_login(self):
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-me')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['username'], self.user.username)
    
    def test_update_user_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-update')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
    
    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('change-password')
        data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que le mot de passe a été changé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))
    
    def test_user_sessions_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-sessions')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class SearchHistoryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='TestPass123!'
        )
        
        # Créer quelques recherches
        from apps.search_history.models import SearchHistory, SearchResult
        self.search1 = SearchHistory.objects.create(
            user=self.user,
            query='python django',
            total_results=150,
            execution_time=0.45
        )
        
        self.search2 = SearchHistory.objects.create(
            user=self.user,
            query='machine learning',
            total_results=200,
            execution_time=0.67
        )
    
    def test_search_history_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('search-history-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search_history_statistics(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('search-analytics')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_searches'], 2)
    
    def test_create_search_history(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('search-history-list')
        data = {
            'query': 'elasticsearch python',
            'total_results': 120,
            'execution_time': 0.35
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['query'], data['query'])


class UserPreferenceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='TestPass123!'
        )
    
    def test_get_user_preferences(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-preferences-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'auto')
        self.assertEqual(response.data['language'], 'fr')
    
    def test_update_user_preferences(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-preferences-detail', args=[self.user.preferences.id])
        data = {
            'theme': 'dark',
            'language': 'en',
            'results_per_page': 20
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'dark')
        self.assertEqual(response.data['language'], 'en')
        self.assertEqual(response.data['results_per_page'], 20)