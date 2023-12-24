from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register('categories', views.CategoryViewSet, basename='categories')
router.register('landing-mobile_brands', views.MobileCategoryViewSet, basename='mobile-category')
router.register('landing-mobile_phone', views.MobileViewSet, basename='mobile-list')


urlpatterns = router.urls 