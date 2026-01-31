# bookings/urls.py
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
# On enregistre notre ViewSet. Il ne permettra que les actions list, create, et destroy.
router.register(r'', BookingViewSet, basename='booking')

urlpatterns = router.urls
