from django.conf import settings
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter

from reviews.models import CustomUser
from api.serializers import (
    SelfUserRegistrationSerializer,
    AdminUserSerializer,
    ObtainTokenSerializer,
    GetOrPatchUserSerializer
)
from api.permissions import OnlyAdminAllowed, AccountOwnerOrManager

from api.utils import generate_and_send_code, generate_user_token


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
            seralizer = self.serializer_class(user)
            return Response(seralizer.data, status=status.HTTP_200_OK)

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
