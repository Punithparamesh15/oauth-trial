from django.urls import path, include
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from oauth2_provider.views import TokenView
from oauth2_provider.urls import urlpatterns as oauth2_urls

urlpatterns = [
    path('', home, name='home'),
    path('api/users/', UserAPIView.as_view(), name='user-list'), 
    path('api/users/<int:user_id>/', UserAPIView.as_view(), name='user-detail'),
    path('api/admins/', AdminAPIView.as_view(), name='admin-list'),
    path('api/admins/<uuid:admin_id>/', AdminAPIView.as_view(), name='admin-detail'),

    path('api/auth/token/', OAuthTokenView.as_view(), name='oauth-token'),
    path('api/user/details/', UserDetailsAPIView.as_view(), name='user-details'),
]