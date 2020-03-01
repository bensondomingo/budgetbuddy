from django.urls import path, include
from rest_framework.routers import DefaultRouter

from budgetplanner.api.views import CategoryTypeViewSet, CategoryViewSet
from budgetplanner.api.views import CategoryTypeAdminCreateView


router = DefaultRouter()
router.register('category-types', CategoryTypeViewSet,
                basename='category-type')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('create-defaults/', CategoryTypeAdminCreateView.as_view(),
         name='create-defaults'),
]
