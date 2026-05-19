from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import User
from accounts.serializers import UserSerializer, RegisterSerializer, UpdateProfileSerializer, RoleUpdateSerializer  

from accounts.permissions import IsSuperAdmin, IsAdmin, IsEditor, IsJournalist, IsReader


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
    
    @action(detail=True, methods=['put'], url_path='update-role', permission_classes=[IsSuperAdmin])
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