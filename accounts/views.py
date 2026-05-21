from django.shortcuts import render
from rest_framework import viewsets, status, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import User
from accounts.serializers import UserSerializer, RegisterSerializer, UpdateProfileSerializer, RoleUpdateSerializer

from accounts.permissions import IsSuperAdmin, IsAdmin, IsEditor, IsJournalist, IsReader
from drf_spectacular.utils import (
    extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample,
    inline_serializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['Users'],
        summary='List all users',
        description='Retrieve a paginated list of all users. Requires authentication.',
    ),
    retrieve=extend_schema(
        tags=['Users'],
        summary='Retrieve a user',
        description='Get the details of a specific user by their ID.',
    ),
    create=extend_schema(
        tags=['Users'],
        summary='Create a new user',
        description='Create a new user account directly. For public self-registration use the `/register` endpoint. Requires authentication.',
        request=RegisterSerializer,
        responses={201: UserSerializer},
    ),
    update=extend_schema(
        tags=['Users'],
        summary='Update a user',
        description='Fully update an existing user. Requires authentication and appropriate permissions.',
    ),
    partial_update=extend_schema(
        tags=['Users'],
        summary='Partially update a user',
        description='Partially update an existing user. Requires authentication and appropriate permissions.',
    ),
    destroy=extend_schema(
        tags=['Users'],
        summary='Delete a user',
        description='Permanently delete a user account. Requires superadmin or admin permissions.',
    ),
    register=extend_schema(
        tags=['Authentication'],
        summary='Register a new user',
        description='Create a new user account. No authentication required.',
        request=RegisterSerializer,
        responses={201: UserSerializer},
    ),
    login=extend_schema(
        tags=['Authentication'],
        summary='Login',
        description='Authenticate with email and password to receive JWT access and refresh tokens.',
        request=inline_serializer(
            name='UserLoginRequest',
            fields={
                'email': drf_serializers.EmailField(help_text='Registered email address'),
                'password': drf_serializers.CharField(
                    help_text='Account password',
                    style={'input_type': 'password'},
                ),
            },
        ),
        responses={
            200: inline_serializer(
                name='UserLoginResponse',
                fields={
                    'refresh': drf_serializers.CharField(help_text='JWT refresh token'),
                    'access': drf_serializers.CharField(help_text='JWT access token'),
                    'user': UserSerializer(),
                },
            ),
            401: inline_serializer(
                name='LoginUnauthorizedResponse',
                fields={'detail': drf_serializers.CharField()},
            ),
            403: inline_serializer(
                name='LoginForbiddenResponse',
                fields={'detail': drf_serializers.CharField()},
            ),
        },
    ),
    update_profile=extend_schema(
        tags=['Users'],
        summary='Update profile',
        description='Update the profile fields of a specific user. Users can update their own profile; admins and superadmins can update any profile.',
        request=UpdateProfileSerializer,
        responses={200: UserSerializer},
    ),
    update_role=extend_schema(
        tags=['Users'],
        summary='Change user role',
        description='Assign a new role to a user (reader, journalist, editor, admin, superadmin). Only superadmins can perform this action.',
        request=RoleUpdateSerializer,
        responses={200: UserSerializer},
    ),
    me=extend_schema(
        tags=['Users'],
        summary='Get current user',
        description='Retrieve the profile of the currently authenticated user.',
        responses={200: UserSerializer},
    ),
    search=extend_schema(
        tags=['Users'],
        summary='Search users',
        description='Search for users by email, first name, or last name using the `q` query parameter.',
        parameters=[
            OpenApiParameter(
                name='q',
                description='Search query — matched against email, first name, and last name.',
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: UserSerializer(many=True)},
    ),
    deactivate=extend_schema(
        tags=['Users'],
        summary='Deactivate a user',
        description='Deactivate a user account, preventing them from logging in. Requires admin or superadmin permissions.',
        responses={
            200: inline_serializer(
                name='DeactivateUserResponse',
                fields={'detail': drf_serializers.CharField()},
            ),
        },
    ),
    activate=extend_schema(
        tags=['Users'],
        summary='Activate a user',
        description='Re-activate a previously deactivated user account. Requires admin or superadmin permissions.',
        responses={
            200: inline_serializer(
                name='ActivateUserResponse',
                fields={'detail': drf_serializers.CharField()},
            ),
        },
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'register', 'login']:
            permission_classes = [AllowAny]
        elif self.action in ['update_role']:
            permission_classes = [IsSuperAdmin]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAdmin | IsEditor | IsJournalist | IsReader]
        else:
            permission_classes = [IsSuperAdmin | IsAdmin | IsEditor | IsJournalist | IsReader]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='login', permission_classes=[AllowAny])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'detail': 'User account is deactivated.'}, status=status.HTTP_403_FORBIDDEN)

        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'], url_path='update-profile', permission_classes=[IsAdmin | IsEditor | IsJournalist | IsReader])
    def update_profile(self, request, pk=None):
        user = self.get_object()
        if request.user != user and not request.user.role in ['admin', 'superadmin']:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'], url_path='change-role', permission_classes=[IsSuperAdmin])
    def update_role(self, request, pk=None):
        user = self.get_object()
        serializer = RoleUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        query = request.query_params.get('q', '')
        if query:
            users = User.objects.filter(email__icontains=query) | User.objects.filter(first_name__icontains=query) | User.objects.filter(last_name__icontains=query)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        return Response({'detail': 'Please provide a search query.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='deactivate', permission_classes=[IsAdmin | IsSuperAdmin])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if request.user != user and not request.user.role in ['admin', 'superadmin']:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        user.is_active = False
        user.save()
        return Response({'detail': 'User deactivated successfully.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='activate', permission_classes=[IsAdmin | IsSuperAdmin])
    def activate(self, request, pk=None):
        user = self.get_object()
        if request.user != user and not request.user.role in ['admin', 'superadmin']:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        user.is_active = True
        user.save()
        return Response({'detail': 'User activated successfully.'}, status=status.HTTP_200_OK)