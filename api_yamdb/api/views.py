from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action

from reviews.models import CustomUser
from api.serializers import (
    SelfUserRegistrationSerializer,
    AdminUserSerializer,
    ObtainTokenSerializer,
)

from api.utils import generate_and_send_code, generate_user_token


class UserAPIView(APIView):
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
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'username'
    pagination_class = PageNumberPagination

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(method=request.method)
        return super().update(request, *args, **kwargs)

    @action(detail=False, 
            url_path='me',
            methods=['get', 'patch'])
    def request_me(self, request):
        user = request.user
        if request.method == 'GET':
            seralizer = self.serializer_class(user)
            return Response(seralizer.data, status=status.HTTP_200_OK)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('role', None)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ObtainTokenApiView(APIView):
    """Вьюсет для получения токена и дальнейшей работы с API."""

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
