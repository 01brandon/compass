from rest_framework import serializers
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'phone', 'profile_picture', 'role']
        read_only_fields = ['id', 'email', 'full_name']
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user
    
class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'profile_picture']
        
class RoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
        
        
