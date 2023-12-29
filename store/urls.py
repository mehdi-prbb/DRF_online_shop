from django.urls import path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register('categories', views.CategoryViewSet, basename='category')
router.register('landing-mobiles-list', views.MobileViewSet, basename='mobile-list')


urlpatterns = [
    path('landing-mobile-brands/<slug:slug>/', views.MobilesByBrand.as_view(), name='mobiles-by-brand'),
    path('landing-mobile-details/<slug:slug>/', views.MobileDetails.as_view(), name='mobiles-detail')
]


urlpatterns += router.urls 