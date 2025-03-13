from django.contrib import admin
from rest_framework import routers
from account import views as account_views
from quran import views as quran_views
from django.urls import path, include
from knox import views as knox_views

router = routers.DefaultRouter()
router.register(r'users', account_views.UserViewSet)
router.register(r'groups', account_views.GroupViewSet)
router.register(r'mushafs', quran_views.MushafViewSet)
router.register(r'auth', account_views.AuthViewSet, basename='auth')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('auth/login/', account_views.LoginView.as_view(), name='knox_login'),
    path('auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('auth/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
]
