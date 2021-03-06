from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings

from rest_framework import generics
from rest_framework import permissions
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters

from budgetplanner.api.serializers import CategorySerializer
from budgetplanner.api.serializers import CategoryTypeSerializer
from budgetplanner.api.serializers import TransactionSerializer
from budgetplanner.api.permissions import IsAuthenticatedOrReadOnly
from budgetplanner.api.permissions import IsObjectOwnerOrReadOnly
from budgetplanner.api.permissions import IsCategoryOwnerOrReadOnly
from budgetplanner.models import Category, CategoryType, Transaction


USER_MODEL = get_user_model()
ADMIN_USERNAME = settings.ADMIN_USERNAME


class CategoryTypeViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin):

    serializer_class = CategoryTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsObjectOwnerOrReadOnly]

    def get_queryset(self):
        return CategoryType.objects.filter(Q(user__username=ADMIN_USERNAME) |
                                           Q(user=self.request.user))

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):

    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsObjectOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'cat_type__name']
    ordering_fields = ['name', 'amount_planned']

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class CategoryTypeAdminCreateView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, **kwargs):
        # Generate default category types
        admin = USER_MODEL.objects.get(username=ADMIN_USERNAME)

        cat_types = [CategoryType.objects.create(name=typ, user=admin)
                     for typ in ['income', 'savings', 'expenditure']]

        data = [CategoryTypeSerializer(cat_type).data for cat_type in cat_types]
        return Response(data, status=status.HTTP_201_CREATED)
