from rest_framework import routers
from django.urls import include, path

from api.views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet
)

APP_VERSION = 'v1'

app_name = 'api'


def add_version_url(url: str) -> str:
    """Добавляем версию к адресу и возвращаем полученный url."""
    return f'{APP_VERSION}/{url}'


router = routers.DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)

urlpatterns = [
    path(add_version_url(''), include(router.urls))
]
