from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


REGISTER_URL = reverse("user:create")


class RegisterApiTest(TestCase):
    """Tests for Unauthenticated client"""
    def setUp(self):
        """Set up tests"""
        self.client = APIClient()

    def test_user_register_with_correct_data(self):
        """Test user registration with correct data"""
        payload = {
            "email": "test@test.com",
            "password": "test12345"
        }

        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_register_with_incorrect_data(self):
        """Test user registration with incorrect data"""
        payload = {
            "username": "test",
            "password": "test12345"
        }

        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
