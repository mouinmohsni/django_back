# companies/urls.py
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet

router = DefaultRouter()
# Cette seule ligne va générer toutes les URLs pour nous (/companies/, /companies/{id}/, etc.)
router.register(r'', CompanyViewSet, basename='company')

urlpatterns = router.urls
