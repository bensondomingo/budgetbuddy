from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions

from profiles.models import Profile

from profiles.api.permissions import IsOwnProfileOrReadOnly
from profiles.api.serializers import ProfileSerializer
from profiles.api.serializers import ProfileAvatarSerializer
from profiles.api.serializers import UserSerializer


USER_MODEL = get_user_model()

class UserListAPIView(generics.ListAPIView):

    queryset = USER_MODEL.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserRUDAPIView(generics.RetrieveUpdateDestroyAPIView):

    queryset = USER_MODEL.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'username'


class ProfileListAPIView(generics.ListAPIView):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProfileRUDAPIView(generics.RetrieveUpdateAPIView):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnProfileOrReadOnly]
    lookup_field = 'user__username'
