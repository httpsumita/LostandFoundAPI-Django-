from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import ItemViewSet
from . import views

router = DefaultRouter()
router.register('items', views.ItemViewSet, basename='item')

urlpatterns = [
    path('api/', views.api_root, name='api-root'),
    path('api/', include(router.urls)),
    
]