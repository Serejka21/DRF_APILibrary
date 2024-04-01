from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


TOKEN_URL = reverse("user:token_obtain_pair")
TOKEN_REFRESH_URL = reverse("user:token_refresh")
TOKEN_VERIFY_URL = reverse("user:token_verify")


class TokenApiTest(TestCase):
    """Tests for token API"""
    def setUp(self):
        """Set up tests"""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_token_endpoint(self):
        """Test token endpoint"""
        payload = {
            "email": "test@test.com",
            "password": "test_password"
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_refresh_endpoint(self):
        """Test token refresh endpoint"""
        payload = {
            "email": "test@test.com",
            "password": "test_password"
        }

        res_token = self.client.post(TOKEN_URL, payload)
        res_refresh = self.client.post(TOKEN_REFRESH_URL, {"refresh": res_token.data["refresh"]})

        self.assertEqual(res_refresh.status_code, status.HTTP_200_OK)

    def test_token_verify_endpoint(self):
        """Test token verify endpoint"""
        payload = {
            "email": "test@test.com",
            "password": "test_password"
        }

        res_token = self.client.post(TOKEN_URL, payload)
        res_refresh = self.client.post(TOKEN_VERIFY_URL, {"token": res_token.data["access"]})

        self.assertEqual(res_refresh.status_code, status.HTTP_200_OK)
