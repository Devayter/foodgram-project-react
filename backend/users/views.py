from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .constants import (
    EMAIL_ALREADY_EXISTS, LOGGED_OUT, NOT_AUTHORIZER, NOT_SUBSCRIBED,
    PASSWORD_CHANGED_MESSAGE, SELF_SUBSCRIPTION_ERROR,
    SUBSCRIPTION_ALREADY_EXISTS, UNSUBSCRIBED, USERNAME_ALREADY_EXIST
)
from .mixins import CreateDestroyListMixin, UserMeViewSetMixin
from .models import Subscribe
from .pagination import UsersPagination
from .serializers import (
   SetPasswordSerializer, BlacklistedTokenSerializer, SignupSerializer,
   SubscribeSerializer, TokenSerializer, UserMeSerializer, UserSerializer
)

User = get_user_model()


class GetSubscribeView(CreateDestroyListMixin):
    pagination_class = UsersPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscribeSerializer

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=self.kwargs.get('user_id'))
        subscriber = request.user

        if user == subscriber:
            return Response(
                SELF_SUBSCRIPTION_ERROR,
                status=status.HTTP_400_BAD_REQUEST
            )

        if not Subscribe.objects.filter(user=user, subscriber=subscriber):
            subscribe = Subscribe.objects.create(
                user=user,
                subscriber=subscriber
                )
            serializer = self.get_serializer(subscribe)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                SUBSCRIPTION_ALREADY_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
                )

    def destroy(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=self.kwargs.get('user_id'))
        subscriber = request.user

        try:
            subscribe = Subscribe.objects.get(user=user, subscriber=subscriber)
            subscribe.delete()
            return Response(UNSUBSCRIBED, status=status.HTTP_204_NO_CONTENT)
        except Subscribe.DoesNotExist:
            return Response(
                NOT_SUBSCRIBED, status=status.HTTP_400_BAD_REQUEST
                )


class LogInView(APIView):
    """Вью для получения токена пользователя"""

    def post(self, request):
        serializer = TokenSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            email = validated_data['email']
            username = User.objects.filter(email=email).first()
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_token = AccessToken.for_user(user)
                return Response(
                    {
                        'auth_token': str(auth_token),
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'message': 'Неправильная электронная почта или пароль'},
                    status=status.HTTP_404_NOT_FOUND
                )

        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class LogOutView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        token = request.auth
        serializer = BlacklistedTokenSerializer(data={"token": str(token)})

        if serializer.is_valid():
            serializer.save()
            return Response(LOGGED_OUT, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                NOT_AUTHORIZER,
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )


class SetPasswordView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
            )

        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = User.objects.get(username=request.user)
            password = validated_data['new_password']
            user.set_password(password)
            user.save()
            return Response(
                PASSWORD_CHANGED_MESSAGE,
                status=status.HTTP_204_NO_CONTENT
                )

        return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class SubscribeViewSet(CreateDestroyListMixin):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return Subscribe.objects.select_related('user').all().filter(
            subscriber=self.request.user
        )


class UserMeAPIView(UserMeViewSetMixin):
    """Вьюсет пользователя для запроса /users/me/"""

    permission_classes = (IsAuthenticated,)
    serializer_class = UserMeSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для регистрации"""

    pagination_class = UsersPagination
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        email = validated_data['email']
        username = validated_data['username']
        password = validated_data['password']

        if User.objects.filter(username=username).exists():
            return Response(
                USERNAME_ALREADY_EXIST,
                status=status.HTTP_400_BAD_REQUEST
                )
        elif User.objects.filter(email=email).exists():
            return Response(
                EMAIL_ALREADY_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
                )
        else:
            hashed_password = make_password(password)
            serializer.save(password=hashed_password)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        user = get_object_or_404(User, pk=pk)
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
