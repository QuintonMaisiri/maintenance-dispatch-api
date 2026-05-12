from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email','first_name', 'last_name', 'role']
        read_only_fields = fields

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
    
    def create(self, validated_data):
        self.password = validated_data.pop('password')
         # Force role to RESIDENT - only admin can create managers/staff
        user = User(role = User.Role.RESIDENT, **validated_data)
        user.set_password(self.password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)