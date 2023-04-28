from django.urls import path, include
from rest_framework.routers import DefaultRouter
from applications.review.views import ReviewModelViewSet

router = DefaultRouter()
router.register('', ReviewModelViewSet)

urlpatterns = [
    path('', include(router.urls))
]
