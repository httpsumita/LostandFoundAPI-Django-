from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import ItemViewSet
from . import views
# from django.urls import get_resolver

router = DefaultRouter()
router.register('items', views.ItemViewSet, basename='item')
for url in router.urls:
    print(url.name, url.pattern)

urlpatterns = [
    path('api/', views.api_root, name='api-root'),
    path('api/', include(router.urls)),
    
]