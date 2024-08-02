from django.urls import path, include
from rest_framework.routers import DefaultRouter


from api.views import AdminUserViewSet, UserAPIView, ObtainTokenApiView


router = DefaultRouter()

router.register(r'users', AdminUserViewSet, basename='user')

urlpatterns = [
    path('v1/auth/signup/', UserAPIView.as_view(), name='signup'),
    path('v1/auth/token/', ObtainTokenApiView.as_view(), name='token_obtain'),
    path('v1/', include(router.urls)),
]
