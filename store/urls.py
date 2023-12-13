from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register('categories', views.CategoryViewSet, basename='categories')
router.register('mobile', views.MobileViewSet, basename='mobile')


category_router = routers.NestedDefaultRouter(router, 'categories', lookup='category')
category_router.register('brand', views.MobileCategoryViewSet, basename='mobile-category')

mobile_cat_router = routers.NestedDefaultRouter(category_router, 'brand', lookup='brand')
mobile_cat_router.register('model', views.MobileViewSet, basename='brand-model')



urlpatterns = router.urls + category_router.urls + mobile_cat_router.urls
