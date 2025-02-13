from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet
from . import views

router = DefaultRouter()
router.register('items', ItemViewSet, basename='item')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.api_root, name='api-root'),
]