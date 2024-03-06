from django.urls import path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register('categories', views.CategoryViewSet, basename='category')
router.register('landing-mobiles', views.MobileViewSet, basename='mobile-list')
router.register('carts', views.CartViewSet, basename='carts')
router.register('orders', views.OrderViewSet, basename='orders')

product_router = routers.NestedDefaultRouter(router, 'landing-mobiles', lookup='mobile')
product_router.register('comments', views.CommentsViewSet, basename='comments')

cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_items_router.register('items', views.CartItemViewset, basename='cart-items')


urlpatterns = [
    path('landing-mobile-brands/<slug:slug>/', views.MobilesByBrand.as_view(), name='mobiles-by-brand')
]


urlpatterns += router.urls + product_router.urls + cart_items_router.urls