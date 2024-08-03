from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import (
    PageNumberPagination, LimitOffsetPagination
)
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter

from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    CustomUser,
)
from .filters import TitleFilterSet
from .mixins import CreateDestroyListNSIMixin
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    SelfUserRegistrationSerializer,
    AdminUserSerializer,
    ObtainTokenSerializer,
    GetOrPatchUserSerializer,
    TitleReadSerializer,
    TitleViewSerializer,
    CommentSerializer,
    ReviewSerializer,
)
from .permissions import OnlyAdminAllowed, AccountOwnerOrManager
from .utils import generate_and_send_code, generate_user_token


class UserAPIView(APIView):
    """
    Апи для самостоятельной регистрации нового пользователя.

    Доступен для любого пользователя, токен не требуется.
    """

    permission_classes = (AllowAny,)
    serializer_class = SelfUserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        if CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.get(username=username)
            generate_and_send_code(user)
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )

        user = serializer.save()
        generate_and_send_code(user)
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Апи для пользователей с ролью 'админ'.

    Включает дополнительный action 'request_me'
    для всех аутентифицрованных пользователей.
    """

    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (OnlyAdminAllowed,)
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(method=request.method)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.serializer_class(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user.role == settings.ADMIN_ROLE:
            user.is_staff = True
        else:
            user.is_staff = False
        user.save()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user.role == settings.ADMIN_ROLE:
            user.is_staff = True
            user.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @action(detail=False,
            url_path='me',
            methods=['get', 'patch'],
            permission_classes=(AccountOwnerOrManager,),
            serializer_class=GetOrPatchUserSerializer)
    def request_me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ObtainTokenApiView(APIView):
    """
    Вьюсет для получения токена и дальнейшей работы с API.

    Доступен для любого пользователя, токен не требуется.
    """

    permission_classes = (AllowAny,)
    serializer_class = ObtainTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = CustomUser.objects.get(username=username)
        token = generate_user_token(user)
        return Response(
            {'token': token}, status=status.HTTP_200_OK
        )


class CategoryViewSet(
    CreateDestroyListNSIMixin,
    viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(
    CreateDestroyListNSIMixin,
    viewsets.GenericViewSet
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(
    viewsets.ModelViewSet
):
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilterSet
    pagination_class = LimitOffsetPagination
    # TODO: perimission_classes = (..., )
    queryset = Title.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitleReadSerializer
        return TitleViewSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    # permission_classes = ()

    def get_review(self):
        """Получение объекта отзыва."""
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review

    def get_queryset(self):
        return self.get_review().comments

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    # permission_classes = ()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title=title_id)

    def perform_create(self, serializer):
        user = self.request.user
        score = self.request.data.get('score')
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(title=title, author=user, score=score)
