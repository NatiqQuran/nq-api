from django.contrib import admin
from rest_framework import routers
from account import views as account_views
from quran import views as quran_views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'users', account_views.UserViewSet)
router.register(r'groups', account_views.GroupViewSet)
router.register(r'mushafs', quran_views.MushafViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls'))
]
