from django.contrib import admin
from rest_framework import routers
from account import views as account_views
from quran import views as quran_views
from core import views as core_views
from django.urls import path, include
from knox import views as knox_views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register(r'users', account_views.UserViewSet)
router.register(r'groups', account_views.GroupViewSet)
router.register(r'mushafs', quran_views.MushafViewSet)
router.register(r'surahs', quran_views.SurahViewSet)
router.register(r'ayahs', quran_views.AyahViewSet)
router.register(r'words', quran_views.WordViewSet)
router.register(r'translations', quran_views.TranslationViewSet)
router.register(r'ayah-translations', quran_views.AyahTranslationViewSet)
router.register(r'auth', account_views.AuthViewSet, basename='auth')
router.register(r'profile', account_views.ProfileViewSet, basename="profile")
router.register(r'phrases', core_views.PhraseViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('auth/login/', account_views.LoginView.as_view(), name='knox_login'),
    path('auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('auth/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
]
