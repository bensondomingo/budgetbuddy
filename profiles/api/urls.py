from django.urls import path

from profiles.api.views import UserListAPIView, UserRUDAPIView
from profiles.api.views import ProfileListAPIView, ProfileRUDAPIView

urlpatterns = [
    path('users/', UserListAPIView.as_view(), name='users-list'),
    path('users/<str:username>/', UserRUDAPIView.as_view(), name='user-detail'),
    path('profiles/', ProfileListAPIView.as_view(), name='profiles-list'),
    path('profiles/<str:user__username>/',
         ProfileRUDAPIView.as_view(), name='profiles-detail'),
]
