from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .constants import (
    EMAIL_ALREADY_EXIST, LOGGED_OUT, NOT_AUTHORIZER, USERNAME_ALREADY_EXIST
)
from .mixins import UserMeViewSetMixin
from .serializers import (
   BlacklistedTokenSerializer, SignupSerializer, TokenSerializer, UserMeSerializer, 
   UserSerializer
)

User = get_user_model()


class LogInView(APIView):
    """Вью для получениятокена пользователя"""
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            username = validated_data['username']
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                access_token = AccessToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)
                return Response(
                    {
                        'access_token': str(access_token),
                        'refresh_token': str(refresh_token),
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'message': 'Неправильное имя пользователя или пароль'},
                    status=status.HTTP_404_NOT_FOUND
                )

        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class LogOutView(APIView):
    def post(self, request):
        print("<<<<<<<<", request)
        token = request.auth
        print(">>>>>>>", token)
        serializer = BlacklistedTokenSerializer(data={"token": str(token)})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        # print('>>>>>>', request.data)
        # request.auth = None
        # refresh_token = RefreshToken(request.data.get("refresh_token"))
        # refresh_token.blacklist()
          # Устанавливаем значение auth в None
        return Response({'detail': 'User has been logged out.'}, status=status.HTTP_200_OK)
        # access_token = request.auth
        # token = OutstandingToken.objects.filter(token=access_token)
        # token.blacklist()
        # return Response({'detail': 'User has been logged out.'}, status=status.HTTP_200_OK)
        

        # token = request.auth
        # if token:
        #     token.delete()
        #     return Response(LOGGED_OUT, status=status.HTTP_200_OK)
        # else:
        #     return Response(NOT_AUTHORIZER, status=status.HTTP_400_BAD_REQUEST)


class UserMeAPIView(UserMeViewSetMixin):
    """Вьюсет пользователя для запроса /users/me/"""

    serializer_class = UserMeSerializer
    # permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        username = validated_data['username']
        name = validated_data['name']
        last_name = validated_data['last_name']
        email = validated_data['email']
        password = validated_data['password']
        if User.objects.filter(username=username).exists():
            return Response(
                USERNAME_ALREADY_EXIST, status=status.HTTP_400_BAD_REQUEST
                )
        elif User.objects.filter(email=email).exists():
            return Response(
                EMAIL_ALREADY_EXIST, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            user = User.objects.create(
                username=username,
                name=name,
                last_name=last_name,
                email=email,
                password=password)
            user.set_password(password)
            user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

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
