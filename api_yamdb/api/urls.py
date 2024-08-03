from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewViewSet


APP_VERSION = 'v1'

app_name = 'api'


def add_version_url(url: str) -> str:
    """Добавляем версию к адресу и возвращаем полученный url."""
    return f'{APP_VERSION}/{url}'


router = DefaultRouter()
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
    path(add_version_url(''), include(router.urls)),
]
