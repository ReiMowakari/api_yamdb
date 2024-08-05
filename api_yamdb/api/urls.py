from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import (
    AdminUserViewSet,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
)

from .views import (
    CommentViewSet,
    ReviewViewSet,
    UserAPIView,
    ObtainTokenApiView
)


APP_VERSION = 'v1'

app_name = 'api'


def add_version_url(url: str) -> str:
    """Добавляем версию к адресу и возвращаем полученный url."""
    return f'{APP_VERSION}/{url}'


router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='user')
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)

urlpatterns = [
    path('v1/auth/signup/', UserAPIView.as_view(), name='signup'),
    path('v1/auth/token/', ObtainTokenApiView.as_view(), name='token_obtain'),
    path('v1/', include(router.urls)),
    path(add_version_url(''), include(router.urls)),
]
