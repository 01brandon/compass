from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import User
from accounts.serializers import RegisterSerializer, UserSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Prevent issuing tokens for inactive users
        if not getattr(self.user, 'is_active', True):
            raise AuthenticationFailed('User account is deactivated.')
        data["user"] = UserSerializer(self.user).data
        return data

@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Login',
        description='Authenticate a user and obtain JWT tokens.',
    )
)
class LoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Register',
        description='Register a new user account. No authentication required.',
        request=RegisterSerializer,
        responses={201: UserSerializer},
    )
)
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)