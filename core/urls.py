from django.urls import path, include

urlpatterns = [
    # path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt'))
]

