from django.urls import path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register('categories', views.CategoryViewSet, basename='category')
router.register('category-mobile', views.MobileViewSet, basename='mobile')
router.register('category-laptop', views.LaptopViewSet, basename='laptop')
router.register('category-headphone', views.HeadPhoneViewSet, basename='headphone')
router.register('carts', views.CartViewSet, basename='carts')
router.register('orders', views.OrderViewSet, basename='orders')

mobile_router = routers.NestedDefaultRouter(router, 'category-mobile', lookup='mobile')
mobile_router.register('comments', views.CommentsViewSet, basename='mobile-comments')

laptop_router = routers.NestedDefaultRouter(router, 'category-laptop', lookup='laptop')
laptop_router.register('comments', views.CommentsViewSet, basename='laptop-comments')

laptop_router = routers.NestedDefaultRouter(router, 'category-headphone', lookup='headphone')
laptop_router.register('comments', views.CommentsViewSet, basename='headphone-comments')

cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_items_router.register('items', views.CartItemViewset, basename='cart-items')

urlpatterns = [
    path('mobile-brand-<str:slug>/', views.MobileByBrandViewSet.as_view(), name='mobile-by-brand'),
    path('laptop-brand-<str:slug>/', views.LaptopByBrandViewSet.as_view(), name='laptop-by-brand'),
    path('headphone-brand-<str:slug>/', views.HeadPhoneByBrandViewSet.as_view(), name='headphone-by-brand'),
    path('search/', views.GlobalSearchView.as_view(), name='search'),
]


urlpatterns += router.urls + mobile_router.urls + laptop_router.urls + cart_items_router.urls