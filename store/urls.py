from django.urls import path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register('categories', views.CategoryViewSet, basename='category')
router.register('landing-mobiles', views.MobileViewSet, basename='mobile-list')

product_router = routers.NestedDefaultRouter(router, 'landing-mobiles', lookup='mobile')
product_router.register('comments', views.CommentsViewSet, basename='comments')


urlpatterns = [
    path('landing-mobile-brands/<slug:slug>/', views.MobilesByBrand.as_view(), name='mobiles-by-brand')
]


urlpatterns += router.urls + product_router.urls