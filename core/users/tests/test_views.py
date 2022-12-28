from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.users.models import User


class UserTests(APITestCase):
    
    def test_create_user(self):
        """
        Ensure we can create a new User.
        """
        url = reverse('user-list')

        data = {
            'username': 'TestUserOne',
            'email': 'testuserone@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get(email='testuserone@email.com').username, 'TestUserOne')

        data = {
            'username': 'TestUserTwo',
            'email': 'testusertwo@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(email='testusertwo@email.com').username, 'TestUserTwo')