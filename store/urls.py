from django.urls import path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register('categories', views.CategoryViewSet, basename='category')
router.register('category-mobile', views.MobileViewSet, basename='mobile')
router.register('carts', views.CartViewSet, basename='carts')
router.register('orders', views.OrderViewSet, basename='orders')

mobile_router = routers.NestedDefaultRouter(router, 'category-mobile', lookup='mobile')
mobile_router.register('comments', views.CommentsViewSet, basename='comments')

cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_items_router.register('items', views.CartItemViewset, basename='cart-items')

urlpatterns = [
    path('mobile-brand-<str:category__slug>/', views.MobileByBrandViewSet.as_view(), name='mobile-by-brand')
]


urlpatterns += router.urls + mobile_router.urls + cart_items_router.urls