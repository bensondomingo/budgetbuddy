from django.urls import path, include
from rest_framework.routers import DefaultRouter

from budgetplanner.api.views import (
    CategoryTypeViewSet, CategoryViewSet, TransactionAPIViewSet)
from budgetplanner.api.views import CategoryTypeAdminCreateView


router = DefaultRouter()
router.register('categorytypes', CategoryTypeViewSet,
                basename='categorytype')
router.register('categories', CategoryViewSet, basename='category')
router.register('transactions', TransactionAPIViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('create-defaults/', CategoryTypeAdminCreateView.as_view(),
         name='create-defaults'),
]
