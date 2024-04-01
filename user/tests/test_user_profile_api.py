from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


ME_URL = reverse("user:manage")


class UnauthenticatedMeApiTest(TestCase):
    """Tests for Unauthenticated client"""
    def setUp(self):
        """Set up tests"""
        self.client = APIClient()

    def test_anon_client(self):
        """Test anonymous client access to profile"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedMeApiTest(TestCase):
    """Tests for Authenticated client"""
    def setUp(self):
        """Set up tests"""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_get_me_page(self):
        """Test user profile page"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_update(self):
        """Test user update info with incorrect data"""
        payload = {
            "username": "test",
            "password": "test12345"
        }

        res = self.client.put(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
