"""
URL mappings for the medicheck app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from medicheck import views

router = DefaultRouter()
router.register('diseases', views.DiseaseViewSet)
router.register('tags', views.TagViewSet)

app_name = 'medicheck'

urlpatterns = [
    path('', include(router.urls)),
]