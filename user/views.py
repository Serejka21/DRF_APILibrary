from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """View to create a new user"""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """View to manage user profile"""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """Get authenticated user object"""
        return self.request.user
