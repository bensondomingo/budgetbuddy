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

from budgetplanner.api.serializers import (
    CategorySerializer, CategoryTypeSerializer, TransactionSerializer)
from budgetplanner.api.permissions import (
    IsAuthenticatedOrReadOnly, IsObjectOwnerOrReadOnly)
from budgetplanner.models import Category, CategoryType, Transaction

from utils.funcs import filter_list_of_dict


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

    def retrieve(self, request, *args, **kwargs):
        '''
        Adds an option to include list of related objects on the serialized 
        data. Checks "rl" query params to determine action.
        rl:
            true: include
            false/not present: don't include
        '''

        include_related_list = request.GET.get('rl', False)
        if not include_related_list:
            return super().retrieve(request, *args, **kwargs)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            objects = instance.categories.all()
            data_list = CategorySerializer(objects, many=True).data
            fields = ['id', 'name', 'amount_planned']
            categories = filter_list_of_dict(data_list, fields)
            data = serializer.data
            data.update({'categories': categories})
            return Response(data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):

    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsObjectOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category_type__name']
    ordering_fields = ['name', 'amount_planned']

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        '''
        Adds an option to include list of related objects on the serialized 
        data. Checks "rl" query params to determine action.
        rl:
            true: include
            false/not present: don't include
        '''
        include_related_list = request.GET.get('rl', False)
        if not include_related_list:
            return super().retrieve(request, *args, **kwargs)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            objects = instance.transactions.all()
            data_list = TransactionSerializer(objects, many=True).data
            fields = ['id', 'date', 'amount', 'description']
            transactions = filter_list_of_dict(data_list, fields)

            data = serializer.data
            data.update({'transactions': transactions})
            return Response(data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionAPIViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin):

    serializer_class = TransactionSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsObjectOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['date', 'description']
    ordering_fields = ['date', 'amount', 'category__name']

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CategoryTypeAdminCreateView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, **kwargs):
        # Generate default category types
        admin = USER_MODEL.objects.get(username=ADMIN_USERNAME)

        cat_types = [CategoryType.objects.create(name=typ, user=admin)
                     for typ in ['income', 'savings', 'expenditure']]

        data = [CategoryTypeSerializer(
            cat_type).data for cat_type in cat_types]
        return Response(data, status=status.HTTP_201_CREATED)
